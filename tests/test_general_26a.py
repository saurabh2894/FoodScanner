"""general-26a: five FSSAI 2.8.1 sugar names (plantation white, khandsari, bura, cube, icing) routed to the existing sugar row as aliases. Recognition only; the sugar row's placement (FAO Table 1 Group 2 "sugar and molasses obtained from cane or beet") and conditions apply unchanged. Held with reasons: paneer/chhana (FSSAI 2.1.16 identity only; the FAO cheese clause covers non-alcoholic fermentation, acid-precipitated paneer is not named), dextrose (FAO lists it among Group 4 markers), sugar cube/icing alone (not FSSAI names)."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


NAMES = ["Plantation white sugar", "Khandsari sugar", "Bura sugar", "Cube sugar", "Icing sugar"]


@pytest.mark.parametrize("t", NAMES)
def test_named_sugars_follow_the_sugar_row(t):
    assert g(t) == g("Sugar") == 2
    assert g("Cashew nuts, " + t + ", Salt") == 3


@pytest.mark.parametrize("t", NAMES)
def test_flavour_marker_still_group_4(t):
    assert g("Wheat flour, " + t + ", Salt, Flavour") == 4


@pytest.mark.parametrize("t", ["Sugar cube", "Icing", "Khandsari", "Paneer", "Chhana"])
def test_held_names_stay_unrecognised(t):
    assert g(t) is None
