"""names-24 (India-relevant): amla head (FAO Group 1 fruit; PROTA4U identity) and sourced English-name aliases brinjal, aubergine, radish, mooli, daikon, chinese radish, japanese radish, lady's finger, ash gourd, wax gourd, white gourd, dasheen, eddoe, aonla, emblic myrobalan. Every probed form equals the target row."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "Dried {}", "Roasted {}", "{} (Sugar)", "{} 100%", "{} powder", "{} extract", "Instant {}", "Decaffeinated {}", "{} flavour", "{} leaves", "{} bags", "Iced {}", "{} concentrate", "Cooked {}", "{} (Salt)", "Milk, {}", "{}, Milk"]


ALIASES = [('Brinjal', 'Eggplant'), ('Aubergine', 'Eggplant'), ('Radish', 'Radishes'), ('Mooli', 'Radishes'), ('Daikon', 'Radishes'), ('Chinese radish', 'Radishes'), ('Japanese radish', 'Radishes'), ("Lady's finger", 'Okra'), ('Lady’s finger', 'Okra'), ('Ash gourd', 'Waxgourd'), ('Wax gourd', 'Waxgourd'), ('White gourd', 'Waxgourd'), ('Dasheen', 'Taro'), ('Eddoe', 'Taro'), ('Aonla', 'Amla'), ('Emblic myrobalan', 'Amla')]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name,target", ALIASES)
def test_alias_matches_target(name, target, form):
    assert g(form.format(name)) == g(form.format(target)), (name, form)


@pytest.mark.parametrize("form", FORMS)
def test_amla_matches_a_plain_fruit_row(form):
    assert g(form.format("Amla")) == g(form.format("Cantaloupe melons")), form


@pytest.mark.parametrize("name", ["Amla"] + [a for a, _ in ALIASES])
def test_plain_group_1(name):
    assert g(name) == 1


@pytest.mark.parametrize("name", ["Cocoyam", "Winter melon", "Drumstick", "Moringa", "Capsicum"])
def test_deliberately_unaliased_names_abstain(name):
    assert g(name) is None
