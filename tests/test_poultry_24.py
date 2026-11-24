"""poultry-24: quail, pheasant, ostrich, guinea hen behave like the existing duck and turkey rows in every probed form."""
import pytest
from foodscan.pipeline import analyse_text


def res(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "{}, Sugar", "{}, Oil", "Dried {}", "{} powder", "Smoked {}", "Canned {}", "{} sausage", "Fried {}", "Breaded {}", "{} (5%), Water", "Rice, {}", "{} flavour", "{} stock"]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", ["Quail", "Pheasant", "Ostrich", "Guinea hen"])
def test_matches_duck(form, name):
    assert res(form.format(name)) == res(form.format("Duck"))
