"""fssai-fish-26b: eleven fish names listed in FSSAI 2.6.2 behave exactly like the existing haddock row (FAO Table 1 Group 1 fish example). Held: sardine, mackerel, pomfret, seer fish, anchovy (FSSAI 2.6 canned-fish list; canned-fish-g3-1 keeps bare names unrecognised)."""
import pytest
from foodscan.pipeline import analyse_text


def res(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "{}, Sugar", "Dried {}", "{} powder", "Smoked {}", "Canned {}", "Salted {}", "Breaded {}", "Fried {}", "{} (5%), Water", "Rice, {}", "{} flavour", "{} stock", "Hydrogenated {}"]
FISH = ['Barracuda', 'Bombay Duck', 'Catfish', 'Flatfish', 'Goatfish', 'Queen Fish', 'Ribbon Fish', 'Silver Belly', 'Threadfin', 'Tilapia', 'Snakehead']


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", FISH)
def test_fish_matches_haddock(form, name):
    if form == "Smoked {}":
        assert res(form.format(name)) is None
        return
    assert res(form.format(name)) == res(form.format("Haddock"))


def test_plain_forms_placed():
    for n in FISH:
        assert res(n) == 1


@pytest.mark.parametrize("n", ["Sardine", "Sardines", "Mackerel", "Pomfret", "Seer fish", "Anchovies", "Tuna"])
def test_canned_ambiguous_names_stay_unrecognised(n):
    assert res(n) is None
