"""general-24n: one plain fruit head (kaith) and twelve Hindi alias names from IISc India Flora (the singular "curry leaf" alias is deliberately not added: see test_plural_synonyms_1). Every probed form equals the comparison row; every alias equals its head."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "Dried {}", "Roasted {}", "{} (Sugar)", "{} 100%", "{} powder", "{} extract", "Instant {}", "Decaffeinated {}", "{} flavour", "{} leaves", "{} bags", "Iced {}", "{} concentrate", "Cooked {}", "{} (Salt)", "Milk, {}", "{}, Milk"]

FRUITS = ["Kaith"]
ALIASES = [("Bhindi", "Okra"), ("Khira", "Cucumber"), ("Jameenkand", "Elephant yam"), ("Suvaran", "Elephant yam"), ("Kamarak", "Carambola"), ("Anar", "Pomegranates"), ("Papeeta", "Papayas"), ("Kathal", "Jackfruit"),
           ("Chukandar", "Beetroot"), ("Shakar kendi", "Sweet potatoes"), ("Chakotra", "Pummelo"), ("Curry pattha", "Curry leaves")]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", FRUITS)
def test_fruit_head_matches_guava(name, form):
    assert g(form.format(name)) == g(form.format("Guavas")), (name, form)


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name,target", ALIASES)
def test_alias_matches_head(name, target, form):
    assert g(form.format(name)) == g(form.format(target)), (name, form)


@pytest.mark.parametrize("name", FRUITS + [a for a, _ in ALIASES if a != "Curry pattha"])
def test_plain_group_1(name):
    assert g(name) == 1


def test_unaliased_names_stay_unrecognised():
    # general-24z: wood apple removed from this stale expected gap; it now has its own head row (Purdue/Morton identity and raw-pulp use). Elephant apple (Dillenia) stays unrecognised.
    for t in ["Elephant apple", "Sadaphal", "Ladyfinger"]:
        assert g(t) is None
