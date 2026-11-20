"""Data behind the additive-codes block: plural class words, and where each code was found."""
import pytest

from foodscan.normalise import normalise_ingredient
from foodscan.pipeline import analyse_text


@pytest.mark.parametrize("plural", ["Acidity Regulators", "Preservatives", "Antioxidants", "Stabilisers", "Thickeners",
                                    "Anticaking Agents", "Flour Treatment Agents", "Humectants"])
def test_plural_class_words_are_recognised(plural):
    a = analyse_text(f"Ingredients: Rice, {plural} (INS 999, INS 998), salt.")
    assert not any("group name" in u for u in a.unassessed), plural     # the heading is understood, not expanded away


def test_code_list_stays_under_its_heading():
    a = analyse_text("Ingredients: Rice, Acidity Regulators(INS330, INS296, INS334), salt.")
    assert [u.code for u in a.ins_mappings] == ["330", "296", "334"]
    assert {u.ingredient for u in a.ins_mappings} == {"Acidity Regulators(INS330, INS296, INS334)"}


def test_humectants_plural_counts_like_humectant():
    # research/02 marker class 2 names humectant agents; the plural must not slip past the singular term
    assert analyse_text("Ingredients: Rice, humectant (INS 422), salt.").group == 4
    assert analyse_text("Ingredients: Rice, humectants (INS 422), salt.").group == 4


def test_insuse_carries_what_the_table_needs():
    (u,) = normalise_ingredient("colour (INS 102)").ins
    assert u.name == "tartrazine" and u.classes == ("colour",) and u.strength == "strong" and u.ingredient == "colour (INS 102)"
    (unknown,) = normalise_ingredient("preservative (INS 999)").ins
    assert unknown.name is None and unknown.classes == () and unknown.strength is None


def test_section_travels_with_the_code():
    a = analyse_text("Ingredients: Rice. Seasoning 12%: Salt, emulsifier (INS 471).")
    (u,) = a.ins_mappings
    assert u.section == "Seasoning 12%" and u.ingredient == "emulsifier (INS 471)"
