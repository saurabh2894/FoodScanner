"""general-25c: peaches, crookneck squash, scallop squash, alfalfa sprouts heads; peach alias (FDC SR Legacy names). Chard, beet and beets held (existing nalt/beetroot guards: swiss chard rewrite, beet food-colour collision). Radish sprouts held: the existing radish alias rewrites the first word of the phrase."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


NAMES = ["Peaches", "Peach", "Crookneck squash", "Scallop squash", "Alfalfa sprouts"]


@pytest.mark.parametrize("name", NAMES)
def test_plain_group_1(name):
    assert g(name) == 1


@pytest.mark.parametrize("name", NAMES)
@pytest.mark.parametrize("form", ["{}, Salt", "Sugar, {}"])
def test_salt_sugar_group_3(name, form):
    assert g(form.format(name)) == 3


def test_aliases_and_heads_agree():
    assert g("Peach") == g("Peaches")


@pytest.mark.parametrize("t", ["Canned peaches", "Peach jam", "Alfalfa seeds"])
def test_other_forms_not_group_1(t):
    assert g(t) != 1
