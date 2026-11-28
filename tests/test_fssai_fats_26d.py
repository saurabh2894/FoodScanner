"""fssai-fats-26d: five FSSAI 2.2 fats (poppy seed oil, salseed fat, dhupa fat, phulwara fat, goat fat) are Group 2 culinary rows like kokum fat and lard; five FSSAI name aliases route to existing rows. Held: beef fat, suet, mutton fat (FSSAI says only "fat obtained from a carcass", no rendering), margarine, fat spread, vanaspati."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


HEADS = ["Poppy seed oil", "Salseed fat", "Dhupa fat", "Phulwara fat", "Goat fat"]
ALIASES = {"Sun flower seed oil": "Sunflower oil", "Safflower seed oil": "Safflower oil", "Water-melon seed oil": "Watermelon seed oil", "Palm olein": "Palmolein", "Refined salseed fat": "Salseed fat"}


@pytest.mark.parametrize("t", HEADS)
def test_head_matches_kokum_fat(t):
    for form in ["{}", "Cashew nuts, {}, Salt", "Hydrogenated {}", "Interesterified {}", "Wheat flour, {}, Flavour", "{}, colour (150d)", "Rice, {}"]:
        assert g(form.format(t)) == g(form.format("Kokum fat")), form


@pytest.mark.parametrize("t", HEADS)
def test_plain_group_2(t):
    assert g(t) == 2


@pytest.mark.parametrize("a,target", list(ALIASES.items()))
def test_alias_follows_target(a, target):
    for form in ["{}", "Cashew nuts, {}, Salt", "Hydrogenated {}", "Wheat flour, {}, Flavour"]:
        assert g(form.format(a)) == g(form.format(target)), form
    assert g(a) == 2


@pytest.mark.parametrize("t", ["Beef fat", "Suet", "Mutton fat", "Margarine", "Fat spread", "Vanaspati", "Tallow"])
def test_held_names_stay_unrecognised(t):
    assert g(t) is None
