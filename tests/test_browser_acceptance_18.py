"""Task 18 acceptance gate (senior version): portable, local by default, results to tmp_path, no tracked evidence overwritten.
Skipped when node, playwright or the built page is missing. The full run uses the page's real local OCR (about 20 s)."""
from __future__ import annotations

import http.server
import json
import shutil
import socketserver
import subprocess
import sys
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import run_browser_acceptance_18 as gate  # noqa: E402

DIST = ROOT / "web_preview" / "dist"
TRACKED = ROOT / "evaluation" / "browser_acceptance_18_senior"


def _ready() -> bool:
    if shutil.which("node") is None or not (DIST / "index.html").exists():
        return False
    r = subprocess.run(["node", "-e", "require('playwright')"], capture_output=True, text=True, cwd=str(ROOT / "tests" / "js"))
    return r.returncode == 0


pytestmark = pytest.mark.skipif(not _ready(), reason="needs node, playwright and a built web_preview/dist (python scripts/build_web_preview.py)")


def _modified_fixtures(tmp_path, mutate):
    data = json.loads(gate.FIXTURES.read_text(encoding="utf-8"))
    mutate({f["key"]: f for f in data["labels"]})
    p = tmp_path / "fixtures.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def _results(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_provenance_detects_an_exact_rebuild_and_a_modified_dist(tmp_path, monkeypatch):
    prov = gate.build_provenance()
    assert prov["status"] in ("exact_rebuild_match", "mismatch")          # never assumed: it is compared byte for byte
    fake = tmp_path / "dist"
    shutil.copytree(DIST, fake)
    (fake / "index.html").write_text((fake / "index.html").read_text(encoding="utf-8") + "\n<!-- hand edit -->", encoding="utf-8")
    monkeypatch.setattr(gate, "DIST", fake)
    assert gate.build_provenance()["status"] == "mismatch"


def test_wrong_or_unverifiable_build_fails_the_gate(tmp_path):
    base = {"status": "mismatch", "reason": "test", "expectedParityTotal": None}
    rc, res, _ = gate.run_gate(tmp_path / "a", skip_photo=True, provenance=base)
    assert rc == 1 and any("exact rebuild" in n for n in _results(res)["summary"]["failedNames"])
    rc, res, _ = gate.run_gate(tmp_path / "b", skip_photo=True, provenance={"status": "unknown"})
    assert rc == 1 and any("exact rebuild" in n for n in _results(res)["summary"]["failedNames"])
    rc, res, _ = gate.run_gate(tmp_path / "c", skip_photo=True, provenance={"status": "unknown"}, allow_unknown_build=True)
    assert rc == 2 and _results(res)["summary"]["failed"] == 0            # explicit opt-in: unknown identity accepted, run still marked partial (no photo)


def test_wrong_expectations_and_missing_evidence_fail_with_a_nonzero_exit(tmp_path):
    fx = _modified_fixtures(tmp_path, lambda f: (f["L02"]["paste"].update(group=3), f["L06"]["paste"].update(driversInclude=["NOT A REAL DRIVER"])))
    rc, res, _ = gate.run_gate(tmp_path / "a", skip_photo=True, fixtures=fx)
    names = _results(res)["summary"]["failedNames"]
    assert rc == 1 and "L02 paste: group" in names and any("NOT A REAL DRIVER" in n for n in names)
    fx2 = _modified_fixtures(tmp_path, lambda f: f["L04"].update(textPath="evaluation/does_not_exist.txt"))
    rc, res, _ = gate.run_gate(tmp_path / "b", skip_photo=True, fixtures=fx2)
    s = _results(res)["summary"]
    assert rc == 1 and s["missingEvidence"]


def test_live_smoke_is_opt_in_and_compares_to_the_expected_stamp_only(tmp_path):
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("<html><body><footer><p>x 7 of 7 matched at build time.</p></footer></body></html>", encoding="utf-8")

    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=str(site), **k)

        def log_message(self, *a):
            pass

    with socketserver.TCPServer(("127.0.0.1", 0), H) as httpd:
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        url = f"http://127.0.0.1:{httpd.server_address[1]}/"
        rc, res, _ = gate.run_gate(tmp_path / "off", skip_photo=True, allow_unknown_build=True)
        assert _results(res)["liveSmoke"] is None                           # nothing contacted without the flag
        rc, res, _ = gate.run_gate(tmp_path / "obs", skip_photo=True, allow_unknown_build=True, smoke_live=url)
        assert _results(res)["liveSmoke"]["status"] == "observed_only" and rc == 2   # no expectation supplied: observation only, never a failure
        rc, res, _ = gate.run_gate(tmp_path / "ok", skip_photo=True, allow_unknown_build=True, smoke_live=url, expected_parity=7)
        assert _results(res)["liveSmoke"]["status"] == "stamp_matches_expected" and rc == 2
        rc, res, _ = gate.run_gate(tmp_path / "bad", skip_photo=True, allow_unknown_build=True, smoke_live=url, expected_parity=9)
        assert _results(res)["liveSmoke"]["status"] == "stamp_differs_from_expected" and rc == 1
        httpd.shutdown()


def test_full_gate_real_labels_real_ocr_item_level(tmp_path):
    before = sorted(p.name for p in TRACKED.rglob("*") if p.is_file())
    rc, res, log = gate.run_gate(tmp_path / "full")
    data = _results(res)
    assert rc == 0, (log, data["summary"]["failedNames"], data["summary"]["missingEvidence"])
    assert data["provenance"]["status"] == "exact_rebuild_match" and data["summary"]["failed"] == 0 and not data["summary"]["missingEvidence"]
    names = {c["name"] for c in data["checks"]}
    # the assertions that were missing in the first version: item level, Done + non-empty text, separate completeness, correction proven or skipped honestly
    for n in ("L03 paste: driver/weak-evidence item \"Maltodextrin\"", "L03 paste: result mentions \"was never closed\"", "L02 photo: extracted text contains \"Supergrain Blend\"",
              "L02 photo: reading finished with \"Done\" (not failed/stalled/timeout)", "L03 paste: completeness (separate from group)", "L05 paste: result mentions \"Refined Palmolien Oil\""):
        assert n in names, n
    assert all(c["pass"] for c in data["checks"])
    corr = data["labels"]["L01"]["ocrCorrection"]
    assert corr["status"] in ("run", "skipped") and (corr["status"] == "skipped" and corr["reason"] or corr["beforeGroup"] is None)
    assert data["inventory"]["realLabels"] == len(data["labels"]) and data["inventory"]["withPhysicalPhoto"] == len(data["inventory"]["photoKeys"])
    assert data["controls"]["synthetic_edit_reanalyse"]["kind"] == "SYNTHETIC_MUTATION_CONTROL"
    assert sorted(p.name for p in TRACKED.rglob("*") if p.is_file()) == before    # tracked evidence untouched
