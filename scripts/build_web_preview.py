"""Build the single-file browser version: web_preview/dist/foodscan-preview.html.

Embeds the resource tables (from the same CSVs the Python app uses) and the JS port.
Run scripts/parity_check.py first; the page's footer claims parity.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from parity_check import TOTAL, main as parity_main  # noqa: E402
from web_tables import tables  # noqa: E402

if parity_main() != 0:
    sys.exit("parity check failed: not building")

tpl = (ROOT / "web_preview" / "template.html").read_text(encoding="utf-8")
engine = (ROOT / "web_preview" / "foodscan.js").read_text(encoding="utf-8")
html = tpl.replace("/*TABLES*/", json.dumps(tables(), ensure_ascii=False).replace("</", "<\\/")) \
          .replace("/*ENGINE*/", engine.replace("</script", "<\\/script")) \
          .replace("/*PARITY*/", str(TOTAL))
VENDOR = ROOT / "web_preview" / "vendor" / "tess"
if not (VENDOR / "tesseract.min.js").exists():
    sys.exit("missing web_preview/vendor/tess: run python scripts/fetch_tesseract_assets.py first")
out = ROOT / "web_preview" / "dist" / "foodscan-preview.html"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding="utf-8")
print(f"wrote {out} ({len(html) / 1024:.0f} KB)")

import shutil  # noqa: E402

shutil.copytree(VENDOR, out.parent / "tess", dirs_exist_ok=True)
shutil.copy(ROOT / "web_preview" / "worker-boot.js", out.parent / "tess" / "worker-boot.js")
print(f"copied photo-reader files to {out.parent / 'tess'}")
shutil.copy(out, out.parent / "index.html")          # a static host serves index.html at the root
shutil.copy(ROOT / "web_preview" / "vercel.dist.json", out.parent / "vercel.json")
print("wrote index.html and vercel.json for static hosting")
