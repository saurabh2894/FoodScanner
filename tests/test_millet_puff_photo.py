"""End to end on a REAL photo (tests/fixtures/millet_puff_label.jpg), the case that showed 'Not enough information'.

The photo has "Puff 88%:" and "Seasoning 12%:" section labels with percentages; before the fix the list ended
at the full stop after "Rice Bran Oil(16%)." and the flavour marker in the seasoning was never seen.
"""
import shutil
from pathlib import Path

import pytest

from foodscan.pipeline import analyse_image
from foodscan.web.app import create_app

PHOTO = Path(__file__).parent / "fixtures" / "millet_puff_label.jpg"
needs_tesseract = pytest.mark.skipif(shutil.which("tesseract") is None, reason="tesseract not installed")


@pytest.mark.ocr
@needs_tesseract
def test_real_photo_is_group4_with_sections():
    a = analyse_image(PHOTO)
    assert a.answered and a.group == 4, a.reason
    assert [label for label, _ in a.sections] == ["Puff 88%", "Seasoning 12%"]
    assert any("Flavours" in d.ingredient and d.section == "Seasoning 12%" for d in a.drivers)
    assert {"330", "296", "334", "508", "392"} <= {u.code for u in a.ins_mappings}
    assert any(u.startswith("Amchur") for u in a.unassessed)


class _FakeOcr:
    def __init__(self, text):
        self.text = text

    def extract_text(self, p):
        return self.text


def test_flask_page_shows_sections_and_not_assessed():
    from test_review_labels import MILLET_PUFF

    client = create_app(_FakeOcr(MILLET_PUFF)).test_client()
    import io
    r = client.post("/", data={"photo": (io.BytesIO(b"x"), "label.png")}, content_type="multipart/form-data")
    html = r.get_data(as_text=True)
    assert "NOVA group 4" in html and "Seasoning 12%" in html and "Puff 88%" in html
    assert "Not assessed" in html and "Amchur" in html
    assert "Seasoning 12%)" in html            # driver is tagged with its section
