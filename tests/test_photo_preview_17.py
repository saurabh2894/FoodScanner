"""Focused browser UI tests for Task 17: photo preview path and acceptance proof on original label."""
from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "web_preview" / "dist"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ORIG_IMAGE = Path(r"C:\Users\saura\.gemini\antigravity\brain\73116aea-a21b-45f7-8d9c-07175e0d5b6a\.user_uploaded\media_1795270130128_c7dc15e3.jpg")


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.mark.skipif(
    not os.path.exists(CHROME_PATH) or shutil.which("node") is None or not (DIST / "index.html").exists(),
    reason="needs Chrome, node, and built web_preview/dist"
)
def test_photo_preview_17_matrix(tmp_path):
    http_port = _free_port()
    cdp_port = _free_port()

    # 1. Start static server
    srv = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(http_port), "--bind", "127.0.0.1"],
        cwd=DIST,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # 2. Start Chrome headless
    user_data = tmp_path / "chrome_user_data"
    user_data.mkdir(parents=True, exist_ok=True)
    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        f"--remote-debugging-port={cdp_port}",
        f"--user-data-dir={user_data}",
        "--headless=new",
        "--window-size=1280,720",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        f"http://127.0.0.1:{http_port}/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    time.sleep(2)

    try:
        # Create second test image (valid PNG) and invalid non-image file
        valid_png = tmp_path / "valid_alt.png"
        import struct, zlib
        # Simple 1x1 valid PNG
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\r\xef5\xc8\x00\x00\x00\x00IEND\xaeB`\x82'
        valid_png.write_bytes(png_data)

        invalid_file = tmp_path / "not_an_image.txt"
        invalid_file.write_text("Hello, this is plain text, not an image.", encoding="utf-8")

        screenshot_dir = ROOT / "evaluation" / "photo_preview_17" / "screenshots"
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        runner_script = ROOT / "tests" / "js" / "photo_preview_17_runner.js"
        res = subprocess.run(
            ["node", str(runner_script), str(cdp_port), str(ORIG_IMAGE), str(valid_png), str(invalid_file), str(screenshot_dir)],
            capture_output=True,
            text=True,
            timeout=90
        )
        assert res.returncode == 0, f"Node script failed:\n{res.stderr}\n{res.stdout}"

        data = json.loads(res.stdout)
        results = data["results"]

        # Check Original JPEG Desktop
        orig = results["original_jpeg_desktop"]
        assert orig["previewHidden"] is False
        assert orig["previewSrc"].startswith("data:image/jpeg")
        assert orig["previewComplete"] is True
        assert 0 < orig["naturalWidth"] <= 640
        assert 0 < orig["naturalHeight"] <= 640
        assert orig["btnDisabled"] is False
        assert "Photo ready." in orig["status"]

        # Check Original JPEG Mobile (390x844)
        mob = results["original_jpeg_mobile"]
        assert mob["previewHidden"] is False
        assert mob["previewSrc"].startswith("data:image/jpeg")
        assert mob["previewComplete"] is True
        assert mob["clientWidth"] <= 390
        assert mob["scrollWidth"] <= 390  # No horizontal overflow

        # Check Valid PNG
        png_res = results["valid_png"]
        assert png_res["previewHidden"] is False
        assert png_res["previewSrc"].startswith("data:image/")
        assert png_res["previewComplete"] is True

        # Check Invalid non-image
        bad = results["invalid_file"]
        assert bad["previewHidden"] is True
        assert bad["naturalWidth"] == 0
        assert "no preview could be shown" in bad["status"]
        assert bad["btnDisabled"] is False  # OCR button stays usable

        # Check Clear selection
        cleared = results["cleared_selection"]
        assert cleared["previewHidden"] is True
        assert cleared["status"] == ""
        assert cleared["btnDisabled"] is True

        # Check Replacement
        rep = results["replacement"]
        assert rep["loadingStateObserved"] is True
        assert rep["oldPreviewClearedImmediately"] is True

        # Check Reselecting same file
        reselect = results["reselect_same"]
        assert reselect["reselectEventFired"] is True
        assert reselect["previewHidden"] is False

        # Check Tab switch
        tab = results["tab_switch"]
        assert tab["previewHidden"] is False
        assert tab["status"] == orig["status"]

        # Check End-to-end OCR and result clearing
        e2e = results["ocr_end_to_end"]
        assert e2e["ocrCompleted"] is True
        assert "INGREDIENTS" in e2e["extractedText"]
        assert "Multigrain Flour Blend" in e2e["extractedText"]
        assert e2e["resultCardRendered"] is True
        assert e2e["newSelectionClearedPriorResult"] is True

    finally:
        chrome_proc.terminate()
        srv.terminate()
