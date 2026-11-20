"""Review items 4 to 6: the Contains policy, user-approved vocabulary/INS additions, and what stays unmapped.

Policy pinned here (also in CLAUDE.md):
  * A "Contains ..." statement counts as evidence only when it declares an additive class (colour, flavour,
    sweetener, emulsifier, ...). Allergen statements ("Contains soy, milk") and "May contain" never do.
  * yeast extract and pea protein are NOT markers: they are in no research/ file, and pea protein does not
    say concentrate or isolate. They stay outside the vocabulary and are shown under "Not assessed".
"""
import pytest

from foodscan.normalise import normalise_ingredient
from foodscan.parser import parse_ingredient_list
from foodscan.pipeline import analyse_text


# ---- Contains policy -------------------------------------------------------------------------------
@pytest.mark.parametrize("statement", [
    "Contains soy, milk, wheat, gluten.", "Contains: milk and soy.", "CONTAINS WHEAT.", "Contains milk solids.",
    "May contain traces of nuts, soy.", "Contains 37% millets.",
])
def test_allergen_and_other_statements_never_drive_group4(statement):
    a = analyse_text("Ingredients: Rice, salt. " + statement)
    assert a.answered and a.group == 3, (statement, a.group, a.reason)


@pytest.mark.parametrize("statement", [
    "Contains permitted natural colour.", "Contains permitted natural color.", "Contains added flavour.",
    "CONTAINS NATURE IDENTICAL FLAVOURING SUBSTANCES.", "Contains artificial sweetener.",
])
def test_declared_additive_classes_do_count(statement):
    a = analyse_text("Ingredients: Rice, salt. " + statement)
    assert a.group == 4 and any("Contains" in d.detail for d in a.drivers), statement


# ---- user-approved additions ("fix all", 2026-11-20) --------------------------------------------------
def test_jaggery_is_a_culinary_ingredient():
    a = analyse_text("Ingredients: Jaggery.")
    assert a.group == 2
    assert analyse_text("Ingredients: Ragi, jaggery, groundnut oil.").group == 3      # previously stopped at jaggery


def test_ins_322_lecithin_is_a_strong_emulsifier_marker():
    (use,) = normalise_ingredient("INS 322").ins
    assert use.name == "lecithin" and "Project-maintained classification mapping" in use.source
    a = analyse_text("Ingredients: Milk, INS 322.")
    assert a.group == 4 and any("INS 322" in d.detail for d in a.drivers)


def test_ins_452i_is_named_but_never_decides_a_group():
    (use,) = normalise_ingredient("stabiliser (INS 452(i))").ins
    assert use.code == "452(i)" and use.name == "sodium polyphosphate" and "Project-maintained classification mapping" in use.source
    a = analyse_text("Ingredients: Milk, stabiliser (INS 452(i)).")
    assert not a.answered and "weak" in a.reason


# ---- decisions: not markers -------------------------------------------------------------------------
@pytest.mark.parametrize("ingredient", ["yeast extract", "pea protein"])
def test_yeast_extract_and_pea_protein_are_not_markers_and_stay_visible(ingredient):
    a = analyse_text(f"Ingredients: Rice, {ingredient}, salt.")
    assert not a.answered and ingredient in a.unassessed
    assert "vocabulary" in a.reason


def test_a_real_marker_still_decides_even_with_these_present():
    a = analyse_text("Ingredients: Rice, yeast extract, pea protein, natural flavour.")
    assert a.group == 4 and "yeast extract" in a.unassessed and "pea protein" in a.unassessed


def test_weak_single_additive_rule_is_unchanged():
    assert not analyse_text("Ingredients: Mango, sugar, pectin (INS 440).").answered
