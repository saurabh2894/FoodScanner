"""Minimal local web page. Binds to 127.0.0.1 only; no accounts, no network calls.

Calls the same pipeline as the CLI. The uploaded photo is written to a temp
file for OCR and deleted straight after.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

from flask import Flask, render_template, request

from ..display import colon_quantity_display, ingredient_display
from ..ocr import OcrEngine, OcrUnavailable, TesseractOcr
from ..pipeline import analyse_image

ALLOWED = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
HOST = "127.0.0.1"


def create_app(ocr: OcrEngine | None = None) -> Flask:
    app = Flask(__name__)
    app.jinja_env.filters["ingredient_display"] = ingredient_display
    app.jinja_env.filters["colon_quantity_display"] = colon_quantity_display
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB
    engine = ocr or TesseractOcr()

    @app.get("/")
    def index():
        return render_template("index.html", result=None, error=None)

    @app.post("/")
    def upload():
        f = request.files.get("photo")
        if f is None or not f.filename:
            return render_template("index.html", result=None, error="Choose a label photo first."), 400
        suffix = Path(f.filename).suffix.lower()
        if suffix not in ALLOWED:
            return render_template("index.html", result=None, error="Unsupported file type. Upload a PNG, JPG, WEBP, BMP or TIFF photo."), 400
        fd, tmp = tempfile.mkstemp(suffix=suffix)
        try:
            with os.fdopen(fd, "wb") as out:
                f.save(out)
            result = analyse_image(tmp, engine)
        except OcrUnavailable as exc:
            return render_template("index.html", result=None, error=str(exc)), 503
        except Exception:  # unreadable / corrupt image
            return render_template("index.html", result=None, error="Could not read that file as an image."), 400
        finally:
            try:
                os.unlink(tmp)
            except OSError:
                pass
        return render_template("index.html", result=result, error=None)

    @app.errorhandler(413)
    def too_large(_):
        return render_template("index.html", result=None, error="File too large (limit 10 MB)."), 413

    return app


def main() -> None:
    create_app().run(host=HOST, port=5000, debug=False)


if __name__ == "__main__":
    main()
