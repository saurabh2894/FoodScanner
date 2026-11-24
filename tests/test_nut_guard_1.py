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


def test_synthetic_all_27_nut_seed_rows_are_covered():
    # clause-named-24 adds hemp seed and hemp seeds; nalt-names-7/11 add separately sourced plain peanut and shea nuts to every existing nut-condition guard.
    assert "peanut" in ROWS
    assert len(ROWS) == 27 and {"almonds", "pumpkin seeds", "flax seeds", "walnuts", "cashew nuts", "shea nuts"} <= set(ROWS)


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


def reason(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return a.reason


def test_synthetic_nut_reasons_name_nuts_and_cite_the_general_group_3_definition_only():
    r = reason("Almonds (canned)")
    assert r.startswith("a canned, bottled or preserved nut or seed (") and "legume" not in r and "vegetable" not in r and "brine and fruit in syrup" not in r
    assert "Group 3 definition covers group 1 foods with salt, oil, sugar or other group 2 ingredients added" in r and "added substances are not established" in r
    r = reason("Walnuts (XQ9)")
    assert r.startswith("a bracket on a nut or seed item names content the vocabulary does not recognise") and "legume" not in r


def test_synthetic_mixed_lists_use_kind_neutral_reasons():
    assert reason("Almonds (XQ9), Rice (XQ9)").startswith("a bracket on a food item names content")
    assert reason("Almonds (canned), Kidney Beans (canned)").startswith("a canned, bottled or preserved food (")


def test_synthetic_existing_kind_reasons_are_unchanged_text():
    assert reason("kidney beans (canned)") == ("a canned, bottled or preserved legume, vegetable or fruit (kidney beans (canned)): FAO Group 3 names vegetables and legumes preserved in brine and fruit in syrup, "
                                              "but the item does not say that salt, sugar, syrup or brine is added, so neither Group 1 nor Group 3 is established")
    assert reason("rice (XQ9)").startswith("a bracket on a legume, vegetable, fruit or flour item names content the vocabulary does not recognise (rice (XQ9): xq9)")


def driver(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    assert a.group == 3
    return a.drivers[0].detail


GENERAL = "FAO Table 1 Group 3 definition: 'Products made by adding salt, oil, sugar or other group 2 ingredients to group 1 foods'; class-instance of that rule, no FAO example names this form)"


def test_synthetic_group_3_drivers_name_the_observed_added_substance():
    assert driver("Walnuts (brine)") == "nut or seed with added brine (" + GENERAL
    assert driver("Walnuts (sunflower oil)") == "nut or seed with added sunflower oil (" + GENERAL
    assert driver("Walnuts (honey)") == "nut or seed with added honey (" + GENERAL
    assert driver("Almonds (salt, sunflower oil)") == "nut or seed with added salt, sunflower oil (" + GENERAL
    # salt or sugar only: the FAO example 'salted or sugared nuts and seeds' fits and stays quoted
    for t in ("Walnuts (salted)", "Walnuts (sugar)", "Salted Walnuts", "Walnuts, Salt".replace(", Salt", " (salt)")):
        assert driver(t) == "nut or seed with added salt or sugar (FAO Table 1 Group 3: 'salted or sugared nuts and seeds')", t
