"""india-24 (India-relevant): pointed gourd, cluster beans and bael heads (FAO Group 1 placement; Purdue NewCROP and PROSEA identity) and aliases parwal, palwal, parmal, cluster bean, bengal quince. Every probed form equals the comparison row."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "Dried {}", "Roasted {}", "{} (Sugar)", "{} 100%", "{} powder", "{} extract", "Instant {}", "Decaffeinated {}", "{} flavour", "{} leaves", "{} bags", "Iced {}", "{} concentrate", "Cooked {}", "{} (Salt)", "Milk, {}", "{}, Milk"]


ALIASES = [('Parwal', 'Pointed gourd'), ('Palwal', 'Pointed gourd'), ('Parmal', 'Pointed gourd'), ('Cluster bean', 'Cluster beans'), ('Bengal quince', 'Bael'), ('Star fruit', 'Carambola'), ('Starfruit', 'Carambola'), ('Karonda', 'Karanda'), ('Karaunda', 'Karanda')]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name,target", ALIASES)
def test_alias_matches_target(name, target, form):
    assert g(form.format(name)) == g(form.format(target)), (name, form)


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", ["Pointed gourd", "Cluster beans"])
def test_new_vegetable_head_matches_okra(name, form):
    assert g(form.format(name)) == g(form.format("Okra")), (name, form)


@pytest.mark.parametrize("form", FORMS)
def test_bael_matches_a_plain_fruit_row(form):
    assert g(form.format("Bael")) == g(form.format("Cantaloupe melons")), form
    assert g(form.format("Karanda")) == g(form.format("Cantaloupe melons")), form
    assert g(form.format("Phalsa")) == g(form.format("Cantaloupe melons")), form


@pytest.mark.parametrize("name", ["Pointed gourd", "Cluster beans", "Bael", "Karanda", "Phalsa"] + [a for a, _ in ALIASES])
def test_plain_group_1(name):
    assert g(name) == 1


@pytest.mark.parametrize("name", ["Guar", "Guar gum", "Wood apple", "Sirphal"])
def test_deliberately_unaliased_names_do_not_take_group_1(name):
    assert g(name) != 1
