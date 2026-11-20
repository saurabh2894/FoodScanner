import shutil

import pytest

from foodscan import ocr


def test_missing_tesseract_gives_clear_error(monkeypatch, tmp_path):
    import pytesseract

    def boom():
        raise pytesseract.TesseractNotFoundError()

    monkeypatch.setattr(pytesseract, "get_tesseract_version", boom)
    with pytest.raises(ocr.OcrUnavailable, match="Tesseract OCR is not installed"):
        ocr.TesseractOcr().extract_text(tmp_path / "x.png")


def test_engine_is_swappable():
    class Fake:
        def extract_text(self, image_path):
            return "Ingredients: Salt."

    engine: ocr.OcrEngine = Fake()
    assert engine.extract_text("any") == "Ingredients: Salt."


@pytest.mark.ocr
@pytest.mark.skipif(shutil.which("tesseract") is None, reason="tesseract not installed")
def test_real_tesseract_reads_rendered_text(tmp_path):
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (900, 120), "white")
    font = ImageFont.load_default(size=40)
    ImageDraw.Draw(img).text((20, 30), "Ingredients: Salt, Sugar.", fill="black", font=font)
    p = tmp_path / "t.png"
    img.save(p)
    assert "salt" in ocr.TesseractOcr().extract_text(p).lower()
