"""general-25e: single-spice powder heads (FAO Group 1 names spices 'whole or powdered'; FSSAI Chapter 2 clause 2.9 defines each powder) plus name aliases. Recognition only: a sole spice never takes a NOVA group by itself (existing rule for herb_spice rows)."""
import pytest
from foodscan.pipeline import analyse_text

HEADS = ["Chilli powder", "Turmeric powder", "Coriander powder", "Cumin powder", "Cardamom powder", "Cinnamon powder", "Clove powder", "Fennel powder", "Fenugreek powder", "Ginger powder", "Mustard powder", "Nutmeg powder", "Black pepper powder"]
ALIASES = {"Red chilli powder": "Chilli powder", "Haldi powder": "Turmeric powder", "Dhania powder": "Coriander powder", "Jeera powder": "Cumin powder", "Dry ginger powder": "Ginger powder", "Dried ginger powder": "Ginger powder"}


def a(t):
    return analyse_text("Ingredients: " + t + ".", source="text")


@pytest.mark.parametrize("t", HEADS + list(ALIASES))
def test_recognised_not_unassessed(t):
    r = a("Cashew nuts, " + t + ", Salt")
    assert not r.unassessed


@pytest.mark.parametrize("t", HEADS)
def test_sole_spice_does_not_take_a_group_by_itself(t):
    assert not a(t).answered


@pytest.mark.parametrize("t", HEADS)
def test_cashew_salt_stays_group_3_with_spice_powder(t):
    assert a("Cashew nuts, " + t + ", Salt").group == 3


@pytest.mark.parametrize("t", HEADS)
def test_flavour_added_is_group_4(t):
    assert a("Cashew nuts, " + t + ", Flavour").group == 4


@pytest.mark.parametrize("t", ["Curry powder", "Garam masala", "Ground spices", "Chilli powder seasoning", "Turmeric extract"])
def test_blends_and_extracts_not_recognised_as_the_plain_powder(t):
    assert a(t).unassessed or not a(t).answered
