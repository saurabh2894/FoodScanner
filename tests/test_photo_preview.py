"""Photo preview in the browser page (web_preview/dist/index.html): skipped when node, playwright or the built page is missing."""
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


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.mark.skipif(shutil.which("node") is None or not (DIST / "index.html").exists(), reason="needs node and a built web_preview/dist (python scripts/build_web_preview.py)")
def test_photo_preview_is_a_self_contained_thumbnail_and_never_a_broken_image(tmp_path):
    port = _free_port()
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=DIST, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(1.0)
        r = subprocess.run(["node", str(ROOT / "tests" / "js" / "photo_preview_smoke.js"), f"http://127.0.0.1:{port}", str(tmp_path)], capture_output=True, text=True, timeout=120)
        if r.returncode and "Cannot find module 'playwright'" in r.stderr:
            pytest.skip("playwright is not installed")
        assert r.returncode == 0, r.stderr
        out = json.loads(r.stdout)
        for k in ("selected", "fileGone", "tabRound"):
            assert out[k]["hidden"] is False and out[k]["complete"] and 0 < out[k]["nw"] <= 640 and out[k]["src"] == "data:image/", (k, out[k])
        assert out["notImage"]["hidden"] is True and out["notImage"]["nw"] == 0 and "no preview could be shown" in out["notImage"]["status"]
    finally:
        srv.terminate()
