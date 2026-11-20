"""Fixes from the diagnostic review and a real photo (a millet puff pack, tests/fixtures/millet_puff_label.jpg).

MILLET_PUFF is the list as printed on that photo, typed by hand (a real label, not synthetic). The
same-line fixtures are SYNTHETIC variants invented for these tests.
"""
import pytest

from foodscan.normalise import normalise_ingredient
from foodscan.parser import parse_ingredient_list
from foodscan.pipeline import analyse_text

MILLET_PUFF = (
    "INGREDIENTS:\nPuff 88%: Supergrain Blend (Jowar, Foxtail Millet,\nCorn, Rice)(72%), Rice Bran Oil(16%).\n"
    "Seasoning 12%: Vegetables and Spices (Onion,\nGarlic, Tomato, Chilli, Amchur, Tamarind), Salt,\n"
    "Natural and Nature Identical Flavours, Raw Sugar,\nAcidity Regulators(INS330, INS296, INS334),\n"
    "Potassium Chloride - Salt Substitute (INS 508),\nRosemary Extract - Antioxidant (INS 392).\n"
    "THIS PRODUCT CONTAINS 37% MILLETS"
)
# SYNTHETIC: the review's snack label with no full stop and no line break before "Seasoning :"
SAME_LINE = ("Ingredients: Base Mix(57%)(Beetroot, Carrot, Rice, Urad Dal), Sabudana Flour, Potato Flour, Rice Bran Oil "
             "Seasoning : Dehydrated Vegetables(Garlic, Onion, Tomato), Iodised Salt, Natural & Nature Identical Flavours")


# ---- percentage in a section label ("Seasoning 12%:") -------------------------------------------------
def test_section_labels_with_percentages_are_sections():
    p = parse_ingredient_list(MILLET_PUFF)
    assert [s.label for s in p.sections] == ["Puff 88%", "Seasoning 12%"]
    assert p.sections[0].items == ["Supergrain Blend (Jowar, Foxtail Millet, Corn, Rice)(72%)", "Rice Bran Oil(16%)"]
    assert p.sections[1].items[0].startswith("Vegetables and Spices (Onion")
    assert p.sections[1].items[-1] == "Rosemary Extract - Antioxidant (INS 392)"
    assert p.declarations == ["CONTAINS 37% MILLETS"]
    assert not any("THIS PRODUCT" in i for i in p.items)


def test_millet_puff_is_group4_from_the_seasoning_section():
    a = analyse_text(MILLET_PUFF, source="text")
    assert a.answered and a.group == 4, a.reason
    flavours = [d for d in a.drivers if "Flavours" in d.ingredient]
    assert flavours and all(d.section == "Seasoning 12%" for d in flavours)
    assert {"330", "296", "334", "508", "392"} <= {u.code for u in a.ins_mappings}


def test_percentage_label_does_not_turn_a_food_into_a_label():
    p = parse_ingredient_list("Ingredients: Rice, salt. Salt 5%: sugar, flavour.")
    assert p.items == ["Rice", "salt"]            # "Salt" is a recognised food, so this is not a section label


# ---- label on the same line, no full stop, no line break ---------------------------------------------
def test_same_line_section_label_is_split_and_the_oil_survives():
    p = parse_ingredient_list(SAME_LINE)
    assert [s.label for s in p.sections] == [None, "Seasoning"]
    assert "Rice Bran Oil" in p.sections[0].items
    assert not any(":" in i for i in p.items)
    a = analyse_text(SAME_LINE)
    assert a.group == 4 and any(d.section == "Seasoning" for d in a.drivers)


def test_unknown_prefix_is_not_guessed_but_flagged():
    t = "Ingredients: Rice, Mystery Paste Seasoning : Onion, salt."
    p = parse_ingredient_list(t)
    assert "Mystery Paste Seasoning : Onion" in p.items            # not split: prefix not recognised
    a = analyse_text(t)
    assert not a.answered
    assert any("section label" in w for w in a.warnings)


def test_additive_class_label_mid_item_is_not_peeled():
    p = parse_ingredient_list("Ingredients: Rice, Rice Bran Oil Colour : INS 150d.")
    assert p.items == ["Rice", "Rice Bran Oil Colour : INS 150d"]


# ---- OCR misread of "Oil" as "O11" seen on the real photo --------------------------------------------
def test_ocr_o11_is_read_as_oil():
    assert normalise_ingredient("Rice Bran O11 (16%)").name == "rice bran oil"
    assert normalise_ingredient("Edible Vegetable O11").name == "edible vegetable oil"


@pytest.mark.parametrize("word", ["Oiled", "Boil", "O1l1"])
def test_o11_rule_does_not_touch_other_words(word):
    assert normalise_ingredient(word).name == word.lower()
