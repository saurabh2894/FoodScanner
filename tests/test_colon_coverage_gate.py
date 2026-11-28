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
QUANTITY_POSITIVES = [
    "Ingredients: Rice: 60%, salt.",
    "Ingredients: Rice: 60 %, salt.",
    "Ingredients: Sugar: 20%, Rice, Salt.",
    "Ingredients: Rice: 30 g, salt.",
]
SUGAR_QUANTITY = "Ingredients: Sugar: 20%, Salt."
WHEAT_QUANTITIES = "Ingredients: Wheat flour: 50%, Sugar: 20%, Salt."
SECTION_NEGATIVE = "Ingredients: Rice, Garlic Powder Seasoning: Onion, salt."
QUANTITY_TEXT_NEGATIVE = "Ingredients: Rice: 60% wheat, salt."
QUANTITY_STRONG = "Ingredients: Rice: 60% wheat, maltodextrin."
NESTED_STRONG = "Ingredients: Rice, Garlic Powder (Seasoning: Onion, salt), maltodextrin."
TEXTS = BRACKET_TEXTS + [SQUARE, CURLY, PLAIN, HEADING, STRONG, DECLARED,
                         BRACKET_STRONG, BRACKET_DECLARED, *QUANTITY_POSITIVES,
                         SUGAR_QUANTITY, WHEAT_QUANTITIES, SECTION_NEGATIVE,
                         QUANTITY_TEXT_NEGATIVE, QUANTITY_STRONG, NESTED_STRONG]


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


@pytest.mark.parametrize("source", ["text", "ocr"])
@pytest.mark.parametrize("text", QUANTITY_POSITIVES)
def test_bare_quantity_colons_do_not_block_classifiable_ingredients(results, source, text):
    result = results[text, source]
    assert result["answered"] and result["group"] == 3
    assert "section label may not have been split" not in result["completeness"]["reasons"]
    assert not any("section label may not have been split" in warning for warning in result["warnings"])


@pytest.mark.parametrize("source", ["text", "ocr"])
@pytest.mark.parametrize("text", [SUGAR_QUANTITY, WHEAT_QUANTITIES])
def test_quantity_colons_do_not_override_existing_classification_abstentions(results, source, text):
    result = results[text, source]
    assert not result["answered"]
    assert "section label may not have been split" not in result["reason"]
    assert not any("section label may not have been split" in reason for reason in result["completeness"]["reasons"])
    if text == SUGAR_QUANTITY:
        assert "combination does not match" in result["reason"]
    else:
        assert "flour-based list" in result["reason"]


@pytest.mark.parametrize("source", ["text", "ocr"])
def test_quantity_followed_by_ingredient_text_still_hits_the_gate(results, source):
    for text in (SECTION_NEGATIVE, QUANTITY_TEXT_NEGATIVE):
        result = results[text, source]
        assert not result["answered"]
        assert any("section label may not have been split" in reason for reason in result["completeness"]["reasons"])
        assert any("section label may not have been split" in warning for warning in result["warnings"])


@pytest.mark.parametrize("source", ["text", "ocr"])
@pytest.mark.parametrize("text", [QUANTITY_STRONG, NESTED_STRONG])
def test_strong_marker_still_survives_quantity_or_nested_colon_uncertainty(results, source, text):
    result = results[text, source]
    assert result["answered"] and result["group"] == 4
    if text == QUANTITY_STRONG:
        assert any("section label may not have been split" in reason for reason in result["completeness"]["reasons"])
    else:
        assert any("bracketed label and contents" in warning for warning in result["warnings"])
