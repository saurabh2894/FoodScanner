import io
import re

from foodscan.ocr import OcrUnavailable
from foodscan.web.app import HOST, create_app


class FakeOcr:
    def __init__(self, text):
        self.text = text

    def extract_text(self, p):
        return self.text


def post(client, name="label.png", data=b"x"):
    return client.post("/", data={"photo": (io.BytesIO(data), name)}, content_type="multipart/form-data")


def test_binds_to_localhost_only():
    assert HOST == "127.0.0.1"


def test_index_renders():
    r = create_app(FakeOcr("")).test_client().get("/")
    assert r.status_code == 200 and b"Upload a photo" in r.data


def test_answer_shows_ingredients_group_and_drivers():
    text = "Ingredients: Sugar, maltodextrin, emulsifier (INS 471), salt."
    r = post(create_app(FakeOcr(text)).test_client())
    html = r.get_data(as_text=True)
    assert "NOVA group 4" in html and "maltodextrin" in html and "INS 471" in html
    assert "Extracted ingredients" in html


def test_abstention_shows_reason_and_no_group():
    r = post(create_app(FakeOcr("Ingredients: Sugar, refined wheat flo")).test_client())
    html = r.get_data(as_text=True)
    assert "Not enough information" in html and "truncated" in html and not re.search(r"NOVA group \d", html)


def test_no_health_judgement_words_in_page():
    for text in ["Ingredients: Sugar, maltodextrin, salt.", "Ingredients: Whole wheat flour."]:
        html = post(create_app(FakeOcr(text)).test_client()).get_data(as_text=True).lower()
        assert not any(w in html for w in ("healthy", "unhealthy", "should not be eaten", "bad for you"))


def test_escapes_html_in_ocr_text():
    r = post(create_app(FakeOcr("Ingredients: <script>alert(1)</script>, salt.")).test_client())
    assert b"<script>alert(1)</script>" not in r.data


def test_rejects_non_image_and_missing_file():
    c = create_app(FakeOcr("")).test_client()
    assert post(c, name="evil.exe").status_code == 400
    assert c.post("/", data={}, content_type="multipart/form-data").status_code == 400


def test_missing_tesseract_shows_clear_error():
    class Broken:
        def extract_text(self, p):
            raise OcrUnavailable("Tesseract OCR is not installed")

    r = post(create_app(Broken()).test_client())
    assert r.status_code == 503 and b"Tesseract OCR is not installed" in r.data


def test_temp_file_deleted(tmp_path):
    seen = []

    class Spy:
        def extract_text(self, p):
            seen.append(p)
            return "Ingredients: Whole wheat flour."

    post(create_app(Spy()).test_client())
    import os
    assert seen and not os.path.exists(seen[0])



def test_additive_codes_are_grouped_with_plain_effect_labels(monkeypatch):
    import csv
    from pathlib import Path
    from foodscan import normalise
    ref = Path(__file__).resolve().parent.parent / 'data/pending/ins_reference.csv'
    monkeypatch.setattr(normalise, '_ins_reference', lambda: {normalise.canonical_code(r['ins']): r for r in csv.DictReader(ref.open(encoding='utf-8'))})
    text = "Ingredients: Rice, Acidity Regulators(INS330, INS296), colour (INS 102), preservative (INS 211), salt."
    html = post(create_app(FakeOcr(text)).test_client()).get_data(as_text=True)
    assert "Additive codes" in html and "4 found: 2 with a decision rule, 2 without." in html
    assert "Acidity Regulators" in html and "Ultra-processing marker" in html and "Not a marker by itself" in html
    assert "No decision rule" in html and "possible functions from the Codex list" in html
    assert "not confirmed for this product" in html and "Name not in the table yet" not in html
    assert "INS numbers" not in html
