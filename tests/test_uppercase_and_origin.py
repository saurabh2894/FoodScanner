"""Shouted labels: an uppercase AND must split a pair like lowercase 'and'; a bare INS code after
'<class> of <origin words>' is still read (generic wording, no product-specific strings)."""
from foodscan.pipeline import analyse_text


def test_uppercase_and_splits_pair_and_codes_resolve():
    a = analyse_text("Ingredients: SUGAR, EMULSIFIER OF VEGETABLE ORIGIN [472e] AND FLOUR TREATMENT AGENT [1101(ii)].", source="text")
    assert len(a.ingredients) == 3
    assert {u.code for u in a.ins_mappings} == {"472e", "1101(ii)"}


def test_uppercase_and_inside_a_group_name_stays_whole():
    a = analyse_text("Ingredients: Sugar, SPICES AND CONDIMENTS, salt.", source="text")
    assert "SPICES AND CONDIMENTS" in a.ingredients


def test_class_of_origin_then_bare_code():
    a = analyse_text("Ingredients: Sugar, colour of natural origin (160b), salt.", source="text")
    assert any(u.code == "160b" for u in a.ins_mappings)
