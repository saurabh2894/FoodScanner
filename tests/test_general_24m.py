"""general-24m: eight plain heads (fruit: bignay, rukam, horse mango, kei apple, jaboticaba, pulasan; vegetable: mizuna, caisin; PROSEA and other named English sources, FAO Group 1 placement as in the existing rows) and four alias names. Every probed form equals the comparison row; every alias equals its head."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "Dried {}", "Roasted {}", "{} (Sugar)", "{} 100%", "{} powder", "{} extract", "Instant {}", "Decaffeinated {}", "{} flavour", "{} leaves", "{} bags", "Iced {}", "{} concentrate", "Cooked {}", "{} (Salt)", "Milk, {}", "{}, Milk"]

VEGS = ["Mizuna", "Caisin"]
FRUITS = ["Bignay", "Rukam", "Horse mango", "Kei apple", "Jaboticaba", "Pulasan"]
ALIASES = [("Bachang", "Horse mango"), ("Mizuna greens", "Mizuna"), ("Flowering white cabbage", "Caisin"), ("Jabuticaba", "Jaboticaba")]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", VEGS)
def test_veg_head_matches_okra(name, form):
    assert g(form.format(name)) == g(form.format("Okra")), (name, form)


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", FRUITS)
def test_fruit_head_matches_guava(name, form):
    assert g(form.format(name)) == g(form.format("Guavas")), (name, form)


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name,target", ALIASES)
def test_alias_matches_head(name, target, form):
    assert g(form.format(name)) == g(form.format(target)), (name, form)


@pytest.mark.parametrize("name", VEGS + FRUITS + [a for a, _ in ALIASES])
def test_plain_group_1(name):
    assert g(name) == 1


def test_unaliased_names_stay_unrecognised():
    for t in ["Choy sum", "Chinese laurel", "Salamander tree", "Perilla"]:
        assert g(t) is None
