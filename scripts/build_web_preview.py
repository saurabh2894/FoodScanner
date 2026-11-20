"""Build the single-file browser version: web_preview/dist/foodscan-preview.html.

Embeds the resource tables (from the same CSVs the Python app uses) and the JS port.
Run scripts/parity_check.py first; the page's footer claims parity.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from web_tables import tables  # noqa: E402

tpl = (ROOT / "web_preview" / "template.html").read_text(encoding="utf-8")
engine = (ROOT / "web_preview" / "foodscan.js").read_text(encoding="utf-8")
html = tpl.replace("/*TABLES*/", json.dumps(tables(), ensure_ascii=False).replace("</", "<\\/")) \
          .replace("/*ENGINE*/", engine.replace("</script", "<\\/script"))
out = ROOT / "web_preview" / "dist" / "foodscan-preview.html"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding="utf-8")
print(f"wrote {out} ({len(html) / 1024:.0f} KB)")
