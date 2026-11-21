"""whole-food-guard-1 (SYNTHETIC; abstention only). A recognised whole_food item is not answered Group 1 when its own name or bracket carries added salt, sugar, brine, an oil or a canned/bottled/preserved form
(except the 23 grain/flour terms whose salted form is already Group 3), or when its own bracket names a food of a different class (dairy, egg, plant). No Group 3 is asserted for salted or sugared milk or eggs.
Supported same-food and species brackets, plain forms, comma-separated lists and the other kinds are unchanged."""
from __future__ import annotations

import pytest

from foodscan.pipeline import analyse_text


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return (a.group if a.answered else None), a


WHOLE_FOODS = ["Milk", "Toned Milk", "Buffalo Milk", "Cow Milk", "Eggs", "Egg", "Dahi", "Ragi", "Oat", "Wheat", "Yeast", "Milk Solids", "Rice"]


@pytest.mark.parametrize("t", WHOLE_FOODS)
def test_synthetic_added_salt_sugar_oil_brine_or_preserved_forms_abstain(t):
    for f in ("{x} (sugar)", "{x} (sunflower oil)", "{x} (canned)", "{x} (brine)", "{x} (preserved)"):
        group, a = g(f.format(x=t))
        assert group is None and "own text carries added salt, sugar, brine, oil" in a.reason, f.format(x=t)


@pytest.mark.parametrize("t", ["Milk", "Eggs", "Dahi", "Ragi", "Oat", "Wheat", "Yeast"])
def test_synthetic_salted_forms_abstain_and_assert_no_group_3(t):
    for f in ("Salted {x}", "{x} (salted)"):
        group, a = g(f.format(x=t))
        assert group is None and a.reason, f.format(x=t)


def test_synthetic_the_23_grain_terms_keep_their_group_3_and_negations_keep_group_1():
    assert g("Salted Rice")[0] == 3 and g("Salted Wheat Flour")[0] == 3 and g("Rice (salted)")[0] == 3
    for t in ("Unsalted Milk", "Milk (no added salt)", "Eggs (no added sugar)", "Milk (Pasteurized)", "Eggs (Raw)", "Roasted Gram"):
        assert g(t)[0] == 1, t


@pytest.mark.parametrize("t", ["Rice (Egg)", "Eggs (Rice)", "Milk (Rice)", "Milk (Egg)", "Dahi (Rice)", "Wheat (Egg)"])
def test_synthetic_a_distinct_nested_food_abstains_with_an_accurate_reason(t):
    group, a = g(t)
    assert group is None and a.reason.startswith("a bracket names a different kind of food inside the item (") and "not recognise" not in a.reason, t


@pytest.mark.parametrize("t", ["Milk (Buffalo Milk)", "Milk (Cow Milk)", "Toned Milk (Cow Milk)", "Buffalo Milk (Buffalo Milk)", "Eggs (Egg)", "Egg (Eggs)", "Rice (Rice)", "Dehydrated Vegetable (Onion)", "Milk (Pasteurized Cow Milk)"])
def test_synthetic_supported_same_food_and_species_brackets_stay_group_1(t):
    assert g(t)[0] == 1, t


def test_synthetic_species_milk_in_a_non_milk_head_keeps_the_existing_unrecognised_bracket_reason():
    group, a = g("Rice (Buffalo Milk)")
    assert group is None and a.reason.startswith("a bracket on a legume, vegetable, fruit or flour item names content the vocabulary does not recognise")


def test_synthetic_lists_and_other_kinds_are_unchanged():
    assert g("Milk, Sugar")[0] == 3 and g("Rice, Salt")[0] == 3 and g("Milk, Starter Culture")[0] == 1
    assert g("Salted Almonds")[0] == 3 and g("Salted Pinto Beans")[0] == 3 and g("Kidney Beans (canned)")[0] is None
    assert g("Milk (Salted), Water")[0] is None and g("Milk, Eggs (Rice)")[0] is None
