"""generic-fish-24: generic cod, halibut, pollock, flounder, crab, lobster behave like their existing species rows in every probed form."""
import pytest
from foodscan.pipeline import analyse_text


def res(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "{}, Sugar", "Dried {}", "{} powder", "Smoked {}", "Canned {}", "Salted {}", "Breaded {}", "Fried {}", "{} (5%), Water", "Rice, {}", "{} flavour", "{} paste", "{} stick", "Hydrogenated {}"]
SPECIES = {"Cod": "Atlantic cod", "Halibut": "Greenland halibut", "Pollock": "Alaska pollock", "Flounder": "Atlantic cod", "Crab": "Dungeness crab", "Lobster": "Northern lobster"}


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", list(SPECIES))
def test_matches_species_row(form, name):
    assert res(form.format(name)) == res(form.format(SPECIES[name]))


def test_held_generics_stay_unrecognised():
    for n in ["Salmon", "Tuna", "Shrimp", "Catfish", "Tilapia", "Roe", "Herring", "Mackerel", "Anchovy"]:
        assert res(n) is None
