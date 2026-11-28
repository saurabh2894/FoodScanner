"""Coverage gates for ambiguous section labels; see research/02 and research/06."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import parity_check as pc  # noqa: E402


BRACKET_ITEMS = [
    "Garlic Powder (Seasoning: Onion, salt)",
    "Garlic Powder [Seasoning: Onion, salt]",
    "Garlic Powder {Seasoning: Onion, salt}",
    "Mix (Seasoning: Onion, salt)",
    "Garlic Powder (Outer [Seasoning: Onion, salt])",
    "Garlic Powder (Seasoning: Onion)",
]
BRACKET_TEXTS = [f"Ingredients: Rice, {item}, salt." for item in BRACKET_ITEMS]
SQUARE = "Ingredients: Rice, Garlic Powder Seasoning: [Onion, salt]."
CURLY = "Ingredients: Rice, Garlic Powder Seasoning: Onion {cumin, salt}."
PLAIN = "Ingredients: Rice, Garlic Powder, onion, salt."
HEADING = "Ingredients: Seasoning: Onion, salt."
STRONG = "Ingredients: Rice, Garlic Powder Seasoning: Onion, maltodextrin."
DECLARED = "Ingredients: Rice, Garlic Powder Seasoning: Onion, salt. Contains added flavour."
BRACKET_STRONG = "Ingredients: Rice, Garlic Powder (Seasoning: Onion, salt), maltodextrin."
BRACKET_DECLARED = BRACKET_TEXTS[0] + " Contains added flavour."
TEXTS = BRACKET_TEXTS + [SQUARE, CURLY, PLAIN, HEADING, STRONG, DECLARED,
                         BRACKET_STRONG, BRACKET_DECLARED]


@pytest.fixture(scope="module", params=["python", "js"])
def results(request):
    pairs = [(text, source) for text in TEXTS for source in ("text", "ocr")]
    if request.param == "js":
        if not shutil.which("node"):
            pytest.skip("node is needed for the browser engine")
        values = pc.run_js(pairs)
    else:
        values = [pc.py_result(text, source) for text, source in pairs]
    return dict(zip(pairs, values))


@pytest.mark.parametrize("source", ["text", "ocr"])
@pytest.mark.parametrize("item,text", list(zip(BRACKET_ITEMS, BRACKET_TEXTS)))
def test_closed_bracket_colon_is_disclosed_and_blocks(results, source, item, text):
    result = results[text, source]
    assert not result["answered"]
    assert result["ingredients"] == ["Rice", item, "salt"]
    assert result["completeness"]["status"] == "uncertain"
    assert result["completeness"]["assessed"]["not_assessed"] >= 1
    assert any("Seasoning: Onion" in x and "not assessed separately" in x for x in result["unassessed"])
    assert any("bracketed label and contents" in x for x in result["warnings"])


@pytest.mark.parametrize("source", ["text", "ocr"])
@pytest.mark.parametrize("text", [SQUARE, CURLY])
def test_ambiguous_section_label_blocks(results, source, text):
    result = results[text, source]
    assert not result["answered"]
    assert result["completeness"]["status"] == "uncertain"
    assert "section label may not have been split" in result["reason"]


@pytest.mark.parametrize("source", ["text", "ocr"])
@pytest.mark.parametrize("text", [PLAIN, HEADING])
def test_unambiguous_food_lists_stay_group_three(results, source, text):
    result = results[text, source]
    assert result["answered"] and result["group"] == 3
    assert result["completeness"]["status"] == "complete"


@pytest.mark.parametrize("source", ["text", "ocr"])
@pytest.mark.parametrize("text", [STRONG, DECLARED, BRACKET_STRONG, BRACKET_DECLARED])
def test_strong_marker_survives_coverage_uncertainty(results, source, text):
    result = results[text, source]
    assert result["answered"] and result["group"] == 4
    assert result["completeness"]["status"] == "uncertain"
    assert result["warnings"]
