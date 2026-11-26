"""names-24b (India-relevant, aliases only, no new head): PROTA4U/FDC-named aliases lablab, wing bean, goa bean, black-eye pea forms, ceylon spinach, malabar nightshade, vine spinach, basella, water chestnuts. Two candidate heads were dropped because rows already existed (vinespinach, waterchestnuts). Every probed form equals the target row."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "Dried {}", "Roasted {}", "{} (Sugar)", "{} 100%", "{} powder", "{} extract", "Instant {}", "Decaffeinated {}", "{} flavour", "{} leaves", "{} bags", "Iced {}", "{} concentrate", "Cooked {}", "{} (Salt)", "Milk, {}", "{}, Milk"]


ALIASES = [('Lablab', 'Hyacinth beans'), ('Lablab bean', 'Hyacinth beans'), ('Lablab beans', 'Hyacinth beans'), ('Wing bean', 'Winged beans'), ('Wing beans', 'Winged beans'), ('Goa bean', 'Winged beans'), ('Black-eye pea', 'Cowpeas'), ('Black-eye peas', 'Cowpeas'), ('Black-eyed pea', 'Cowpeas'), ('Black-eyed peas', 'Cowpeas'), ('Black eyed peas', 'Cowpeas'), ('Black-eye bean', 'Cowpeas'), ('Vine spinach', 'Vinespinach'), ('Ceylon spinach', 'Vinespinach'), ('Malabar nightshade', 'Vinespinach'), ('Basella', 'Vinespinach'), ('Water chestnuts', 'Waterchestnuts')]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name,target", ALIASES)
def test_alias_matches_target(name, target, form):
    assert g(form.format(name)) == g(form.format(target)), (name, form)


@pytest.mark.parametrize("name", [a for a, _ in ALIASES])
def test_plain_group_1(name):
    assert g(name) == 1


@pytest.mark.parametrize("name", ["Indian spinach", "Asparagus pea", "Singhara"])
def test_deliberately_unaliased_names_abstain(name):
    assert g(name) is None
