"""Photo selection races (Task 17): a replaced or removed photo must not be restored, read, or have another photo's result shown.
Deterministic: the thumbnail decode and the text reader are held on promises released by hand (tests/js/photo_races_17.js). Portable: images are generated
in the page, the browser is whatever playwright provides; skipped when node, playwright or the built page is missing. Not a native file-picker or real OCR test."""
from __future__ import annotations

import json
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "web_preview" / "dist"
DONE = "Done."
READY = "Photo ready. Press Read photo and analyse."


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def races(tmp_path_factory):
    if shutil.which("node") is None or not (DIST / "index.html").exists():
        pytest.skip("needs node and a built web_preview/dist (python scripts/build_web_preview.py)")
    port = _free_port()
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=DIST, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(1.0)
        r = subprocess.run(["node", str(ROOT / "tests" / "js" / "photo_races_17.js"), f"http://127.0.0.1:{port}", str(tmp_path_factory.mktemp("races"))], capture_output=True, text=True, timeout=240)
        if r.returncode and "Cannot find module 'playwright'" in r.stderr:
            pytest.skip("playwright is not installed")
        assert r.returncode == 0, r.stderr
        return json.loads(r.stdout)
    finally:
        srv.terminate()


def test_thumbnail_of_a_replaced_photo_never_shows(races):
    p = races["thumb_replaced"]
    assert p["hidden"] is False and p["color"][2] > 200 and p["color"][0] < 50      # B (blue), not A (red)


def test_thumbnail_pending_when_selection_is_cleared_or_cancelled_never_comes_back(races):
    for k in ("thumb_cleared", "thumb_cancel_empty"):
        assert races[k]["hidden"] is True and races[k]["hasSrc"] is False and races[k]["analyseEnabled"] is False, k


def test_synthetic_cancel_with_the_selection_intact_changes_nothing(races):
    r = races["synthetic_cancel"]
    assert r["analyseEnabledAfterCancel"] is False and r["terminatedAfterCancel"] == 0     # still running, not stopped
    assert r["final"]["status"].startswith(DONE) and r["prev"]["hidden"] is False


def test_replacing_the_photo_during_the_first_reading_stops_it_and_shows_no_result(races):
    r = races["replace_during_first_read"]
    assert r["beforeRelease"]["terminated"] == 1 and r["beforeRelease"]["result"] == ""      # stopped at once, old progress card removed
    assert r["ocrCalls"] == 1                                                                 # no second pass was started
    assert "B.png" in r["final"]["opened"] and r["final"]["opened"].count("A.png") == 2       # thumbnail + first reading of A; nothing re-read A or read B for A's run
    assert r["final"]["status"] == READY and r["final"]["result"] == "" and r["analyseEnabled"] is True


def test_second_pass_result_of_a_replaced_photo_is_not_shown(races):
    r = races["replace_during_second_read"]["final"]
    assert r["status"] == READY and r["result"] == "" and r["opened"] == ["A.png", "A.png", "A.png", "B.png"]


def test_clearing_the_photo_during_a_reading_leaves_no_failure_card_and_a_disabled_button(races):
    r = races["clear_during_first_read"]
    assert r["ocrCalls"] == 1 and r["final"]["status"] == "" and r["final"]["result"] == "" and r["final"]["analyse"] is False and r["final"]["terminated"] == 1


def test_a_finished_result_is_removed_when_another_photo_is_chosen(races):
    r = races["result_after_replace"]
    assert r["done"]["status"].startswith(DONE) and r["done"]["result"]
    assert r["afterReplace"]["result"] == "" and r["afterReplace"]["status"] == READY
