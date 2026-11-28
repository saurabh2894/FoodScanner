"""One shared "known prefix" rule for parser._peel_label, in Python and in the JS port (web_preview/foodscan.js, the engine that runs in production).

History: Python used exact lexicon/marker terms only, JS used lookup() (exact, plural, descriptor-stripped, kind-scoped descriptor). They diverged on "Red chilli powder Seasoning : Onion" and
similar (strict-xfail probes, removed now). `lookup()` has NO synonym path in either engine: the old description of JS as "synonym-aware" was wrong. A second source of divergence was the
curly apostrophe (JS flatten and normalise.flatten read it as a straight one, parser._flat did not): "Bishop’s Seed Seasoning : Onion".
The probes are in scripts/parity_check.py (all 37,329+ pairs identical); this file pins the Python behaviour and the Python/JS agreement for them directly.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest

from foodscan.parser import _flat, _known_phrase, _peel_label
from scripts import parity_check as pc

PEELS = [
    ("Dried Paprika Seasoning: Onion", ("Dried Paprika", "Seasoning", "Onion")),
    ("Paprika Powder Seasoning: Onion", ("Paprika Powder", "Seasoning", "Onion")),
    ("Garlic Powder Seasoning : Onion", ("Garlic Powder", "Seasoning", "Onion")),
    ("Red chilli powder Seasoning : Onion", ("Red chilli powder", "Seasoning", "Onion")),
    ("Dry ginger powder Seasoning : Onion", ("Dry ginger powder", "Seasoning", "Onion")),
    ("Bishop’s Seed Seasoning : Onion", ("Bishop’s Seed", "Seasoning", "Onion")),
    ("Red Chilli Powders Seasoning : Onion", ("Red Chilli Powders", "Seasoning", "Onion")),
    ("Roasted Rice Seasoning (12%): Onion", ("Roasted Rice", "Seasoning 12%", "Onion")),
]
KEPT = ["Mystery Powder Seasoning : Onion", "Mystery Dried Paprika Seasoning : Onion", "Garlic Powder Flavour : Onion", "Garlic Powder Note: Onion", "Toasted Milk Seasoning : Onion",
        "Dried Paprika Seasoning :", "Dried Paprika Seasoning : 12%"]


@pytest.mark.parametrize("item,expected", PEELS)
def test_known_prefix_forms_peel_the_section_label(item, expected):
    assert _peel_label(item) == expected


@pytest.mark.parametrize("item", KEPT)
def test_unknown_prefix_or_guarded_label_is_never_peeled(item):
    assert _peel_label(item) is None


def test_curly_and_straight_apostrophe_flatten_alike():
    assert _flat("Bishop’s Seed") == _flat("Bishop's Seed") == "bishop's seed"
    assert _known_phrase(_flat("Bishop’s Seed"))


@pytest.mark.skipif(shutil.which("node") is None, reason="node is needed to run the browser engine")
@pytest.mark.parametrize("item", [i for i, _ in PEELS] + KEPT)
def test_python_and_js_agree(item):
    text = "Ingredients: Rice, " + item + ", salt."
    assert pc.py_result(text, "text") == pc.run_js([(text, "text")])[0]
