"""general-25d (mung bean sprouts held: the existing mung bean alias rewrites it to moong dal sprouts): indian gooseberry alias to amla (Kew naming)."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


@pytest.mark.parametrize("t", ["Indian gooseberry"])
def test_plain_group_1(t):
    assert g(t) == 1


def test_alias_agrees():
    assert g("Indian gooseberry") == g("Amla")


@pytest.mark.parametrize("t", ["Indian gooseberry candy", "Indian gooseberry juice"])
def test_other_forms_not_group_1(t):
    assert g(t) != 1
