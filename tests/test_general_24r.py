"""general-24r: cubeb (herb_spice) and tiger nut (vegetable, tuber) heads and the chufa alias. Every probed form equals the comparison row of the same kind; the alias equals its head."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "Dried {}", "Roasted {}", "{} (Sugar)", "{} 100%", "{} powder", "{} extract", "Instant {}", "Decaffeinated {}", "{} flavour", "{} leaves", "{} bags", "Iced {}", "{} concentrate", "Cooked {}", "{} (Salt)", "Milk, {}", "{}, Milk"]

SPICES = ["Cubeb"]
VEGS = ["Tiger nut"]
ALIASES = [("Chufa", "Tiger nut")]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", SPICES)
def test_spice_head_matches_cumin(name, form):
    assert g(form.format(name)) == g(form.format("Cumin")), (name, form)


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", VEGS)
def test_veg_head_matches_okra(name, form):
    assert g(form.format(name)) == g(form.format("Okra")), (name, form)


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name,target", ALIASES)
def test_alias_matches_head(name, target, form):
    assert g(form.format(name)) == g(form.format(target)), (name, form)


def test_tiger_nut_plain_group_1():
    assert g("Tiger nut") == 1 and g("Chufa") == 1


def test_unaliased_names_stay_unrecognised():
    for t in ["Tigernut", "Earth almond", "Tailed pepper"]:
        assert g(t) is None
