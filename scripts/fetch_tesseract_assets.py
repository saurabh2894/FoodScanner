"""Fetch the pinned tesseract.js files the browser page ships alongside itself.

Why: by default tesseract.js downloads its worker, engine and English data from a CDN at runtime,
and the artifact viewer blocks such fetches (and refuses .gz files), so photo reading stalled. The page now loads everything
from its own published files. All three packages are Apache-2.0.

Usage: python scripts/fetch_tesseract_assets.py     (needs npm; writes web_preview/vendor/tess/, git-ignored)
"""
import base64
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "web_preview" / "vendor" / "tess"
PACKAGES = ["tesseract.js@5.1.1", "tesseract.js-core@5.1.1", "@tesseract.js-data/eng@1.0.0"]
# (package tarball prefix, path inside package, destination under DEST)
WANTED = [
    ("tesseract.js-5.1.1.tgz", "package/dist/tesseract.min.js", "tesseract.min.js"),
    ("tesseract.js-5.1.1.tgz", "package/dist/worker.min.js", "worker.min.js"),
    ("tesseract.js-core-5.1.1.tgz", "package/tesseract-core-simd-lstm.wasm.js", "tesseract-core-simd-lstm.wasm.js"),
    ("tesseract.js-core-5.1.1.tgz", "package/tesseract-core-lstm.wasm.js", "tesseract-core-lstm.wasm.js"),
    ("tesseract.js-data-eng-1.0.0.tgz", "package/4.0.0_best_int/eng.traineddata.gz", "eng.traineddata.b64.txt"),
]


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["npm", "pack", *PACKAGES], cwd=td, check=True, capture_output=True)
        for tgz, inner, dest in WANTED:
            with tarfile.open(Path(td) / tgz) as tar:
                member = tar.getmember(inner)
                out = DEST / dest
                out.parent.mkdir(parents=True, exist_ok=True)
                with tar.extractfile(member) as src, out.open("wb") as dst:
                    if dest.endswith(".b64.txt"):  # the viewer serves text files, not .gz: see web_preview/worker-boot.js
                        dst.write(base64.b64encode(src.read()))
                    else:
                        shutil.copyfileobj(src, dst)
                print(f"{dest}: {out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
