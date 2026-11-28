"""general-25f: arrowroot starch (FAO Group 2 starches; FSSAI 2.4.14(1) defines arrowroot as the purified starch) and maize flour (FAO Group 1 flour made from corn; FSSAI 2.4.21 Whole Maize (Corn) Flour), plus name aliases arrowroot, whole maize/corn flour, sultana(s) (Codex CXS 67 7.1.1) and finger millet (FSSAI 2.4.6). Held with reasons: chana sattu / roasted bengal gram flour (the existing aliases chana and bengal gram rewrite inside the new name, an engine-lane collision), bare sattu and bare corn flour (other grains / UK corn starch), arrowroot root forms, tapioca sago (no NOVA clause)."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


def un(t):
    return bool(analyse_text("Ingredients: " + t + ".", source="text").unassessed)


STARCH = ["Arrowroot starch", "Arrowroot"]
FLOUR = ["Maize flour", "Whole maize flour", "Whole corn flour"]


@pytest.mark.parametrize("t", STARCH)
def test_arrowroot_is_a_culinary_ingredient_group_2(t):
    assert g(t) == 2


@pytest.mark.parametrize("t", STARCH)
def test_arrowroot_with_salt_in_a_list_is_not_unassessed(t):
    assert not un("Cashew nuts, " + t + ", Salt")


@pytest.mark.parametrize("t", FLOUR + ["Sultanas", "Sultana", "Finger millet"])
def test_plain_group_1(t):
    assert g(t) == 1


@pytest.mark.parametrize("t", ["Sultana, Sugar", "Sultanas, Salt"])
def test_sultana_with_sugar_or_salt_group_3(t):
    assert g(t) == 3


@pytest.mark.parametrize("t", STARCH + FLOUR)
def test_flavour_added_is_group_4(t):
    assert g("Wheat flour, " + t + ", Salt, Flavour") == 4


def test_aliases_and_heads_agree():
    assert g("Arrowroot") == g("Arrowroot starch")
    assert g("Whole corn flour") == g("Maize flour")
    assert g("Sultana") == g("Sultanas") == g("Raisins")
    assert g("Finger millet") == g("Ragi")


@pytest.mark.parametrize("t", ["Arrowroot root", "Arrowroot tuber", "Arrowroot biscuit", "Corn flour", "Sattu", "Chana sattu", "Tapioca pearls", "Sabudana"])
def test_held_forms_stay_unrecognised(t):
    assert un(t) or g(t) is None
