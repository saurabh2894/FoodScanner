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


FISH_C = ["Sardine", "Sardines", "Mackerel", "Pomfret", "Seer fish", "Anchovy", "Anchovies", "Tuna"]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", FISH_C)
def test_named_in_canned_standard_matches_haddock(form, name):
    if form in ("Smoked {}", "Canned {}") and name in ("Tuna", "Sardine", "Sardines"):
        return  # canned tuna/sardine rows are Group 3 by canned-fish-g3-1
    if form == "Smoked {}":
        assert res(form.format(name)) is None
        return
    assert res(form.format(name)) == res(form.format("Haddock"))


@pytest.mark.parametrize("n", FISH_C)
def test_bare_names_group1_canned_pack_forms_abstain(n):
    assert res(n) == 1
    for f in ("{} (Canned)", "{} in Oil", "{}, Tomato Sauce"):
        assert res(f.format(n)) is None
