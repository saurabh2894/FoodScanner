"""general-24z: abiu, wampee, grumichama, wood apple heads (Purdue/Morton identity and use). Plain forms group 1; processed forms abstain."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


NAMES = ["Abiu", "Wampee", "Grumichama", "Wood apple"]


@pytest.mark.parametrize("name", NAMES)
def test_plain_group_1(name):
    assert g(name) == 1


@pytest.mark.parametrize("name", NAMES)
@pytest.mark.parametrize("form", ["{}, Salt", "Sugar, {}"])
def test_salt_sugar_group_3(name, form):
    assert g(form.format(name)) == 3


@pytest.mark.parametrize("t", ["Wood apple juice", "Wampee jam", "Abiu powder", "Grumichama jelly"])
def test_processed_abstain(t):
    assert g(t) is None
