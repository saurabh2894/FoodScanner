"""dried-fruit-24 and produce-gaps-24: new rows behave like their nearest existing row in every probed form."""
import pytest
from foodscan.pipeline import analyse_text


def res(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "{}, Sugar", "{}, Oil", "{}, Sunflower oil", "Dried {}", "{} powder", "{} juice", "{} puree", "{} paste", "Rice, {}", "{} in brine", "Canned {}", "Pickled {}", "{}, Sulphur dioxide (INS 220)", "{} flavour", "Fried {}", "{} (5%), Water"]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", ["Raisins", "Prunes"])
def test_dried_fruit_matches_dried_apricots(form, name):
    assert res(form.format(name)) == res(form.format("Dried apricots")) or form == "Dried {}"


@pytest.mark.parametrize("form", [f for f in FORMS if f not in ("{}", "Dried {}")])
@pytest.mark.parametrize("name", ["Jicama", "Water chestnuts", "Cloud ears", "Goji berries", "Sapote", "Hearts of palm", "Fiddlehead ferns"])
def test_produce_matches_shiitake_in_processed_forms(form, name):
    assert res(form.format(name)) == res(form.format("Shiitake mushrooms"))


@pytest.mark.parametrize("name", ["Raisins", "Prunes", "Jicama", "Water chestnuts", "Cloud ears", "Goji berries", "Sapote", "Hearts of palm", "Fiddlehead ferns"])
def test_with_salt_is_group_3_and_flavour_is_group_4(name):
    assert res(f"{name}, Salt") == 3 and res(f"{name} flavour") == 4
