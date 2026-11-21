"""Powder standard (class-bulk-2, owner rulings 2026-11-21; STANDING for all class batches). SYNTHETIC cases, both directions.
A descriptor-'powder' item on a whole_food, legume or vegetable row, and an item of the food_powder kind, NEVER takes Group 1 from the powder reading alone: an 'X powder' label does not establish
whole-food composition (extract, starch, colour, carrier). Group 1 (sole item only) when the item's OWN text states it, in exactly two forms: '100%' and 'whole' ('whole' is not read for milk: 'whole milk
powder' is a fat grade). Everything else abstains; unassessed co-ingredients are never laundered; markers keep priority."""
from __future__ import annotations

import pytest

from foodscan.classify import powder_composition_stated
from foodscan.normalise import normalise_ingredient
from foodscan.pipeline import analyse_text


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return (a.group if a.answered else None), a


@pytest.mark.parametrize("t", ["Spinach Powder", "Carrot Powder", "Onion Powder", "Pinto Beans Powder", "Banana Powder", "Date Powder", "Milk Powder", "Whole Milk Powder", "Kale Powder (45%)", "Spinach Powdered"])
def test_synthetic_negative_a_bare_x_powder_never_takes_group_1_from_the_powder_reading(t):
    group, a = g(t)
    assert group is None and "named without its composition" in (a.reason or ""), (t, group)


@pytest.mark.parametrize("t", ["100% Spinach Powder", "Spinach Powder (100%)", "Whole Spinach Powder", "100% Date Powder", "Whole Carrot Powder"])
def test_synthetic_the_two_affirmative_forms_take_group_1_as_the_sole_item(t):
    group, a = g(t)
    assert group == 1 and "states whole-food composition" in a.drivers[0].detail, (t, group)


def test_synthetic_the_affirmative_forms_are_exactly_100_percent_and_whole_and_never_milk_whole():
    ok = lambda t: powder_composition_stated(normalise_ingredient(t))
    assert ok("100% Spinach Powder") and ok("Spinach Powder (100%)") and ok("Whole Spinach Powder")
    assert not ok("Spinach Powder") and not ok("Spinach Powder (45%)") and not ok("Pure Spinach Powder") and not ok("Whole Milk Powder") and not ok("100.5% Spinach Powder")


@pytest.mark.parametrize("t", ["Rice, Spinach Powder", "Rice, 100% Spinach Powder", "Milk, Banana Powder", "Rice, Spinach Powder, Salt"])
def test_synthetic_in_a_list_the_powder_item_never_gives_group_1_and_the_rice_is_unaffected(t):
    group, a = g(t)
    assert group is None and "named without its composition" in (a.reason or ""), (t, group)
    assert g("Rice")[0] == 1                                                   # plain rows unchanged
    assert g("Rice, Salt")[0] == 3


def test_synthetic_unassessed_co_ingredients_are_not_laundered_by_the_powder_abstention():
    group, a = g("Rice, Spinach Powder, XQ9")
    assert group is None and "XQ9" in " ".join(a.unassessed) and "not in the local vocabulary" in a.reason
    group, a = g("Rice, Spinach Powder, Flavouring XQ9")
    assert group == 4 and not any("spinach" in d.detail.lower() for d in a.drivers)          # the flavour marker decides (existing); the powder gives nothing
    group, a = g("Seasoning Blend (Spinach Powder, Salt)")
    assert group is None and any("Seasoning Blend" in u for u in a.unassessed) and "Spinach Powder" in a.reason     # nested: the blend stays unassessed, the powder member abstains


@pytest.mark.parametrize("t", ["Spinach Extract Powder", "Beet Red Powder", "Celery Powder", "Arrowroot Powder"])
def test_synthetic_negative_base_terms_that_stay_out_remain_unassessed(t):
    group, a = g(t)
    assert group is None and t.lower() in " ".join(u.lower() for u in a.unassessed)


@pytest.mark.parametrize("t", ["Spinach Powder (Maltodextrin)", "Spinach & Kale Powder"])
def test_synthetic_carrier_and_shared_descriptor_forms_never_take_group_1(t):
    group, a = g(t)
    assert group != 1, t
    assert not any(d.detail.startswith("single recognised") for d in a.drivers)


@pytest.mark.parametrize("t", ["Spinach", "Dried Spinach", "Unsalted Carrots", "Salted Pinto Beans", "Rice, Carrots", "Kale (frozen)"])
def test_synthetic_plain_negated_and_guarded_forms_are_unchanged(t):
    group, a = g(t)
    expected = {"Spinach": 1, "Dried Spinach": 1, "Unsalted Carrots": 1, "Salted Pinto Beans": 3, "Rice, Carrots": None, "Kale (frozen)": 1}[t]
    assert group == expected, t


def test_synthetic_a_salted_or_brined_powder_keeps_its_guard_group_3():
    assert g("Salted Pinto Beans Powder")[0] == 3
