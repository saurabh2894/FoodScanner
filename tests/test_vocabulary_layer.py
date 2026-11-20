"""Priority 1 of the first unseen-label evaluation: ordinary ingredients under ordinary wordings.

These tests use wordings of MY OWN choosing, not the evaluated labels: the point is a general normalisation layer
(descriptor words, singular/plural, regional synonyms), not strings added for particular products.
"""
import pytest

from foodscan.classify import lookup
from foodscan.pipeline import analyse_text


def group(text):
    a = analyse_text("Ingredients: " + text, source="text")
    return a.group if a.answered else None


@pytest.mark.parametrize("wording", ["oats", "oat", "Rolled Oats", "rolled oat flakes", "Whole Oats", "organic rolled oats", "oat flakes",
                                     "Flaked Oats", "steamed rolled oats"])
def test_plain_oats_in_any_ordinary_wording_is_group1(wording):
    assert group(wording) == 1, wording


@pytest.mark.parametrize("wording", ["moong dal", "mung bean splits", "split green gram", "mung dal", "Mung Beans", "husked moong dal",
                                     "toor dal", "arhar dal", "red gram split", "black gram", "bengal gram dal", "red lentil", "masoor dal split"])
def test_plain_pulses_in_regional_wordings_are_group1(wording):
    assert group(wording) == 1, wording


@pytest.mark.parametrize("wording", ["salt", "edible common salt", "iodised salt", "table salt", "black salt", "kala namak", "rock salt",
                                     "sendha namak", "sea salt", "refined sugar", "white sugar", "brown sugar", "powdered sugar", "butter",
                                     "pasteurised butter", "salted butter", "refined palm oil", "palmolein", "cold pressed sesame oil", "extra virgin olive oil"])
def test_plain_culinary_ingredients_are_group2(wording):
    assert group(wording) == 2, wording


def test_plain_dal_fried_in_oil_with_salts_is_group3():
    assert group("mung bean splits, edible vegetable oil, edible common salt, black salt") == 3
    assert group("Split green gram, refined palm oil, table salt") == 3


def test_oats_with_sugar_and_salt_is_group3_not_forced_higher():
    assert group("rolled oats, sugar, salt") == 3


# ---- the layer must not over-reach ---------------------------------------------------------------------
@pytest.mark.parametrize("wording", ["corn flakes", "wheat flakes", "jackfruit seed paste", "mung bean noodles", "oat protein concentrate",
                                     "rice syrup", "oat beta glucan"])
def test_descriptors_do_not_turn_processed_items_into_plain_ones(wording):
    assert group(wording) is None, wording


def test_flakes_is_not_a_descriptor_but_oat_flakes_is_an_oat_wording():
    from foodscan.normalise import normalise_ingredient

    assert lookup("corn flakes") is None and lookup("wheat flakes") is None
    assert normalise_ingredient("oat flakes").name == "oat"                  # synonym, applied in normalisation
    assert lookup(normalise_ingredient("rolled oat flakes").name)["term"] == "oat"


def test_markers_still_win_over_vocabulary():
    assert group("rolled oats, maltodextrin") == 4
    assert group("refined palm oil, hydrogenated vegetable oil") == 4
    assert group("edible common salt, anticaking agent (INS 551), emulsifier (INS 471)") == 4


def test_flour_rule_is_unchanged():
    assert group("whole wheat flour, water, salt, yeast") is None


def test_descriptor_only_is_not_an_ingredient():
    assert lookup("edible") is None and lookup("rolled split") is None


def test_lookup_reports_the_source_of_the_match():
    row = lookup("Edible Common Salt".lower())
    assert row["term"] == "salt" and row["source"]


def test_dal_alias_does_not_double_the_word():
    from foodscan.normalise import normalise_ingredient

    for wording in ["bengal gram dal", "bengal gram", "green gram dal", "red gram dal", "black gram dal"]:
        assert "dal dal" not in normalise_ingredient(wording).name, wording
