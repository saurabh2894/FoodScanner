"""per-form-2a salted-grain guard (SYNTHETIC; both directions). The 23 Batch-4 grain/flour terms with salt added in the item's own name or bracket take Group 3 (FAO: group 1 foods with salt added are classed in
NOVA group 3 as processed foods; inference level: class-instance, no clause names a salted grain); every other row and the nut/legume/vegetable/fruit guards are unchanged."""
from __future__ import annotations

import pytest

from foodscan.classify import _SCOPED_TERMS, grain_added_salt
from foodscan.normalise import normalise_ingredient
from foodscan.pipeline import analyse_text


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return (a.group if a.answered else None), a


@pytest.mark.parametrize("t", ["Salted Buckwheat", "Roasted Salted Buckwheat", "Salted Rice", "Salted Wheat Flour", "Salted Oat Flour", "Rice (salted)", "Rice (Rice, Salt)", "Salted Parboiled Rice", "Wild Rice (with salt)", "Salted Cornmeal"])
def test_synthetic_a_salted_grain_or_grain_flour_item_takes_group_3_not_group_1(t):
    group, a = g(t)
    assert group == 3 and not any(d.detail == "single recognised unprocessed food" for d in a.drivers), (t, group)
    assert any("grain or grain flour with added salt" in d.detail for d in a.drivers)


@pytest.mark.parametrize("t", ["Rice", "Buckwheat", "Wheat Flour", "Unsalted Rice", "Rice (no added salt)", "Rice (salt free)", "Rice (Basmati)", "Roasted Buckwheat", "Toasted Oat Flour", "Toasted Unsalted Oat Flour"])
def test_synthetic_plain_negated_and_roasted_forms_keep_group_1(t):
    assert g(t)[0] == 1, t


@pytest.mark.parametrize("t,expected", [("Salted Milk", None), ("Salted Egg", None), ("Salted Almonds", 3), ("Salted Pinto Beans", 3), ("Salted Potatoes", 3), ("Salted Mango", 3), ("Mango (preserved)", None), ("Kidney Beans (canned)", None)])
def test_synthetic_other_rows_and_the_nut_legume_vegetable_fruit_guards_are_unchanged(t, expected):
    assert g(t)[0] == expected, t                   # salted milk/egg: outside the 23-term scope; whole-food-guard-1 turns the former Group 1 into an abstention (no Group 3 is asserted; that decision stays with the owner)


def test_synthetic_a_salted_grain_inside_a_list_and_the_flour_list_rule():
    assert g("Rice, Salted Buckwheat")[0] == 3 and g("Rice, Salt")[0] == 3
    assert g("Salted Wheat Flour, Water")[0] is None                           # flour-based list: the existing list rule still abstains
    assert g("Rice")[0] == 1


def test_synthetic_the_scope_is_the_23_batch_4_terms_and_negation_is_not_matched():
    assert len(_SCOPED_TERMS["toasted"]) == 23
    ing = lambda t: normalise_ingredient(t)
    assert grain_added_salt(ing("Salted Rice"), "whole_food") and grain_added_salt(ing("Salted Wheat Flour"), "flour")
    assert not grain_added_salt(ing("Unsalted Rice"), "whole_food") and not grain_added_salt(ing("Salted Milk"), "whole_food") and not grain_added_salt(ing("Salted Rice"), "culinary")
