#!/usr/bin/env python3
"""Task 18 real-label browser acceptance gate (portable, local by default).

  python scripts/run_browser_acceptance_18.py [--out-dir DIR] [--browser PATH] [--skip-photo] [--allow-unknown-build]
                                              [--smoke-live URL [--expected-parity N]]

Defaults: serves web_preview/dist on 127.0.0.1, drives playwright's own Chromium (or --browser / $FOODSCAN_BROWSER), real local OCR,
writes results and screenshots under a temp directory (pass --out-dir to refresh tracked evidence on purpose). Production is contacted only with --smoke-live.
Exit codes: 0 pass; 1 failed check / missing evidence / wrong or unverifiable local build; 2 partial (--skip-photo).
Build identity: the served dist is compared byte for byte with a fresh in-memory build of the current sources (template, engine, tables); the record also holds git HEAD,
whether the source files are modified, and sha256 of the served pages. The footer stamp is recorded but is never used as proof of identity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "web_preview" / "dist"
RUNNER = ROOT / "tests" / "js" / "browser_acceptance_18_senior.js"
FIXTURES = ROOT / "evaluation" / "browser_acceptance_18_senior" / "fixtures.json"
SOURCES = ["web_preview/template.html", "web_preview/foodscan.js", "web_preview/worker-boot.js", "scripts/build_web_preview.py", "scripts/web_tables.py", "src/foodscan"]


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _git(*args: str) -> str | None:
    try:
        return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, timeout=30, check=True).stdout.strip()
    except Exception:
        return None


def build_provenance() -> dict:
    """Return the identity record of web_preview/dist. status: exact_rebuild_match | mismatch | unknown (cannot be established)."""
    prov: dict = {"gitHead": _git("rev-parse", "HEAD"), "sourcesModifiedVsHead": None, "distFiles": {}, "status": "unknown", "reason": None, "expectedParityTotal": None}
    dirty = _git("status", "--porcelain", "--", *SOURCES)
    prov["sourcesModifiedVsHead"] = None if dirty is None else bool(dirty)
    for name in ("index.html", "foodscan-preview.html"):
        p = DIST / name
        if p.exists():
            prov["distFiles"][name] = {"sha256": _sha(p.read_bytes()), "bytes": p.stat().st_size}
    if not (DIST / "index.html").exists():
        prov["reason"] = "web_preview/dist/index.html not found"
        return prov
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        sys.path.insert(0, str(ROOT / "src"))
        from build_web_preview import wrap_for_static  # noqa: E402
        from parity_check import TOTAL  # noqa: E402
        from web_tables import tables  # noqa: E402
        tpl = (ROOT / "web_preview" / "template.html").read_text(encoding="utf-8")
        engine = (ROOT / "web_preview" / "foodscan.js").read_text(encoding="utf-8")
        page = (tpl.replace("/*TABLES*/", json.dumps(tables(), ensure_ascii=False).replace("</", "<\\/"))
                   .replace("/*ENGINE*/", engine.replace("</script", "<\\/script"))
                   .replace("/*PARITY*/", str(TOTAL)))
        expect = {"foodscan-preview.html": page, "index.html": wrap_for_static(page)}
        prov["expectedParityTotal"] = TOTAL
        prov["rebuildSha256"] = {k: _sha(v.encode("utf-8")) for k, v in expect.items()}
        same = all(prov["distFiles"].get(k, {}).get("sha256") == prov["rebuildSha256"][k] for k in expect)
        prov["status"] = "exact_rebuild_match" if same else "mismatch"
        prov["reason"] = None if same else "web_preview/dist differs from a fresh build of the current sources (stale or hand-edited): run scripts/build_web_preview.py"
    except Exception as e:  # cannot rebuild here: identity unknown, never assumed
        prov["reason"] = f"rebuild comparison unavailable: {type(e).__name__}: {e}"
    return prov


def run_gate(out_dir: Path, browser: str | None = None, skip_photo: bool = False, allow_unknown_build: bool = False, smoke_live: str | None = None,
             expected_parity: int | None = None, fixtures: Path = FIXTURES, provenance: dict | None = None, timeout: int = 600) -> tuple[int, Path, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    prov = provenance if provenance is not None else build_provenance()
    (out_dir / "provenance.json").write_text(json.dumps(prov, indent=2), encoding="utf-8")
    port = _free_port()
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=DIST, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(1.0)
        cmd = ["node", str(RUNNER), f"--target=http://127.0.0.1:{port}/index.html", f"--out={out_dir / 'results.json'}", f"--screenshots-dir={out_dir / 'screenshots'}",
               f"--fixtures={fixtures}", f"--root={ROOT}", f"--provenance={out_dir / 'provenance.json'}"]
        if browser:
            cmd.append(f"--browser={browser}")
        if skip_photo:
            cmd.append("--skip-photo")
        if allow_unknown_build:
            cmd.append("--allow-unknown-build")
        if smoke_live:
            cmd.append(f"--smoke-live={smoke_live}")
            if expected_parity is not None:
                cmd.append(f"--expected-parity={expected_parity}")
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(ROOT / "tests" / "js"))
        return r.returncode, out_dir / "results.json", r.stdout + r.stderr
    finally:
        srv.terminate()
        try:
            srv.wait(timeout=3)
        except Exception:
            srv.kill()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", default=None, help="where results.json, provenance.json and screenshots go (default: a new temp directory; tracked evidence is not touched)")
    ap.add_argument("--browser", default=os.environ.get("FOODSCAN_BROWSER"), help="Chrome/Chromium executable (default: playwright's bundled Chromium)")
    ap.add_argument("--skip-photo", action="store_true", help="paste flows only; exit code 2, not an acceptance")
    ap.add_argument("--allow-unknown-build", action="store_true", help="accept a dist whose identity cannot be established (still fails on a mismatch)")
    ap.add_argument("--smoke-live", default=None, metavar="URL", help="explicit opt-in: read the footer stamp of this deployed URL")
    ap.add_argument("--expected-parity", type=int, default=None, help="with --smoke-live: the stamp you expect the deployed build to show")
    a = ap.parse_args()
    if shutil.which("node") is None:
        print("node not found", file=sys.stderr)
        return 1
    out = Path(a.out_dir) if a.out_dir else Path(tempfile.mkdtemp(prefix="foodscan_accept18_"))
    rc, res, log = run_gate(out, a.browser, a.skip_photo, a.allow_unknown_build, a.smoke_live, a.expected_parity)
    print(log)
    print(f"results: {res}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
