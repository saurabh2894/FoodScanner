"""veg-24 (general): seven FDC-named raw plant foods placed Group 1 by the FAO Group 1 definition and example, plus bitter gourd, fava beans, fava bean and broad beans routed to existing rows. Every probed form must equal the comparison row."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "Dried {}", "Roasted {}", "{} (Sugar)", "{} 100%", "{} powder", "{} extract", "Instant {}", "Decaffeinated {}", "{} flavour", "{} leaves", "{} bags", "Iced {}", "{} concentrate", "Cooked {}", "{} (Salt)", "Milk, {}", "{}, Milk"]


VEG = ["Cress", "Pumpkin flowers", "Sesbania flower", "Winged bean leaves", "Winged bean tuber", "Mountain yam"]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", VEG)
def test_new_vegetable_head_matches_okra(name, form):
    assert g(form.format(name)) == g(form.format("Okra")), (name, form)


@pytest.mark.parametrize("form", FORMS)
def test_roselle_matches_cantaloupe_melons(form):
    assert g(form.format("Roselle")) == g(form.format("Cantaloupe melons")), form


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name,target", [("Bitter gourd", "Balsam-pear"), ("Fava beans", "Broadbeans"), ("Fava bean", "Broadbeans"), ("Broad beans", "Broadbeans")])
def test_alias_matches_target(name, target, form):
    assert g(form.format(name)) == g(form.format(target)), (name, form)


@pytest.mark.parametrize("name", VEG + ["Roselle", "Bitter gourd", "Fava beans", "Broad beans"])
def test_plain_group_1(name):
    assert g(name) == 1
