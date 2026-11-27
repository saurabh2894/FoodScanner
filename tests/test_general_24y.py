"""general-24y: mirabelle, red huckleberry, barberry heads. Plain forms group 1; processed forms abstain; bare huckleberry stays unrecognised."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


@pytest.mark.parametrize("name", ["Mirabelle", "Red huckleberry", "Barberry"])
def test_plain_group_1(name):
    assert g(name) == 1


@pytest.mark.parametrize("name", ["Mirabelle", "Red huckleberry", "Barberry"])
@pytest.mark.parametrize("form", ["{}, Salt", "Sugar, {}"])
def test_salt_sugar_group_3(name, form):
    assert g(form.format(name)) == 3


@pytest.mark.parametrize("t", ["Huckleberry", "Mirabelle juice", "Barberry powder", "Red huckleberry jam"])
def test_processed_and_bare_abstain(t):
    assert g(t) is None
