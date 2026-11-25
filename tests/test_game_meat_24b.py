"""game-meat-24b: emu, elk, horse, beaver, squirrel, muskrat behave like the antelope and duck rows in every probed form; goat milk and mutton are untouched."""
import pytest
from foodscan.pipeline import analyse_text


def res(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "{}, Sugar", "Dried {}", "{} powder", "Smoked {}", "Canned {}", "Salted {}", "Breaded {}", "Fried {}", "{} (5%), Water", "Rice, {}", "{} flavour", "{} stock", "{} sausage", "Hydrogenated {}"]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", ["Emu", "Elk", "Horse", "Beaver", "Squirrel", "Muskrat"])
def test_matches_antelope(form, name):
    assert res(form.format(name)) == res(form.format("Antelope"))


def test_neighbours_unchanged():
    assert res("Mutton") is None
    assert res("Goat milk") == 1
    assert res("Goat") is None  # species word alone stays unrecognised (qualifier of milk and cheese)
