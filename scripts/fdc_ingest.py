"""WS2 supply ingest: USDA FoodData Central (FDC) bulk downloader and normaliser. Candidate NAMES with per-row provenance, nothing else.

FDC data are public domain, published under CC0 1.0 Universal; FDC asks users to list it as the source (see data/ingest/SOURCES.md, which keeps that listing).
Commodity datasets only supply names and food categories. They never decide a NOVA group, a kind or a lexicon row: that is the clause-tier mapping (WS3) and the
validation gate (WS4), and nothing here writes to src/foodscan/resources/.

Commands
  download   fetch the enabled dataset zips from https://fdc.nal.usda.gov/ into --cache, recording URL, UTC time, size and SHA-256 in downloads.json
  normalise  read the zips (no extraction to disk) and write candidates.csv: one row per food with its provenance and the description split into parts
Source registry: only sources marked enabled can be used. IFCT 2017 is a documented hook (licence unverified, NOT used); Open Food Facts is reference-only (nothing is
incorporated: ODbL share-alike fit unresolved); the FDC branded dataset is registered but disabled (brand products, not commodity names).

Exit codes: 0 ok; 1 error; 2 refused (output exists without --force, disabled source, or a non-FDC URL).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FDC_HOST = "fdc.nal.usda.gov"
DOWNLOAD_PAGE = f"https://{FDC_HOST}/download-datasets/"      # the slash matters: the slash-less URL redirects to plain http
FDC_LICENCE = "CC0 1.0 Universal (USDA FoodData Central data are in the public domain and not copyrighted; listing FoodData Central as the source is requested)"
FDC_CITATION = ("U.S. Department of Agriculture, Agricultural Research Service, Beltsville Human Nutrition Research Center. FoodData Central. [Internet]. "
                "Available from https://fdc.nal.usda.gov/.")

# Source registry. `enabled` is enforced by the commands below.
SOURCES: dict[str, dict] = {
    "foundation": {"enabled": True, "family": "FoodData_Central_foundation_food_csv", "data_types": ("foundation_food",),
                   "note": "Foundation Foods. Only data_type foundation_food is a food; sample_food, sub_sample_food, market_acquisition and agricultural_acquisition are lab samples "
                           "(many carry brand names) and are not used."},
    "sr_legacy": {"enabled": True, "family": "FoodData_Central_sr_legacy_food_csv", "data_types": ("sr_legacy_food",),
                  "note": "SR Legacy (final release April 2018): the generic commodity names and the 'Spices and Herbs' category."},
    "survey": {"enabled": False, "family": "FoodData_Central_survey_food_csv", "data_types": ("survey_fndds_food",),
               "note": "FNDDS survey foods: prepared dishes, not commodity names. Registered, disabled."},
    "branded": {"enabled": False, "family": "FoodData_Central_branded_food_csv", "data_types": ("branded_food",),
                "note": "Branded products (very large, brand-specific). Registered, disabled."},
    "ifct_2017": {"enabled": False, "hook": True, "note": "Indian Food Composition Tables 2017: licence unverified, NOT used. Hook only: see data/ingest/SOURCES.md for the interface a future "
                                                         "adapter must meet (same candidates.csv columns, per-row provenance, licence recorded) before this entry may be enabled."},
    "open_food_facts": {"enabled": False, "reference_only": True, "note": "Reference only. Nothing is incorporated (ODbL share-alike fit unresolved)."},
}

CANDIDATE_COLUMNS = ["candidate_id", "dataset", "data_type", "fdc_id", "description", "description_norm", "parts", "food_category_id", "food_category", "publication_date",
                     "dataset_release", "source_url", "licence"]


class Refused(Exception):
    pass


def require_enabled(name: str) -> dict:
    if name not in SOURCES:
        raise Refused(f"unknown source '{name}'; registered: {', '.join(SOURCES)}")
    s = SOURCES[name]
    if not s.get("enabled"):
        why = "hook only" if s.get("hook") else ("reference only" if s.get("reference_only") else "disabled")
        raise Refused(f"source '{name}' is not enabled ({why}): {s['note']}")
    return s


def check_fdc_url(url: str) -> str:
    p = urllib.parse.urlparse(url)
    if p.scheme != "https" or p.hostname != FDC_HOST:
        raise Refused(f"only https://{FDC_HOST}/ URLs may be fetched, got {url}")
    return url


# ---------------------------------------------------------------- discovery and download
def discover_zip(html: str, family: str) -> str:
    """Latest zip of a dataset family listed on the FDC download page (by the date in the file name)."""
    links = re.findall(r'href=["\'](/fdc-datasets/' + re.escape(family) + r'_(\d{4}-\d{2}(?:-\d{2})?)\.zip)["\']', html)
    if not links:
        raise Refused(f"no '{family}' zip is listed on the download page")
    path = max(links, key=lambda x: x[1])[0]
    return f"https://{FDC_HOST}{path}"


class _GuardedRedirect(urllib.request.HTTPRedirectHandler):
    """A redirect must stay on https://fdc.nal.usda.gov/ (the proxy tunnels HTTPS only, and nothing else may be fetched)."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_fdc_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url: str, timeout: int = 300, attempts: int = 4):
    """GET with the host guard and an integrity check: the body must match Content-Length (a transfer the proxy cuts short must not be saved as a file).
    Returns (bytes, {"etag", "last_modified"})."""
    check_fdc_url(url)
    last = "no attempt"
    for _ in range(attempts):
        req = urllib.request.Request(url)
        try:
            with urllib.request.build_opener(_GuardedRedirect).open(req, timeout=timeout) as r:      # noqa: S310 (host checked above and on every redirect)
                expected = int(r.headers.get("Content-Length") or -1)
                meta = {"etag": r.headers.get("ETag"), "last_modified": r.headers.get("Last-Modified")}
                chunks, got = [], 0
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    chunks.append(b)
                    got += len(b)
        except Refused:
            raise
        except Exception as e:   # noqa: BLE001
            last = f"{type(e).__name__}: {e}"
            continue
        if expected >= 0 and got != expected:
            last = f"short read: {got} of {expected} bytes"
            continue
        return b"".join(chunks), meta
    raise OSError(f"could not fetch {url} intact after {attempts} attempts ({last})")


