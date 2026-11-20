"""Text extraction from a label photo.

OCR sits behind the OcrEngine protocol so a vision model can replace it later
without touching the parser or classifier.
"""
from __future__ import annotations

from pathlib import Path
from typing import Protocol


class OcrUnavailable(RuntimeError):
    """The OCR backend cannot run (e.g. tesseract binary not installed)."""


class OcrEngine(Protocol):
    def extract_text(self, image_path: str | Path) -> str: ...


INSTALL_HINT = (
    "Tesseract OCR is not installed or not on PATH. Install it: "
    "macOS `brew install tesseract`; Debian/Ubuntu `apt install tesseract-ocr`; "
    "Windows: UB Mannheim installer (https://github.com/UB-Mannheim/tesseract/wiki), "
    "ticking English language data."
)


class TesseractOcr:
    def __init__(self, lang: str = "eng"):
        self.lang = lang

    def extract_text(self, image_path: str | Path) -> str:
        try:
            import pytesseract
            from PIL import Image
        except ImportError as exc:  # pragma: no cover
            raise OcrUnavailable(f"Missing Python dependency: {exc.name}") from exc
        try:
            pytesseract.get_tesseract_version()
        except pytesseract.TesseractNotFoundError as exc:
            raise OcrUnavailable(INSTALL_HINT) from exc
        with Image.open(image_path) as img:
            return pytesseract.image_to_string(img.convert("L"), lang=self.lang)
