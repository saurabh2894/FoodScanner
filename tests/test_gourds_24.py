"""gourds-24 (India-relevant): snake gourd, ridged gourd, ivy gourd and tinda heads (FAO Group 1 definition placement; PROTA4U identity) and aliases bottle gourd, calabash gourd, bitter melon, karela, ridge gourd, tindori. Every probed form equals the comparison row."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "Dried {}", "Roasted {}", "{} (Sugar)", "{} 100%", "{} powder", "{} extract", "Instant {}", "Decaffeinated {}", "{} flavour", "{} leaves", "{} bags", "Iced {}", "{} concentrate", "Cooked {}", "{} (Salt)", "Milk, {}", "{}, Milk"]


VEG = ["Snake gourd", "Ridged gourd", "Ivy gourd", "Tinda"]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", VEG)
def test_new_vegetable_head_matches_okra(name, form):
    assert g(form.format(name)) == g(form.format("Okra")), (name, form)


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name,target", [("Bottle gourd", "White-flowered gourd"), ("Calabash gourd", "White-flowered gourd"), ("Bitter melon", "Balsam-pear"), ("Karela", "Balsam-pear"), ("Ridge gourd", "Ridged gourd"), ("Tindori", "Ivy gourd")])
def test_alias_matches_target(name, target, form):
    assert g(form.format(name)) == g(form.format(target)), (name, form)


@pytest.mark.parametrize("name", VEG + ["Bottle gourd", "Calabash gourd", "Bitter melon", "Karela", "Ridge gourd", "Tindori"])
def test_plain_group_1(name):
    assert g(name) == 1


def test_bare_calabash_is_not_aliased():
    assert g("Calabash") is None
