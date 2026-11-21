"""The page shows unplaced items in their own section, apart from "Not assessed", and assigns no level (skipped without node, playwright or a built web_preview/dist)."""
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


@pytest.mark.skipif(shutil.which("node") is None or not (DIST / "index.html").exists(), reason="needs node and a built web_preview/dist")
def test_unplaced_items_render_distinctly_and_no_level_is_assigned():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=DIST, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(1.0)
        r = subprocess.run(["node", str(ROOT / "tests" / "js" / "unplaced_render_smoke.js"), f"http://127.0.0.1:{port}"], capture_output=True, text=True, timeout=90)
        if r.returncode and "Cannot find module 'playwright'" in r.stderr:
            pytest.skip("playwright is not installed")
        assert r.returncode == 0, r.stderr
        out = json.loads(r.stdout)
        secs = out["secs"]
        assert [x.lower() for x in secs["Recognised by name, not placed"]] == ["vitamins", "minerals", "sprouted ragi"]
        assert secs["Not assessed"] == ["Zorbium"]                                      # unknown word stays in its own section
        assert "No level assigned" in (out["scale"] or "")                              # never presented as a classification
    finally:
        srv.terminate()
