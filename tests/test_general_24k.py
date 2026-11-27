"""general-24k: six plain fruit heads from PROSEA naming (FAO Group 1 placement as in the existing plain fruit and vegetable rows), plus 27 alias names (English and Hindi names of existing rows). Every probed form equals the comparison row; every alias equals its head."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "Dried {}", "Roasted {}", "{} (Sugar)", "{} 100%", "{} powder", "{} extract", "Instant {}", "Decaffeinated {}", "{} flavour", "{} leaves", "{} bags", "Iced {}", "{} concentrate", "Cooked {}", "{} (Salt)", "Milk, {}", "{}, Milk"]

FRUITS = ["Water apple", "Malay apple", "Cempedak", "Marang", "Naranjilla", "Canistel"]
ALIASES = [(a, b) for a, b in [("Pomerac", "Malay apple"), ("Bell fruit", "Water apple"), ("Chempedak", "Cempedak"), ("Egg-fruit", "Canistel"), ("Egg fruit", "Canistel"), ("West Indian cherry", "Acerola"),
           ("Surinam cherry", "Pitanga"), ("Brazil cherry", "Pitanga"), ("Cantaloupe", "Cantaloupe melons"), ("Musk melon", "Cantaloupe melons"), ("Muskmelon", "Cantaloupe melons"),
           ("Swede", "Rutabagas"), ("Rocket", "Arugula"), ("Garden rocket", "Arugula"), ("Rocket salad", "Arugula"), ("Salad rocket", "Arugula"), ("Palak", "Spinach"), ("Amrud", "Guavas"),
           ("Sitaphal", "Sugar-apples"), ("Ber", "Indian jujube"), ("Lauki", "White-flowered gourd"), ("Tindora", "Ivy gourd"), ("Kundri", "Ivy gourd"), ("Arvi", "Taro"),
           ("Chikoo", "Sapodilla"), ("Chiku", "Sapodilla"), ("Sapota", "Sapodilla")]]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", FRUITS)
def test_fruit_head_matches_plain_fruit_row(name, form):
    assert g(form.format(name)) == g(form.format("Cantaloupe melons")), (name, form)


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name,target", ALIASES)
def test_alias_matches_head(name, target, form):
    assert g(form.format(name)) == g(form.format(target)), (name, form)


@pytest.mark.parametrize("name", FRUITS + [a for a, _ in ALIASES])
def test_plain_group_1(name):
    assert g(name) == 1


def test_black_plum_and_gherkin_stay_unrecognised():
    for t in ["Black plum", "Gherkin", "Loofah", "Petha", "Mosambi"]:
        assert g(t) is None
