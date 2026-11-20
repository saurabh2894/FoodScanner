"""WS2 FDC ingest (scripts/fdc_ingest.py): offline tests with synthetic zips; no network."""
from __future__ import annotations

import io
import json
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest

from scripts import fdc_ingest as fi

FOOD_CSV = ("fdc_id,data_type,description,food_category_id,publication_date\n"
            "100,foundation_food,\"Spices, bay leaf\",2,2026-10-29\n"
            "101,sample_food,\"SALT, BRANDX, IODIZED\",2,2019-04-01\n"
            "102,sub_sample_food,Salt; iodized,2,2019-04-01\n"
            "103,foundation_food,Almonds,12,2026-10-29\n")
CAT_CSV = "id,code,description\n2,0200,Spices and Herbs\n12,1200,Nut and Seed Products\n"


def make_zip(path: Path, with_food: bool = True) -> Path:
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("FoodData_Central_foundation_food_csv_2026-10-29/food_category.csv", CAT_CSV)
        if with_food:
            z.writestr("FoodData_Central_foundation_food_csv_2026-10-29/food.csv", FOOD_CSV)
    return path


def zip_bytes(with_food=True) -> bytes:
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("d/food_category.csv", CAT_CSV)
        if with_food:
            z.writestr("d/food.csv", FOOD_CSV)
    return b.getvalue()


def test_normalise_keeps_only_real_foods_with_full_provenance(tmp_path):
    z = make_zip(tmp_path / "FoodData_Central_foundation_food_csv_2026-10-29.zip")
    rows = fi.normalise_zip(z, "foundation", "https://fdc.nal.usda.gov/fdc-datasets/x.zip")
    assert [r["fdc_id"] for r in rows] == ["100", "103"]                       # lab samples (brand names) are not used
    r = rows[0]
    assert r["candidate_id"] == "fdc_foundation:100" and r["description"] == "Spices, bay leaf" and r["food_category"] == "Spices and Herbs"
    assert json.loads(r["parts"]) == ["spices", "bay leaf"] and r["description_norm"] == "spices, bay leaf"
    assert r["dataset_release"] == "2026-10-29" and r["licence"] == "CC0 1.0 Universal" and r["source_url"].startswith("https://fdc.nal.usda.gov/")
    assert all(r[c] not in (None, "") for r in rows for c in ("candidate_id", "dataset", "data_type", "fdc_id", "description", "food_category", "publication_date", "dataset_release", "source_url", "licence"))


def test_write_is_deterministic_and_refuses_to_overwrite(tmp_path):
    z = make_zip(tmp_path / "FoodData_Central_foundation_food_csv_2026-10-29.zip")
    rows = fi.normalise_zip(z, "foundation")
    out = tmp_path / "c.csv"
    fi.write_candidates(rows, out, force=False)
    first = out.read_text()
    with pytest.raises(FileExistsError):
        fi.write_candidates(rows, out, force=False)
    fi.write_candidates(rows, out, force=True)
    assert out.read_text() == first and first.splitlines()[0].split(",") == fi.CANDIDATE_COLUMNS


@pytest.mark.parametrize("name, why", [("ifct_2017", "hook only"), ("open_food_facts", "reference only"), ("branded", "disabled"), ("survey", "disabled")])
def test_disabled_hook_and_reference_sources_are_refused(name, why):
    with pytest.raises(fi.Refused, match=why):
        fi.require_enabled(name)
    with pytest.raises(fi.Refused):
        fi.normalise_zip(Path("/nonexistent.zip"), name)


def test_unknown_source_is_refused_and_registry_licences_are_explicit():
    with pytest.raises(fi.Refused):
        fi.require_enabled("nope")
    assert fi.SOURCES["ifct_2017"]["enabled"] is False and fi.SOURCES["open_food_facts"]["reference_only"] is True
    assert "CC0" in fi.FDC_LICENCE and "FoodData Central" in fi.FDC_CITATION


