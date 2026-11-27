"""general-24w: ulluco head (PROSEA identity, FAO Group 1 roots and tubers clause) and kundri alias to ivy gourd (IISc Hindi vernacular line, naming only)."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


def test_plain_and_boiled_equal_potato_row():
    assert g("Ulluco") == g("Potato") == 1 and g("Boiled ulluco") == g("Boiled potato") == 1


def test_salt_and_sugar_forms_group3():
    assert g("Ulluco, Salt") == g("Potato, Salt") == 3 and g("Sugar, Kundri") == g("Sugar, Ivy gourd") == 3


@pytest.mark.parametrize("t", ["Ulluco flour", "Canned ulluco", "Kundri powder"])
def test_processed_forms_abstain(t):
    assert g(t) is None


def test_kundri_equals_ivy_gourd():
    assert g("Kundri") == g("Ivy gourd") == 1
