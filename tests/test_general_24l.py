"""general-24l: two plain vegetable heads (arracacha, fig-leaf gourd; PROSEA English names, FAO Group 1 placement as in the existing vegetable rows) plus nine alias names of existing rows. Sponge gourd was a duplicate head of the existing dishcloth gourd row and is now an alias of it. Every probed form equals the comparison row; every alias equals its head."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "Dried {}", "Roasted {}", "{} (Sugar)", "{} 100%", "{} powder", "{} extract", "Instant {}", "Decaffeinated {}", "{} flavour", "{} leaves", "{} bags", "Iced {}", "{} concentrate", "Cooked {}", "{} (Salt)", "Milk, {}", "{}, Milk"]

VEGS = ["Arracacha", "Fig-leaf gourd"]
ALIASES = [("Peruvian parsnip", "Arracacha"), ("Malabar gourd", "Fig-leaf gourd"), ("Tannia", "Yautia"), ("Jute mallow", "Jute"), ("Jews mallow", "Jute"), ("Jew's mallow", "Jute"),
           ("Sponge gourd", "Dishcloth gourd"), ("Smooth loofah", "Dishcloth gourd")]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", VEGS)
def test_veg_head_matches_okra(name, form):
    assert g(form.format(name)) == g(form.format("Okra")), (name, form)


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name,target", ALIASES)
def test_alias_matches_head(name, target, form):
    assert g(form.format(name)) == g(form.format(target)), (name, form)


@pytest.mark.parametrize("name", VEGS + [a for a, _ in ALIASES])
def test_plain_group_1(name):
    assert g(name) == 1


def test_black_plum_and_gherkin_stay_unrecognised():
    for t in ["Cocoyam", "Indian spinach", "Malabar spinach", "Loofah"]:
        assert g(t) is None
