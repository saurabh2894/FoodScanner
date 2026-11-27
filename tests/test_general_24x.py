"""general-24x: aronia, jostaberry, black sapote, calamansi, kabocha heads plus chokeberry(ies) aliases. Plain forms equal their reference rows; processed forms abstain; chokecherry (Prunus) stays unrecognised."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


@pytest.mark.parametrize("name", ["Aronia", "Chokeberry", "Chokeberries", "Jostaberry", "Black sapote", "Calamansi", "Kabocha"])
def test_plain_group_1(name):
    assert g(name) == 1


@pytest.mark.parametrize("name,ref", [("Aronia", "Gooseberry"), ("Jostaberry", "Gooseberry"), ("Black sapote", "Persimmon"), ("Calamansi", "Lime"), ("Kabocha", "Pumpkin")])
@pytest.mark.parametrize("form", ["{}, Salt", "Sugar, {}"])
def test_salt_sugar_match_reference(name, ref, form):
    assert g(form.format(name)) == g(form.format(ref)) == 3


@pytest.mark.parametrize("t", ["Calamansi juice", "Kabocha puree", "Aronia powder", "Chokecherry"])
def test_processed_and_other_species_abstain(t):
    assert g(t) is None
