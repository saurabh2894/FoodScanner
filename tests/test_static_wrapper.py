"""The static-hosting build must carry its own document skeleton (doctype, lang, viewport, ...).

Regression for the review finding: the page was served without them, so phones laid it out at 980 px
in quirks mode. The artifact host adds a skeleton itself; an ordinary static host does not.
"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
_spec = importlib.util.spec_from_file_location("build_web_preview", ROOT / "scripts" / "build_web_preview.py")
build = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build)          # defines functions only; building needs main()

TEMPLATE = (ROOT / "web_preview" / "template.html").read_text(encoding="utf-8")
WRAPPED = build.wrap_for_static(TEMPLATE)


def test_wrapper_has_every_head_requirement():
    assert WRAPPED.startswith("<!doctype html>")
    assert '<html lang="en">' in WRAPPED
    assert '<meta charset="utf-8">' in WRAPPED
    assert 'name="viewport" content="width=device-width, initial-scale=1' in WRAPPED
    assert 'name="description"' in WRAPPED and 'rel="icon"' in WRAPPED
    assert "<title>Foodscan</title>" in WRAPPED


def test_head_and_body_are_split_where_expected():
    head, _, body = WRAPPED.partition("</head>")
    assert "<style>" in head and "</style>" in head and "<title>" in head
    assert '<div class="wrap">' in body and "<script" in body and "<style>" not in body
    assert WRAPPED.rstrip().endswith("</html>") and body.count("<body>") == 1


def test_artifact_only_tag_is_left_out_of_the_static_page():
    assert "claude:viewport-fit-sides" in TEMPLATE
    assert "claude:viewport-fit-sides" not in WRAPPED


def test_body_margin_is_reset_by_the_page_itself():
    assert "body { margin: 0;" in TEMPLATE