@pytest.mark.parametrize("url, ok", [("https://fdc.nal.usda.gov/fdc-datasets/a.zip", True), ("http://fdc.nal.usda.gov/x", False), ("https://example.com/a.zip", False),
                                       ("https://fdc.nal.usda.gov.evil.com/a.zip", False), ("ftp://fdc.nal.usda.gov/a", False)])
def test_only_https_fdc_urls_may_be_fetched(url, ok):
    if ok:
        assert fi.check_fdc_url(url) == url
    else:
        with pytest.raises(fi.Refused):
            fi.check_fdc_url(url)


def test_discover_zip_picks_the_latest_listed_release():
    html = ('<a href="/fdc-datasets/FoodData_Central_foundation_food_csv_2025-12-18.zip">a</a><a href="/fdc-datasets/FoodData_Central_foundation_food_csv_2026-10-29.zip">b</a>'
            '<a href="/fdc-datasets/FoodData_Central_foundation_food_json_2026-10-29.zip">j</a>')
    assert fi.discover_zip(html, "FoodData_Central_foundation_food_csv").endswith("foundation_food_csv_2026-10-29.zip")
    with pytest.raises(fi.Refused):
        fi.discover_zip(html, "FoodData_Central_sr_legacy_food_csv")


def test_zip_content_check_and_retry_until_a_complete_dataset():
    good, bad = zip_bytes(True), zip_bytes(False)
    assert fi.zip_intact(good) and not fi.zip_intact(bad) and not fi.zip_intact(b"not a zip")
    calls = []

    def opener(url):
        calls.append(url)
        return (bad if len(calls) < 3 else good), {"etag": f"e{len(calls)}"}
    data, meta = fi.get_valid_zip("https://fdc.nal.usda.gov/fdc-datasets/x.zip", opener)
    assert data == good and meta["etag"] == "e3" and len(calls) == 3
    with pytest.raises(OSError, match="no complete dataset zip"):
        fi.get_valid_zip("https://fdc.nal.usda.gov/fdc-datasets/x.zip", lambda u: (bad, {}), attempts=3)


def test_download_records_provenance_and_saves_only_complete_zips(tmp_path):
    page = b'<a href="/fdc-datasets/FoodData_Central_foundation_food_csv_2026-10-29.zip">z</a>'
    good = zip_bytes(True)

    def opener(url):
        return page if url == fi.DOWNLOAD_PAGE else (good, {"etag": '"abc"', "last_modified": "Thu, 19 Nov 2026 14:27:08 GMT"})
    recs = fi.download(["foundation"], tmp_path, force=False, opener=opener)
    m = json.loads((tmp_path / "downloads.json").read_text())["foundation"]
    assert recs[0]["sha256"] == m["sha256"] and m["bytes"] == len(good) and m["http"]["etag"] == '"abc"' and "CC0" in m["licence"]
    assert (tmp_path / m["file"]).read_bytes() == good
    with pytest.raises(fi.Refused):
        fi.download(["ifct_2017"], tmp_path, force=False, opener=opener)


def test_cli_exit_codes_and_normalise_needs_a_recorded_download(tmp_path, capsys):
    assert fi.main(["normalise", "--sources", "ifct_2017", "--cache", str(tmp_path), "--out", str(tmp_path / "c.csv")]) == 2
    assert fi.main(["normalise", "--cache", str(tmp_path), "--out", str(tmp_path / "c.csv")]) == 2          # no downloads.json yet
    z = make_zip(tmp_path / "FoodData_Central_foundation_food_csv_2026-10-29.zip")
    (tmp_path / "downloads.json").write_text(json.dumps({"foundation": {"file": z.name, "url": "https://fdc.nal.usda.gov/fdc-datasets/" + z.name}}))
    out = tmp_path / "c.csv"
    assert fi.main(["normalise", "--sources", "foundation", "--cache", str(tmp_path), "--out", str(out)]) == 0
    assert fi.main(["normalise", "--sources", "foundation", "--cache", str(tmp_path), "--out", str(out)]) == 2          # exists: refused
    assert fi.main(["normalise", "--sources", "foundation", "--cache", str(tmp_path), "--out", str(out), "--force"]) == 0
