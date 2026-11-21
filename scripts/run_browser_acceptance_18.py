#!/usr/bin/env python3
"""CLI runner for Task 18: Repeatable real-label browser acceptance gate."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

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


def main():
    parser = argparse.ArgumentParser(description="Run repeatable browser acceptance gate")
    parser.add_argument("--smoke-live", action="store_true", help="Inspect production site once without hammering")
    parser.add_argument("--chrome-path", default=CHROME_PATH, help="Path to Chrome executable")
    args = parser.parse_args()

    if not os.path.exists(args.chrome_path):
        print(f"Error: Chrome executable not found at {args.chrome_path}", file=sys.stderr)
        sys.exit(1)

    node_bin = shutil.which("node")
    if not node_bin:
        print("Error: node executable not found in PATH", file=sys.stderr)
        sys.exit(1)

    if not (DIST / "index.html").exists():
        print("Error: web_preview/dist/index.html not found. Run scripts/build_web_preview.py first.", file=sys.stderr)
        sys.exit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    http_port = _free_port()
    cdp_port = _free_port()

    print(f"Starting local static server on port {http_port}...")
    srv = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(http_port), "--bind", "127.0.0.1"],
        cwd=DIST,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    import tempfile
    with tempfile.TemporaryDirectory() as tmp_dir:
        user_data = Path(tmp_dir) / "chrome_user_data"
        user_data.mkdir(parents=True, exist_ok=True)

        print(f"Starting headless Chrome on CDP port {cdp_port}...")
        chrome_proc = subprocess.Popen([
            args.chrome_path,
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
            cmd = [
                node_bin,
                str(RUNNER_JS),
                f"--cdp-port={cdp_port}",
                f"--target=http://127.0.0.1:{http_port}/index.html",
                f"--out={OUT_JSON}",
                f"--screenshots-dir={SCREENSHOTS_DIR}"
            ]
            if args.smoke_live:
                cmd.append("--smoke-live")

            print("Executing browser acceptance test matrix...")
            t0 = time.time()
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            elapsed = time.time() - t0

            if res.returncode != 0:
                print(f"Execution failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}", file=sys.stderr)
                sys.exit(1)

            print(res.stdout)
            print(f"Gate completed in {elapsed:.1f}s. Results written to {OUT_JSON}.")

            if OUT_JSON.exists():
                data = json.loads(OUT_JSON.read_text(encoding="utf-8"))
                summary = data["summary"]
                print(f"\n--- GATE RESULTS ---")
                print(f"Unique Real Labels Tested: {summary['totalUniqueRealLabels']}")
                print(f"Total Executions:          {summary['totalExecutions']}")
                print(f"Passed Executions:         {summary['passedExecutions']}")
                print(f"Failed Executions:         {summary['failedExecutions']}")
                audit = data["clientConfusionAudit"]
                print(f"Local Baseline Parity:     {audit['localBuild']['parityMatched']}/{audit['localBuild']['parityTotal']}")
                if "liveProduction" in audit and "parityMatched" in audit["liveProduction"]:
                    print(f"Live Production Parity:    {audit['liveProduction']['parityMatched']}/{audit['liveProduction']['parityTotal']} (Stale Build Detected: {audit['liveProduction']['staleBuildDetected']})")

                if summary["failedExecutions"] > 0:
                    sys.exit(1)
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


if __name__ == "__main__":
    main()
