"""grits-24: corn grits (FAO clause names grits made from corn; FDC 171654 and 171670; FSSAI 2.4.24), alias maize grits. Behaves like the existing cornmeal row in every form except salted ones, where cornmeal has an older rule giving 3 and the new row abstains (conservative). Instant, quick, enriched, cooked and flavoured grits abstain."""
import pytest
from foodscan.pipeline import analyse_text

FORMS = ["{}", "{}, Salt", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "Dried {}", "Roasted {}", "{} (Sugar)", "Chutney ({}, Chilli)", "{} 100%", "{} powder", "{} starch", "Hydrogenated {}", "Fermented {}", "Sweetened {}", "Bleached {}", "Enriched {}", "Instant {}", "Quick {}", "Cooked {}", "{} (Butter flavour)", "Flavoured {}", "Degermed {}", "White {}", "Yellow {}"]


def grp(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


@pytest.mark.parametrize("form", FORMS)
def test_alias_and_cornmeal_match(form):
    assert grp(form.format("Corn grits")) == grp(form.format("Maize grits")) == grp(form.format("Cornmeal"))


def test_sole_and_guarded():
    assert grp("Corn grits") == 1 and grp("Maize grits") == 1
    for t in ["Instant corn grits", "Enriched corn grits", "Cooked corn grits", "Corn grits, Salt", "Corn grits (Butter flavour)"]:
        assert grp(t) in (None, 4)
