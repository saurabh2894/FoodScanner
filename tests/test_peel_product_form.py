"""peel-known-phrase-1, product-form tails: text before a depth-0 colon that is a recognised phrase plus words naming a product form (seasoning, sauce, mix, ...) is NOT peeled and the word
is NOT dropped: the whole text stays one item, is flagged, and the result abstains. Peeling needs every tail word to be a known plain label word; the data holds none (empty allowlist).
Python and JS must agree (parity is agreement on the abstention). Never a more confident result than the pre-peel base.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest

from foodscan.parser import _KNOWN_LABEL_WORDS, _PRODUCT_FORM_WORDS, _peel_label, parse_ingredient_list
from foodscan.pipeline import analyse_text
from scripts import parity_check as pc

PREFIXES = ["Garlic Powder", "Red chilli powder", "Dried Paprika", "Rice Bran Oil", "Corn Oil", "Turmeric", "Bishop’s Seed", "Roasted Rice", "Salt", "Milk Solids"]
TAILS = ["Seasoning", "SEASONING", "seasonings", "Sauce", "Soup", "Mix", "Premix", "Blend", "Paste", "Masala", "Tastemaker", "Topping", "Sprinkler", "Garnish", "Filling", "Coating", "Glaze",
         "Dressing", "Base", "Concentrate", "Extract", "Oleoresin", "Syrup", "Noodles", "Puff"]


@pytest.mark.parametrize("tail", TAILS)
def test_every_product_form_word_blocks_the_peel_after_every_kind_of_known_prefix(tail):
    for pre in PREFIXES:
        assert _peel_label(f"{pre} {tail} : Onion") is None, (pre, tail)
        assert _peel_label(f"{pre} {tail} (12%): Onion") is None, (pre, tail)
        assert _peel_label(f"{pre} {tail} 12%: Onion") is None, (pre, tail)


def test_product_form_word_anywhere_in_a_multi_word_tail_blocks_it():
    assert _peel_label("Rice Bran Oil Hot Masala Seasoning : Onion") is None
    assert _peel_label("Rice Bran Oil Masala Tastemaker : Onion") is None


def test_unknown_tail_words_are_never_peeled_either():
    for tail in ("Zorba", "Mystery", "Fancy Zorba", "Q"):
        assert _peel_label(f"Rice Bran Oil {tail} : Onion") is None


def test_the_allowlist_of_known_label_words_is_empty_by_evidence_and_disjoint_from_product_forms():
    assert _KNOWN_LABEL_WORDS == frozenset() and not (_KNOWN_LABEL_WORDS & _PRODUCT_FORM_WORDS)


def test_product_form_words_are_each_traceable_to_a_source():
    rule = json.loads((REPO_ROOT / "data" / "ingest" / "clause_tier1_herbs_spices.json").read_text(encoding="utf-8"))
    from_rule = set(rule["processed_words"]["words"]) & _PRODUCT_FORM_WORDS
    assert {"seasoning", "mix", "sauce", "paste", "blend", "extract", "syrup"} <= from_rule      # data/ingest rule file, processed_words
    from_labels = {"seasoning", "sauce", "soup", "noodles", "puff", "topping", "sprinkler", "masala", "tastemaker", "coating", "oleoresin"}    # section labels in saved real labels / the parity corpus
    from_review = {"garnish", "filling", "glaze", "dressing", "base", "concentrate", "premix"}                                                # reviewer-listed (not in the data)
    assert _PRODUCT_FORM_WORDS == from_rule | from_labels | from_review, sorted(_PRODUCT_FORM_WORDS ^ (from_rule | from_labels | from_review))


@pytest.mark.parametrize("item", ["Garlic Powder Seasoning : Onion", "Red chilli powder Seasoning : Onion", "Corn Oil Sauce : Onion", "Rice Bran Oil Seasoning : Onion"])
def test_the_word_is_not_dropped_and_the_result_abstains_or_is_flagged(item):
    t = "Ingredients: Rice, " + item + ", salt."
    p = parse_ingredient_list(t)
    assert item in p.items and [s.label for s in p.sections] == [None]
    a = analyse_text(t, source="text")
    assert not a.answered and a.completeness["status"] == "uncertain"
    assert any("section label may not have been split" in w for w in a.warnings)


def test_nested_and_multi_colon_shapes_keep_the_word_and_never_split():
    for item in ("Garlic Powder Seasoning : Onion : Garlic", "Garlic Powder Seasoning: Masala: Onion", "Garlic Powder Seasoning : Onion (Red Chilli Powder Sauce : Salt)",
                 "GARLIC POWDER SEASONING (12%): ONION", "garlic powder Seasoning 5%: onion", "Bishop’s Seed Seasoning (5%): Onion"):
        p = parse_ingredient_list("Ingredients: Rice, " + item + ", salt.")
        assert item in p.items and [s.label for s in p.sections] == [None], item


@pytest.mark.skipif(shutil.which("node") is None, reason="node is needed to run the browser engine")
@pytest.mark.parametrize("item", ["Garlic Powder Seasoning : Onion", "Red chilli powder Sauce : Onion", "Corn Oil Seasoning (12%): Onion", "Bishop’s Seed Masala 5%: Onion",
                                  "Garlic Powder Seasoning : Onion : Garlic", "Garlic Powder Seasoning: Masala: Onion", "Garlic Powder Seasoning : Onion (Red Chilli Powder Sauce : Salt)",
                                  "GARLIC POWDER SEASONING (12%): ONION", "Rice Bran Oil Hot Masala Seasoning : Onion", "Rice Bran Oil Zorba : Onion", "Red Chilli Powders Seasonings : Onion"])
def test_python_and_js_agree_and_both_abstain(item):
    t = "Ingredients: Rice, " + item + ", salt."
    py, js = pc.py_result(t, "text"), pc.run_js([(t, "text")])[0]
    assert py == js and not py["answered"]
