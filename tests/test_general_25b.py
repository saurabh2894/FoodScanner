"""general-25b: wheat, oat and rice bran heads (FDC SR Legacy names, FAO Group 1 fractioning). Plain form group 1; salted or sugared group 3; bran products and oil stay out."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


NAMES = ["Wheat bran", "Oat bran", "Rice bran"]


@pytest.mark.parametrize("name", NAMES)
def test_plain_group_1(name):
    assert g(name) == 1


@pytest.mark.parametrize("name", NAMES)
@pytest.mark.parametrize("form", ["{}, Salt", "Sugar, {}"])
def test_salt_sugar_group_3(name, form):
    assert g(form.format(name)) == 3


def test_rice_bran_oil_unchanged():
    assert g("Rice bran oil") == 2


@pytest.mark.parametrize("t", ["Bran flakes", "Bran biscuit", "Wheat bran powder", "Corn bran"])
def test_other_bran_forms_not_group_1(t):
    assert g(t) != 1
