"""lemon-grass-24: lemon grass behaves like the existing herb rows (thyme) in every probed form; lemongrass is a spelling synonym."""
import pytest
from foodscan.pipeline import analyse_text


def res(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return (a.group if a.answered else None)


FORMS = ["{}", "{}, Salt", "Rice, {}", "{} (5%), Rice", "Dried {}, Rice", "{} powder, Rice", "{} paste, Rice", "{} extract, Rice", "{} oil", "{} flavour", "Water, {}, Sugar", "{}, Ginger, Salt"]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", ["Lemon grass", "Lemongrass"])
def test_matches_thyme_in_every_form(form, name):
    assert res(form.format(name)) == res(form.format("Thyme"))


def test_flavour_form_still_group_4():
    assert res("Lemongrass flavour") == 4
