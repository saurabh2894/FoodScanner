"""algae-24: kelp, laver, wakame, spirulina behave like the existing mushroom (fungi) rows in every probed form."""
import pytest
from foodscan.pipeline import analyse_text


def res(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}, Salt", "Dried {}, Salt", "{} powder, Salt", "{} extract, Salt", "{}, Oil, Salt", "{} (5%), Water", "Rice, {}", "{} tablets", "{} snack"]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", ["Kelp", "Laver", "Wakame", "Spirulina"])
def test_matches_shiitake_in_every_form(form, name):
    assert res(form.format(name)) == res(form.format("Shiitake mushrooms"))


@pytest.mark.parametrize("name", ["Kelp", "Laver", "Wakame", "Spirulina"])
def test_plain_with_salt_is_group_3_and_flavour_is_group_4(name):
    assert res(f"{name}, Salt") == 3
    assert res(f"{name} flavour") == 4
