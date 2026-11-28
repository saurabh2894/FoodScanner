"""cofid-fish-fruit-24: CoFID-named raw fish and fruit behave exactly like the existing haddock and gooseberries rows."""
import pytest
from foodscan.pipeline import analyse_text


def res(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "{}, Sugar", "Dried {}", "{} powder", "Smoked {}", "Canned {}", "Salted {}", "Breaded {}", "Fried {}", "{} (5%), Water", "Rice, {}", "{} flavour", "{} stock", "{} juice", "Hydrogenated {}"]
FISH = ["Plaice", "Hake", "Bream", "Coley", "Sprats", "Skate", "Rohu", "Katla", "Hilsa"]
FRUIT = ["Redcurrants", "Whitecurrants", "Damsons", "Greengages"]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", FISH)
def test_fish_matches_haddock(form, name):
    if form == "Smoked {}":
        # smoked-fish-24: "Smoked Haddock" is now an explicit Group 3 row (FAO "smoked fish", FDC identity); these CoFID names stay unrecognised when smoked
        assert res(form.format(name)) is None
        return
    assert res(form.format(name)) == res(form.format("Haddock"))


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", FRUIT)
def test_fruit_matches_gooseberries(form, name):
    assert res(form.format(name)) == res(form.format("Gooseberries"))


def test_plain_forms_placed():
    for n in FISH + FRUIT:
        assert res(n) == 1


def test_neighbours_unchanged():
    assert res("Salmon") is None and res("Tuna") == 1  # Tuna: fssai-fish-26c
    # general-24k: Swede left this control list. PROTA Brassica napus (https://plantuse.plantnet.org/en/Brassica_napus_(PROTA)) gives "Swede, rutabaga (En)", so it is now an alias of the existing rutabagas row.
    assert res("Swede") == res("Rutabagas") == 1
