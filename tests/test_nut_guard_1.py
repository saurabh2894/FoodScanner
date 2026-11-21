"""nut-guard-1 (SYNTHETIC): the canned/bottled/preserved, brine and unrecognised-bracket guards of the legume, vegetable and fruit kinds also apply to kind nut_seed (all 23 nut_seed rows).
Before: 'Almonds (brine)', 'Almonds (canned)' and 'Almonds (XQ9)' answered Group 1. Same item-level reading (the item's own name and bracket); plain, roasted, salted/sugared forms are unchanged."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
ROWS = [r["term"] for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline="")) if r["kind"] == "nut_seed"]


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return a.group if a.answered else None


def test_synthetic_all_23_nut_seed_rows_are_covered():
    assert len(ROWS) == 23 and {"almonds", "pumpkin seeds", "flax seeds", "walnuts", "cashew nuts"} <= set(ROWS)


@pytest.mark.parametrize("t", ROWS)
def test_synthetic_canned_preserved_and_unknown_bracket_abstain(t):
    for f in ("{x} (canned)", "{x} (bottled)", "{x} (preserved)", "{x} (XQ9)"):
        assert g(f.format(x=t)) is None, f.format(x=t)


@pytest.mark.parametrize("t", ROWS)
def test_synthetic_brine_oil_salt_and_sugar_in_the_item_are_group_3(t):
    for f in ("{x} (brine)", "{x} (in brine)", "{x} (sunflower oil)", "{x} (salted)", "{x} (sugar)", "salted {x}", "{x}, salt"):
        assert g(f.format(x=t)) == 3, f.format(x=t)


@pytest.mark.parametrize("t", ROWS)
def test_synthetic_plain_and_benign_forms_keep_group_1(t):
    for f in ("{x}", "roasted {x}", "{x} (raw)", "{x} (whole)", "{x} (dried)", "{x} (peeled)", "{x} (cooked)", "{x} (no added salt)"):
        assert g(f.format(x=t)) == 1, f.format(x=t)


def test_synthetic_other_kinds_are_unchanged():
    assert g("Kidney Beans (canned)") is None and g("Rice (XQ9)") is None and g("Mango (preserved)") is None
