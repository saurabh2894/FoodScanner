"""tamarind-24: plain tamarind (FAO Group 1 fruit class, FSSAI 2.3.49 seedless tamarind, FDC SR Legacy 167763). Pulp/puree/paste/concentrate, juice, powder, seed, kernel, gum, nectar, candy, chutney and sauce forms are different products (FSSAI 2.3.18 defines pulp as boiled and sieved) and must abstain."""
import pytest
from foodscan.pipeline import analyse_text


def grp(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


@pytest.mark.parametrize("t", ["Tamarind", "Tamarinds", "Dried tamarind", "Seedless tamarind"])
def test_plain_forms_group_1(t):
    assert grp(t) == 1


@pytest.mark.parametrize("t", ["Tamarind, Salt", "Tamarind, Sugar", "Tamarind and Jaggery"])
def test_added_ingredient_group_3(t):
    assert grp(t) == 3


@pytest.mark.parametrize("t", ["Tamarind pulp", "Tamarind paste", "Tamarind puree", "Tamarind concentrate", "Tamarind concentrate (65%)", "Tamarind (pulp)", "Tamarind juice", "Tamarind powder", "Tamarind extract", "Tamarind seed", "Tamarind seed powder", "Tamarind kernel powder", "Tamarind gum", "Tamarind nectar", "Tamarind candy", "Tamarind chutney", "Tamarind sauce", "Sweetened tamarind", "Tamarind in brine", "Tamarind (E412)", "Tamarind flakes", "Imli"])
def test_other_forms_abstain(t):
    assert grp(t) is None
