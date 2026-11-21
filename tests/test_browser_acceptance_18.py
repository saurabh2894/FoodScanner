"""Task 18: Repeatable real-label browser acceptance gate test suite."""
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
RUNNER_JS = ROOT / "tests" / "js" / "browser_acceptance_18_runner.js"
OUT_DIR = ROOT / "evaluation" / "browser_acceptance_18"
OUT_JSON = OUT_DIR / "test_results.json"
SCREENSHOTS_DIR = OUT_DIR / "screenshots"


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.mark.skipif(
    not os.path.exists(CHROME_PATH) or shutil.which("node") is None or not (DIST / "index.html").exists(),
    reason="requires Chrome, node, and built web_preview/dist"
)
def test_browser_acceptance_18_gate(tmp_path):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

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
        # 3. Execute JS Runner
        cmd = [
            shutil.which("node"),
            str(RUNNER_JS),
            f"--cdp-port={cdp_port}",
            f"--target=http://127.0.0.1:{http_port}/index.html",
            f"--out={OUT_JSON}",
            f"--screenshots-dir={SCREENSHOTS_DIR}",
            "--smoke-live"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        assert res.returncode == 0, f"JS runner failed: stdout={res.stdout}\nstderr={res.stderr}"

        assert OUT_JSON.exists(), "Results JSON was not written"
        data = json.loads(OUT_JSON.read_text(encoding="utf-8"))

        # Gating Assertions
        summary = data["summary"]
        assert summary["totalUniqueRealLabels"] == 6, f"Expected 6 unique real labels, got {summary['totalUniqueRealLabels']}"
        assert summary["failedExecutions"] == 0, f"Gate failed with {summary['failedExecutions']} failures: {json.dumps(data, indent=2)}"
        assert summary["passedExecutions"] == summary["totalExecutions"], "Not all executions passed"
        assert summary["totalExecutions"] >= 13, f"Expected at least 13 test executions, got {summary['totalExecutions']}"

        # Real Labels Assertions
        labels = data["labels"]
        assert "L01" in labels and "L02" in labels and "L03" in labels
        assert "L04" in labels and "L05" in labels and "L06" in labels

        # Multigrain L01
        l01 = labels["L01"]
        assert l01["pasteFlow"]["passed"] is True
        assert l01["pasteFlow"]["isAbstain"] is True
        assert l01["pasteFlow"]["observedGroup"] is None
        assert l01["editAndReanalyse"]["passed"] is True
        assert l01["editAndReanalyse"]["provesFreshInputAssociation"] is True
        assert l01["photoFlow"]["passed"] is True
        assert l01["photoFlow"]["ocrIsAbstain"] is True
        assert l01["ocrCorrectionFlow"]["passed"] is True

        # Millet Puff L02
        l02 = labels["L02"]
        assert l02["pasteFlow"]["passed"] is True
        assert l02["pasteFlow"]["observedGroup"] == 4
        assert l02["photoFlow"]["passed"] is True

        # Chips L03
        l03 = labels["L03"]
        assert l03["pasteFlow"]["passed"] is True
        assert l03["pasteFlow"]["observedGroup"] == 4
        assert l03["photoFlow"]["passed"] is True

        # Negation Labels L04, L05, L06
        assert labels["L04"]["pasteFlow"]["isAbstain"] is True
        assert labels["L04"]["pasteFlow"]["observedGroup"] is None
        assert labels["L05"]["pasteFlow"]["isAbstain"] is True
        assert labels["L05"]["pasteFlow"]["observedGroup"] is None
        assert labels["L06"]["pasteFlow"]["observedGroup"] == 4

        # Synthetic Controls Assertions
        controls = data["syntheticControls"]
        assert controls["NC01_empty"]["passed"] is True
        assert controls["NC01_empty"]["noStaleGroupVisible"] is True
        assert controls["NC02_unknown_compound"]["passed"] is True
        assert controls["NC02_unknown_compound"]["noStaleGroupVisible"] is True

        # Viewport Inspection Assertions
        px = data["pixelInspection"]
        assert px["desktop_1280x720"]["hasHorizontalOverflow"] is False
        assert px["mobile_390x844"]["hasHorizontalOverflow"] is False
        assert px["mobile_390x844"]["noHorizontalOverflowPass"] is True
        assert px["mobile_390x844"]["buttonsFullyVisible"] is True

        # Stale Client Audit Assertions
        audit = data["clientConfusionAudit"]
        assert audit["localBuild"]["parityMatched"] == 921
        assert audit["localBuild"]["isCurrentSeniorBaseline"] is True
        if "liveProduction" in audit and "parityMatched" in audit["liveProduction"]:
            assert audit["liveProduction"]["parityMatched"] == 859
            assert audit["liveProduction"]["staleBuildDetected"] is True

    finally:
        chrome_proc.terminate()
        srv.terminate()
        try:
            chrome_proc.wait(timeout=3)
        except Exception:
            chrome_proc.kill()
        try:
            srv.wait(timeout=3)
        except Exception:
            srv.kill()
