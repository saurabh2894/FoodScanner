"""Build the browser version into web_preview/dist/.

Two outputs from one template:
  foodscan-preview.html  the artifact page. The artifact host wraps it in a document skeleton itself.
  index.html             the same page wrapped for ordinary static hosting (Vercel): doctype, lang,
                         viewport, description, favicon. Without these a phone lays the page out at 980 px
                         wide in quirks mode, so the static build must carry them itself.
Hosting config (headers, build commands) lives in the repo-root vercel.json, the single source for Git deploys.
Run order: scripts/fetch_tesseract_assets.py once, then this. It refuses to build unless the Python and
JS implementations agree on every parity text.
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from parity_check import TOTAL, main as parity_main  # noqa: E402
from web_tables import tables  # noqa: E402

DESCRIPTION = ("Paste an Indian packaged-food ingredient list, or photograph the label, and see its NOVA "
               "processing level with the ingredients behind the call. Runs in your browser; nothing is uploaded.")
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
           "%3Crect width='32' height='32' rx='6' fill='%230d6b5a'/%3E"
           "%3Crect x='6' y='19' width='4' height='7' fill='%23d4ebe3'/%3E%3Crect x='12' y='15' width='4' height='11' fill='%239fd0c2'/%3E"
           "%3Crect x='18' y='11' width='4' height='15' fill='%234fa593'/%3E%3Crect x='24' y='6' width='4' height='20' fill='white'/%3E%3C/svg%3E")


def wrap_for_static(page: str) -> str:
    """Wrap the artifact-style page (head elements, then body content) in a full HTML document."""
    cut = page.index("</style>") + len("</style>")
    head, body = page[:cut], page[cut:]
    head = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>\n?', "", head)   # artifact-host tag only
    return (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        f'<meta name="description" content="{DESCRIPTION}">\n'
        f'<link rel="icon" href="{FAVICON}">\n'
        f"{head}\n</head>\n<body>{body}\n</body>\n</html>\n"
    )


def build() -> None:
    if parity_main() != 0:
        sys.exit("parity check failed: not building")
    vendor = ROOT / "web_preview" / "vendor" / "tess"
    if not (vendor / "tesseract.min.js").exists():
        sys.exit("missing web_preview/vendor/tess: run python scripts/fetch_tesseract_assets.py first")

    tpl = (ROOT / "web_preview" / "template.html").read_text(encoding="utf-8")
    engine = (ROOT / "web_preview" / "foodscan.js").read_text(encoding="utf-8")
    page = (tpl.replace("/*TABLES*/", json.dumps(tables(), ensure_ascii=False).replace("</", "<\\/"))
               .replace("/*ENGINE*/", engine.replace("</script", "<\\/script"))
               .replace("/*PARITY*/", str(TOTAL)))

    dist = ROOT / "web_preview" / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    (dist / "foodscan-preview.html").write_text(page, encoding="utf-8")
    (dist / "index.html").write_text(wrap_for_static(page), encoding="utf-8")
    shutil.copytree(vendor, dist / "tess", dirs_exist_ok=True)
    shutil.copy(ROOT / "web_preview" / "worker-boot.js", dist / "tess" / "worker-boot.js")
    print(f"wrote {dist / 'foodscan-preview.html'} (artifact) and {dist / 'index.html'} (static host), "
          f"{len(page) / 1024:.0f} KB; photo-reader files copied")


if __name__ == "__main__":
    build()
