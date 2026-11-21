"""provenance-fixes-1: the FAO nuts/seeds condition '(with no added salt or sugar)' is applied AT ITEM LEVEL (SYNTHETIC cases; negative tests both ways).
Group 3 of the same table covers 'salted or sugared nuts and seeds'; the condition is about the nuts, not about the product they sit in."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from foodscan.classify import nut_added_salt_or_sugar
from foodscan.normalise import normalise_ingredient
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
LEX = {r["term"]: r for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return (a.group if a.answered else None), a


@pytest.mark.parametrize("t", ["almonds", "pumpkin seeds", "flax seeds"])
def test_synthetic_nut_seed_rows_keep_the_placement_and_record_the_condition_in_provenance(t):
    r = LEX[t]
    assert r["kind"] == "nut_seed" and "(with no added salt or sugar)" in r["source"] and "CONDITION KEPT" in r["source"] and "AT ITEM LEVEL" in r["source"] and "exact term not named by the clause" in r["source"] and "provenance_audit_1" in r["source"]
    assert g(t.title())[0] == 1                                                    # the placement is kept


@pytest.mark.parametrize("t", ["Salted Almonds", "Almonds (Almonds, Salt)", "Almonds, Salt", "Rice, Salted Pumpkin Seeds", "Flax Seeds (Flax Seeds, Sugar)", "Almonds (with salt)"])
def test_synthetic_negative_an_item_whose_own_name_or_bracket_adds_salt_or_sugar_never_takes_group_1_via_the_nut_clause(t):
    group, a = g(t)
    assert group == 3 and not any(d.detail == "single recognised unprocessed food" for d in a.drivers), (t, group)


@pytest.mark.parametrize("t", ["Unsalted Almonds", "Almonds (no added salt)", "Almonds (salt free)", "Pumpkin Seeds (Roasted)", "Almonds (Roasted)", "Flax Seeds (Organic)"])
def test_synthetic_conditions_that_are_met_or_irrelevant_keep_group_1(t):
    assert g(t)[0] == 1


@pytest.mark.parametrize("t", ["Sugared Almonds", "Honey Roasted Almonds"])
def test_synthetic_forms_outside_the_vocabulary_never_get_group_1(t):
    assert g(t)[0] != 1


def test_synthetic_negative_a_plain_almonds_entry_inside_a_sweetened_product_does_not_lose_its_placement():
    a = analyse_text("Ingredients: Wheat Flour, Sugar, Almonds, Butter.", source="text")
    from foodscan.pipeline import _expand
    ings = _expand([("Almonds", None)])
    assert not nut_added_salt_or_sugar(ings[0])                                       # the product's sugar is not added to the nuts
    group, a2 = g("Rice, Sugar, Almonds")
    assert group == 3 and any(d.ingredient == "Almonds" and d.detail == "recognised whole food" for d in a2.drivers)


def test_synthetic_a_nut_condition_is_never_read_from_a_neighbouring_item():
    assert not nut_added_salt_or_sugar(normalise_ingredient("Almonds"))
    assert nut_added_salt_or_sugar(normalise_ingredient("Salted Almonds"))
    assert not nut_added_salt_or_sugar(normalise_ingredient("Unsalted Almonds"))
