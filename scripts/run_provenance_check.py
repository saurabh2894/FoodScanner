"""Strict, local cross-input reliability gate. Never installs dependencies implicitly.

Exit 0: all 22 mocked-reader controls passed; 1: check failed; 2: setup missing.
This gate does not measure real photo/OCR accuracy or contact production.
"""
from __future__ import annotations
import argparse
import functools
import http.server
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading

ROOT = Path(__file__).resolve().parent.parent


def setup_error(message):
    print('SETUP REQUIRED: ' + message, file=sys.stderr)
    return 2


def run(out_dir: Path, browser: str | None = None):
    if not shutil.which('node'):
        return setup_error('Install Node.js, then run npm ci and npx playwright install chromium.')
    probe = subprocess.run(['node', '-e', "const{chromium}=require('playwright');console.log(chromium.executablePath())"], cwd=ROOT, capture_output=True, text=True)
    if probe.returncode:
        return setup_error('Run npm ci in the repository root, then npx playwright install chromium.')
    executable = browser or os.environ.get('FOODSCAN_BROWSER') or probe.stdout.strip()
    if not Path(executable).is_file():
        return setup_error('Chromium not found. Run npx playwright install chromium or set FOODSCAN_BROWSER to an installed Chromium executable.')
    if not (ROOT / 'web_preview/dist/index.html').is_file():
        return setup_error('Build the current page: python scripts/fetch_tesseract_assets.py then python scripts/build_web_preview.py.')
    # Existing acceptance helper compares served bytes to a source rebuild.
    sys.path.insert(0, str(ROOT / 'scripts'))
    from run_browser_acceptance_18 import build_provenance
    identity = build_provenance()
    if identity.get('status') != 'exact_rebuild_match':
        print('FAILED: built page does not exactly match current sources; rebuild before testing.', file=sys.stderr)
        return 1
    image = ROOT / 'evaluation/browser_acceptance_18_senior/inputs/original_multigrain_label.jpg'
    if not image.is_file():
        return setup_error('The existing multigrain regression photo is missing from the checkout.')
    out_dir.mkdir(parents=True, exist_ok=True)
    # A previous run's evidence must never satisfy a new run.
    (out_dir / 'result-source-controls.json').unlink(missing_ok=True)
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(ROOT / 'web_preview/dist')))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    env = os.environ.copy()
    env['FOODSCAN_BROWSER'] = executable
    try:
        result = subprocess.run(['node', str(ROOT / 'tests/js/result_source_provenance.js'), 'http://127.0.0.1:' + str(server.server_address[1]) + '/index.html', str(image), str(out_dir)], cwd=ROOT, env=env, capture_output=True, text=True, timeout=90)
        (out_dir / 'browser.stdout.log').write_text(result.stdout)
        (out_dir / 'browser.stderr.log').write_text(result.stderr)
        if result.returncode:
            print(result.stdout + result.stderr, file=sys.stderr)
            return 1
        record = json.loads((out_dir / 'result-source-controls.json').read_text())
        checks = record.get('checks', [])
        if len(checks) != 22 or not all(c.get('passed') is True for c in checks):
            print('FAILED: expected exactly 22 passing source-provenance controls.', file=sys.stderr)
            return 1
        print('22/22 cross-input browser controls passed (mocked OCR, not photo accuracy).')
        print('Evidence: ' + str(out_dir))
        return 0
    except (subprocess.TimeoutExpired, OSError, ValueError) as exc:
        print('FAILED: browser gate did not finish: ' + str(exc), file=sys.stderr)
        return 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir', type=Path)
    parser.add_argument('--browser', help='Optional installed Chromium executable; otherwise FOODSCAN_BROWSER or Playwright Chromium.')
    args = parser.parse_args()
    out_dir = args.out_dir or Path(tempfile.mkdtemp(prefix='foodscan-provenance-'))
    return run(out_dir, args.browser)


if __name__ == '__main__':
    raise SystemExit(main())
