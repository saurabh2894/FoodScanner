"""general-24s: six Hindi-name aliases of existing rows (IISc India Flora). Every alias equals its English head in every probed form."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "Dried {}", "Roasted {}", "{} (Sugar)", "{} 100%", "{} powder", "{} extract", "Instant {}", "Decaffeinated {}", "{} flavour", "{} leaves", "{} bags", "Iced {}", "{} concentrate", "Cooked {}", "{} (Salt)", "Milk, {}", "{}, Milk"]

ALIASES = [("Gajar", "Carrots"), ("Matar", "Peas"), ("Adarak", "Ginger"), ("Tamatar", "Tomato"), ("Santra", "Mandarin"), ("Seb", "Apples")]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name,target", ALIASES)
def test_alias_matches_head(name, target, form):
    assert g(form.format(name)) == g(form.format(target)), (name, form)


@pytest.mark.parametrize("t", ["Gajar halwa", "Matar paneer", "Tamatar ketchup", "Seb juice", "Santra juice", "Adrak", "Kaddu", "Aloo"])
def test_compound_and_unsourced_names_match_their_english_reading_or_abstain(t):
    ans = g(t)
    assert ans is None or ans == g(t.replace("Gajar", "Carrot").replace("Matar", "Pea").replace("Tamatar", "Tomato").replace("Seb", "Apple").replace("Santra", "Mandarin")), t
