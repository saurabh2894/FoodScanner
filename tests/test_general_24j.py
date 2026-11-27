"""general-24j: ten plain fruit heads and two vegetable heads from PROSEA/PROTA/EPPO naming (FAO Group 1 placement as in the existing plain fruit and vegetable rows), plus twelve alias names. Every probed form equals the comparison row; every alias equals its head."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "Dried {}", "Roasted {}", "{} (Sugar)", "{} 100%", "{} powder", "{} extract", "Instant {}", "Decaffeinated {}", "{} flavour", "{} leaves", "{} bags", "Iced {}", "{} concentrate", "Cooked {}", "{} (Salt)", "Milk, {}", "{}, Milk"]

FRUITS = ["Ambarella", "Bilimbi", "Langsat", "Salak", "Santol", "Tamarillo", "Wax apple", "Cape gooseberry", "Dragon fruit"]
VEGS = ["Snow peas"]
ALIASES = [("Jamun", "Java-plum"), ("Jambolan", "Java-plum"), ("Snake fruit", "Salak"), ("Tree tomato", "Tamarillo"), ("Java apple", "Wax apple"), ("Wax jambu", "Wax apple"),
           ("Pitaya", "Dragon fruit"), ("Pitahaya", "Dragon fruit"), ("Sentol", "Santol"), ("Kechapi", "Santol"), ("Mangetout", "Snow peas"), ("Smooth loofah", "Dishcloth gourd"), ("Sponge gourd", "Dishcloth gourd")]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", FRUITS)
def test_fruit_head_matches_plain_fruit_row(name, form):
    assert g(form.format(name)) == g(form.format("Cantaloupe melons")), (name, form)


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", VEGS)
def test_veg_head_matches_okra(name, form):
    assert g(form.format(name)) == g(form.format("Okra")), (name, form)


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name,target", ALIASES)
def test_alias_matches_head(name, target, form):
    assert g(form.format(name)) == g(form.format(target)), (name, form)


@pytest.mark.parametrize("name", FRUITS + VEGS + [a for a, _ in ALIASES])
def test_plain_group_1(name):
    assert g(name) == 1


def test_black_plum_and_gherkin_stay_unrecognised():
    for t in ["Black plum", "Gherkin", "Loofah"]:
        assert g(t) is None