REQUIRED_TABLES = ("food.csv", "food_category.csv")


def zip_intact(data: bytes) -> bool:
    """A usable FDC dataset zip: it passes the zip integrity test and holds the tables the normaliser reads."""
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        names = [n.rsplit("/", 1)[-1] for n in z.namelist()]
        return z.testzip() is None and all(t in names for t in REQUIRED_TABLES)
    except zipfile.BadZipFile:
        return False


def get_valid_zip(url: str, opener, attempts: int = 8) -> tuple[bytes, dict]:
    """fdc.nal.usda.gov was seen serving TWO different objects for the same URL on different requests (2026-11-20: 4,209,875 bytes, ETag 6aff073c, a complete dataset, and
    1,127,612 bytes, ETag 6ae24373, an older object without food.csv). Retry until a response is a complete dataset; never save anything else."""
    last = "no attempt"
    for _ in range(attempts):
        got = opener(url)
        data, meta = got if isinstance(got, tuple) else (got, {})
        if zip_intact(data):
            return data, meta
        last = f"{len(data)} bytes, etag {meta.get('etag')}: not a complete FDC dataset zip"
    raise OSError(f"{url}: no complete dataset zip after {attempts} requests (last: {last}); nothing saved")


def download(names: list[str], cache: Path, force: bool, opener=fetch) -> list[dict]:
    cache.mkdir(parents=True, exist_ok=True)
    manifest_path = cache / "downloads.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.is_file() else {}
    page_got = opener(DOWNLOAD_PAGE)
    page = (page_got[0] if isinstance(page_got, tuple) else page_got).decode("utf-8", "replace")
    done = []
    for name in names:
        s = require_enabled(name)
        url = discover_zip(page, s["family"])
        target = cache / Path(url).name
        meta: dict = {}
        if target.exists() and not force:
            data = target.read_bytes()
            if not zip_intact(data):
                raise OSError(f"{target} in the cache is not a complete dataset zip; delete it or use --force")
            meta = (manifest.get(name) or {}).get("http", {})
        else:
            data, meta = get_valid_zip(url, opener)
            target.write_bytes(data)
        rec = {"source": name, "url": url, "file": target.name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "http": meta,
               "retrieved_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "licence": FDC_LICENCE}
        manifest[name] = rec
        done.append(rec)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return done


# ---------------------------------------------------------------- normalisation
def norm_description(desc: str) -> str:
    return re.sub(r"\s+", " ", desc.strip().lower())


def split_parts(desc: str) -> list[str]:
    """The description split on commas (FDC convention 'group, item, form'), lowercased and tidied. No interpretation: that is WS3's job."""
    return [re.sub(r"\s+", " ", p).strip(" .;") for p in norm_description(desc).split(",") if p.strip(" .;")]


def release_of(zip_name: str) -> str:
    m = re.search(r"(\d{4}-\d{2}(?:-\d{2})?)", zip_name)
    return m.group(1) if m else "unknown"


def _read_csv(z: zipfile.ZipFile, basename: str) -> list[dict]:
    names = [n for n in z.namelist() if n.endswith("/" + basename) or n == basename]
    if not names:
        raise Refused(f"{basename} not found in the zip")
    with z.open(names[0]) as fh:
        return list(csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8-sig", newline="")))


def normalise_zip(path: Path, source: str, source_url: str | None = None) -> list[dict]:
    s = require_enabled(source)
    with zipfile.ZipFile(path) as z:
        cats = {r["id"]: r["description"] for r in _read_csv(z, "food_category.csv")}
        foods = _read_csv(z, "food.csv")
    release = release_of(path.name)
    url = source_url or f"https://{FDC_HOST}/fdc-datasets/{path.name}"
    rows = []
    for r in foods:
        if r["data_type"] not in s["data_types"]:
            continue
        rows.append({
            "candidate_id": f"fdc_{source}:{r['fdc_id']}", "dataset": source, "data_type": r["data_type"], "fdc_id": r["fdc_id"], "description": r["description"],
            "description_norm": norm_description(r["description"]), "parts": json.dumps(split_parts(r["description"]), ensure_ascii=False),
            "food_category_id": r.get("food_category_id", ""), "food_category": cats.get(r.get("food_category_id", ""), ""), "publication_date": r.get("publication_date", ""),
            "dataset_release": release, "source_url": url, "licence": "CC0 1.0 Universal"})
    rows.sort(key=lambda x: (x["dataset"], int(x["fdc_id"])))
    return rows


def write_candidates(rows: list[dict], out: Path, force: bool) -> None:
    if out.exists() and not force:
        raise FileExistsError(f"{out} exists; use --force to overwrite")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=CANDIDATE_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


# ---------------------------------------------------------------- CLI
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="USDA FoodData Central (CC0) bulk downloader and normaliser: candidate names with provenance only.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("download", help="fetch enabled dataset zips into the cache")
    d.add_argument("--sources", nargs="+", default=["foundation", "sr_legacy"])
    d.add_argument("--cache", type=Path, default=ROOT / "data" / "cache" / "fdc")
    d.add_argument("--force", action="store_true", help="re-download files already in the cache")
    n = sub.add_parser("normalise", help="write candidates.csv from cached zips")
    n.add_argument("--sources", nargs="+", default=["foundation", "sr_legacy"])
    n.add_argument("--cache", type=Path, default=ROOT / "data" / "cache" / "fdc")
    n.add_argument("--out", type=Path, required=True, help="candidates.csv to write")
    n.add_argument("--force", action="store_true", help="overwrite --out")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "download":
            for rec in download(args.sources, args.cache, args.force):
                print(f"{rec['source']}: {rec['file']} {rec['bytes']} bytes sha256 {rec['sha256'][:16]}...")
            return 0
        manifest_path = args.cache / "downloads.json"
        manifest = json.loads(manifest_path.read_text()) if manifest_path.is_file() else {}
        rows = []
        for name in args.sources:
            require_enabled(name)
            rec = manifest.get(name)
            if not rec:
                raise Refused(f"no download recorded for '{name}' in {manifest_path}; run `download` first")
            rows += normalise_zip(args.cache / rec["file"], name, rec["url"])
        write_candidates(rows, args.out, args.force)
        print(f"{len(rows)} candidate rows from {', '.join(args.sources)} -> {args.out}")
        return 0
    except FileExistsError as e:
        sys.stderr.write(f"Refusing to overwrite: {e}\n")
        return 2
    except Refused as e:
        sys.stderr.write(f"Refused: {e}\n")
        return 2
    except Exception as e:   # noqa: BLE001
        sys.stderr.write(f"Error: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
