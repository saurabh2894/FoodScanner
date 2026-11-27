"""general-25a: plain single-grain flake heads (wheat, ragi, jowar, rice) and poha / sorghum flakes aliases. Plain form group 1; salted or sugared group 3; corn flakes stay held; processed or dish forms abstain."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


NAMES = ["Wheat flakes", "Ragi flakes", "Jowar flakes", "Rice flakes", "Poha", "Sorghum flakes"]


@pytest.mark.parametrize("name", NAMES)
def test_plain_group_1(name):
    assert g(name) == 1


@pytest.mark.parametrize("name", NAMES)
@pytest.mark.parametrize("form", ["{}, Salt", "Sugar, {}"])
def test_salt_sugar_group_3(name, form):
    assert g(form.format(name)) == 3


def test_alias_equals_head():
    assert g("Poha") == g("Rice flakes") and g("Sorghum flakes") == g("Jowar flakes")


@pytest.mark.parametrize("t", ["Corn flakes", "Fried rice flakes", "Poha mix", "Rice flakes, Sugar, Flavour", "Quinoa flakes"])
def test_held_or_other_forms_not_group_1(t):
    assert g(t) != 1
