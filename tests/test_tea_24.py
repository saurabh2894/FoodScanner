"""tea-24: black tea, oolong tea, kangra tea routed to the existing tea row (FSSAI 2.10.1(1)-(2)); aliases, not heads."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "Dried {}", "Roasted {}", "{} (Sugar)", "{} 100%", "{} powder", "{} extract", "Instant {}", "Decaffeinated {}", "{} flavour", "{} leaves", "{} bags", "Iced {}", "{} concentrate", "Cooked {}", "{} (Salt)", "Milk, {}", "{}, Milk"]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", ["Black tea", "Oolong tea", "Kangra tea"])
def test_alias_matches_tea(name, form):
    assert g(form.format(name)) == g(form.format("Tea")), (name, form)


@pytest.mark.parametrize("name", ["Black tea", "Oolong tea", "Kangra tea"])
def test_plain_group_1(name):
    assert g(name) == 1
