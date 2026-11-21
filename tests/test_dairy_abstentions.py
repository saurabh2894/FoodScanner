"""Addendum (research/04): dairy additions that have no explicit NOVA-method basis stay abstaining. FSSAI identity is not a NOVA group basis.
These tests pin the abstentions so a later rule cannot widen them silently."""
import pytest
from foodscan.pipeline import analyse_text


@pytest.mark.parametrize("text", [
    "Ingredients: Milk & Milk Solids",
    "Ingredients: Toned milk, milk solids.",
    "Ingredients: Milk, milk solids, Vitamin A.",
    "Ingredients: Milk solids, Vitamin A palmitate & Vitamin D (ergocalciferol)",
])
def test_no_method_basis_means_abstain(text):
    r = analyse_text(text, source="text")
    assert not r.answered and r.group is None, text


def test_single_milk_solids_and_culture_rule_unchanged():
    assert analyse_text("Ingredients: Milk solids", source="text").group == 1
    assert analyse_text("Ingredients: Milk solids (Toned Milk) & Active Culture", source="text").group == 1


def test_species_qualified_milk_is_group_1_since_per_form_2b():
    # UPDATED (per-form-2b, owner decision 2026-11-21: species-head milk recognition): 'Pasteurized Cow Milk' left the abstention list. FAO Group 1 places animal milk without a species restriction and the
    # the FAO Group 1 definition places milk without species restriction; 'cow milk' and 'goat milk' are recognised milk rows. The other abstentions above (milk solids and vitamin additions) are unchanged.
    assert analyse_text("Ingredients: Pasteurized Cow Milk", source="text").group == 1
