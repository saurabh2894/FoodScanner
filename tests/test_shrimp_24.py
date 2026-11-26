"""shrimp-24: shrimp head (FDC 175179; FSSAI 2.6.1(1)(i) names shrimps or prawns; FAO Group 1 seafood class-instance, squid-row conditions); prawn alias. Reverses the fish-rows-2-24 hold with a processed-form matrix."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "{}, Sugar", "Dried {}", "{} powder", "Smoked {}", "Canned {}", "Salted {}", "Breaded {}", "Fried {}", "{} (5%), Water", "Rice, {}", "{} flavour", "{} paste", "{} stick", "Hydrogenated {}", "Freeze dried {}", "{} sauce", "{} extract", "{} cracker", "{} chips", "Frozen {}", "Cooked {}", "{} (Salt)", "{} 100%", "Wheat flour, {}"]


@pytest.mark.parametrize("form", FORMS)
def test_prawn_matches_shrimp(form):
    assert g(form.format("Prawn")) == g(form.format("Shrimp"))
    assert g(form.format("Prawns")) == g(form.format("Shrimps"))


@pytest.mark.parametrize("form", FORMS)
def test_shrimp_matches_squid_condition_set(form):
    s, q = g(form.format("Shrimp")), g(form.format("Squid"))
    assert s == q, (form, s, q)


def test_plain_is_group_1():
    for t in ["Shrimp", "Prawn", "Shrimps", "Prawns"]:
        assert g(t) == 1


def test_processed_forms_never_group_1():
    for t in ["Dried Shrimp", "Shrimp Paste", "Shrimp Powder", "Shrimp Sauce", "Freeze Dried Prawns", "Prawn Crackers", "Breaded Shrimp", "Shrimp Flavour", "Canned Shrimp", "Smoked Prawns", "Fried Prawns", "Shrimp Extract"]:
        assert g(t) != 1, t
