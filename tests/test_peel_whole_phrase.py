"""peel-known-phrase-1 (W): when the whole text before the colon is already a recognised ingredient name, it is the name, never name + section label.

Before: "Corn Oil: x" became the ingredient "Corn" plus a section "Oil" (61 of the 423 multi-word lexicon terms did this, in both engines). Every existing guard stays in front of this one.
The last test pins a documented OPEN ITEM, not a fix: a known prefix followed by a non-form tail that is part of a product name ("Paprika Oleoresin (0.6%): ...") still peels.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest

from foodscan.classify import lexicon
from foodscan.parser import _peel_label, parse_ingredient_list
from scripts import parity_check as pc

NO_PEEL = ["Corn Oil: Onion", "Moong Dal: Roasted", "Milk Solids: Skimmed Milk", "Rice Flour: Rice, Water", "Roasted Barley Flour: Wheat", "Coriander Leaf: Fresh",
           "Oyster Mushrooms: Garlic", "Mustard Greens: Salt", "Wheat Flour (45%): Wheat", "Wheat Flour 45%: Wheat", "Vitamins and Minerals: Iron, Zinc", "Tomato Concentrate: Tomato",
           "Rice Flours: Wheat", "Corn Oil: Onion: Garlic", "Corn Oil 12%: Onion", "Dried Moong Dal: Roasted", "Mystery Corn Oil: Onion"]
STILL_PEEL = [("Corn Oil Seasoning : Onion", ("Corn Oil", "Seasoning", "Onion")), ("Milk Solids Seasoning : Onion", ("Milk Solids", "Seasoning", "Onion")),
              ("Moong Dal Seasoning (12%): Onion", ("Moong Dal", "Seasoning 12%", "Onion")), ("Rice Bran Oil Seasoning : Onion", ("Rice Bran Oil", "Seasoning", "Onion"))]


@pytest.mark.parametrize("item", NO_PEEL)
def test_recognised_whole_name_is_not_split(item):
    assert _peel_label(item) is None


@pytest.mark.parametrize("item,expected", STILL_PEEL)
def test_name_plus_real_section_label_still_peels(item, expected):
    assert _peel_label(item) == expected


def test_every_multi_word_lexicon_term_stays_whole_before_a_colon():
    bad = [t for t in sorted(lexicon()) if " " in t and _peel_label(f"{t.title()}: Roasted Sesame")]
    assert bad == []                                       # was 61 terms before this rule


def test_bracketed_sub_list_with_a_whole_name_colon_keeps_the_item_whole():
    p = parse_ingredient_list("Ingredients: Rice, Corn Oil: Onion (Moong Dal: Roasted), salt.")
    assert "Corn Oil: Onion (Moong Dal: Roasted)" in p.items and [s.label for s in p.sections] == [None]


def test_open_item_known_prefix_plus_non_form_tail_still_peels():
    # OPEN ITEM (documented in evaluation/peel_known_phrase_1/README.md): "Paprika" is known, "Oleoresin" is neither a form word nor a lexicon term, and the whole phrase is not a recognised name.
    assert _peel_label("Paprika Oleoresin (0.6%): Roasted Sesame") == ("Paprika", "Oleoresin 0.6%", "Roasted Sesame")


@pytest.mark.skipif(shutil.which("node") is None, reason="node is needed to run the browser engine")
@pytest.mark.parametrize("item", NO_PEEL + [i for i, _ in STILL_PEEL] + ["Paprika Oleoresin (0.6%): Roasted Sesame"])
def test_python_and_js_agree(item):
    text = "Ingredients: Rice, " + item + ", salt."
    assert pc.py_result(text, "text") == pc.run_js([(text, "text")])[0]
