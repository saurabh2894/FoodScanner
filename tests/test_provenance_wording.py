"""Display-only INS names come from the JECFA pages that were read (ins_names.csv), so no row or footer may cite Codex CXG 36 for them."""
from pathlib import Path

from foodscan.web.app import create_app

ROOT = Path(__file__).resolve().parent.parent


class FakeOcr:
    def __init__(self, text): self.text = text
    def extract_text(self, p): return self.text


def test_python_page_cites_jecfa_not_codex_for_bare_code_rows():
    from test_web import post
    html = post(create_app(FakeOcr("Ingredients: Water, Sugar, Potassium chloride (INS 508).")).test_client()).get_data(as_text=True)
    assert "No decision rule (the JECFA page read names it" in html
    assert "apps.who.int/food-additives-contaminants-jecfa-database" in html
    assert "Codex list" not in html and "Codex CXG" not in html


def test_browser_template_footer_and_help_cite_jecfa():
    t = (ROOT / "web_preview" / "template.html").read_text()
    assert "Codex CXG 36-1989" not in t and "The Codex list names this code" not in t
    assert "A JECFA database page that was read names this code" in t and "JECFA database page" in t
