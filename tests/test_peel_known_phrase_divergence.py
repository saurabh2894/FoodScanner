"""Pinned, known Python/JS divergence (release-relevant: the JS port in web_preview/foodscan.js is what runs in production, Python is the source of truth).

`known phrase` in the peel-label heuristic: Python (parser._known_phrase) accepts exact lexicon/marker terms only; JS (knownPhrase) accepts anything isRecognised
(descriptor-stripped, plural- and synonym-aware). So JS peels "Garlic Powder Seasoning : Onion" into "Garlic Powder" + section "Seasoning" while Python keeps the item whole and
flags it. The four texts below are SYNTHETIC probes, deliberately NOT in scripts/parity_check.py's corpus (that corpus must stay all-identical).
Each is xfail(strict): the day Python and JS agree the test turns red, and the marker must be removed (and the text moved into the parity corpus).
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest

from scripts import parity_check as pc

PROBES = [
    "Ingredients: Rice, Dried Paprika Seasoning: Onion, salt.",
    "Ingredients: Rice, Paprika Powder Seasoning: Onion, salt.",
    "Ingredients: Rice, Chilli Powder Seasoning : Onion, salt.",
    "Ingredients: Rice, Garlic Powder Seasoning : Onion, salt.",
]


@pytest.mark.skipif(shutil.which("node") is None, reason="node is needed to run the browser engine")
@pytest.mark.xfail(strict=True, reason="KNOWN DIVERGENCE: JS peels a section label after any isRecognised prefix, Python only after an exact lexicon/marker term. Fix = one shared rule, decided by the owner.")
@pytest.mark.parametrize("text", PROBES)
def test_synthetic_python_and_js_agree_on_a_label_after_a_descriptor_form_prefix(text):
    js = pc.run_js([(text, "text")])[0]
    assert pc.py_result(text, "text") == js
