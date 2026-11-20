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


TARGET_WIDTH = 1000   # tesseract reads label text poorly below roughly this width
MAX_UPSCALE = 4


def prepare_image(img):
    """Greyscale; upscale small photos (Lanczos), then stretch contrast and sharpen.

    Found on a real 239x167 label: raw OCR was unreadable, 4x upscaling read it
    almost perfectly. Images already >= TARGET_WIDTH are only greyscaled.
    """
    from PIL import ImageFilter, ImageOps

    img = img.convert("L")
    if img.width >= TARGET_WIDTH:
        return img
    factor = min(MAX_UPSCALE, max(2, round(TARGET_WIDTH / img.width)))
    img = img.resize((img.width * factor, img.height * factor), resample=3)  # 3 = Image.LANCZOS
    return ImageOps.autocontrast(img).filter(ImageFilter.SHARPEN)


def flatten_lighting(img):
    """Second reading for photos that did not read cleanly: divide by the local mean (uneven lighting, glare), stretch the
    1st-99th percentile, no sharpening. Mirrors the browser's "flat" pass. Falls back to prepare_image without numpy."""
    from PIL import Image

    try:
        import numpy as np
    except ImportError:  # pragma: no cover
        return prepare_image(img)
    g = img.convert("L")
    if max(g.size) > 2400:
        s = 2400 / max(g.size)
        g = g.resize((round(g.width * s), round(g.height * s)), resample=3)
    a = np.asarray(g, dtype=float)
    r = max(8, int(min(a.shape) / 30))
    h, w = a.shape
    c = np.pad(a, ((r + 1, r), (r + 1, r)), mode="edge").cumsum(0).cumsum(1)
    mean = (c[2 * r + 1:, 2 * r + 1:] - c[:h, 2 * r + 1:] - c[2 * r + 1:, :w] + c[:h, :w]) / ((2 * r + 1) ** 2)
    flat = np.clip(a / np.maximum(mean, 1) * 128, 0, 255)
    lo, hi = np.percentile(flat, 1), np.percentile(flat, 99)
    return Image.fromarray(np.clip((flat - lo) * 255 / max(hi - lo, 1), 0, 255).astype("uint8"))


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
            return pytesseract.image_to_string(prepare_image(img), lang=self.lang)

    def extract_text_alt(self, image_path: str | Path) -> str:
        """The second, lighting-corrected reading (see flatten_lighting)."""
        import pytesseract
        from PIL import Image

        with Image.open(image_path) as img:
            return pytesseract.image_to_string(flatten_lighting(img), lang=self.lang)
