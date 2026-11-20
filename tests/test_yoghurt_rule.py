"""Narrow milk-plus-starter-culture rule (research/04): the whole list is recognised and is only milk plus cultures -> Group 1.
Everything else keeps its current behaviour. Nothing is keyed off the product words yoghurt, dahi or curd."""
import pytest

from foodscan.pipeline import analyse_text


def a(t):
    return analyse_text(t, source="text")


@pytest.mark.parametrize("text", [
    "Pasteurized Toned Milk & Active Lactic Culture",
    "Ingredients: Milk, live cultures.",
    "Ingredients: Double toned milk, active culture.",
    "Ingredients: Milk, yoghurt culture, lactic culture.",
])
def test_plain_milk_plus_cultures_is_group_1_and_cites_the_nova_source(text):
    r = a(text)
    assert r.answered and r.group == 1, text
    assert all("NUPENS-USP" in d.source for d in r.drivers) and "starter culture" in r.drivers[0].detail


def test_one_unrecognised_item_abstains():
    r = a("Ingredients: Toned milk, active culture, xyzgum.")
    assert not r.answered and r.group is None


@pytest.mark.parametrize("text, expect", [
    ("Ingredients: Milk, active culture, sugar.", 3),                          # unchanged: milk + a culinary ingredient is group 3
    ("Ingredients: Milk, active culture, salt.", 3),
    ("Ingredients: Milk, active culture, sweetener (INS 950).", 4),            # marker rules still apply
    ("Ingredients: Milk, active culture, added flavour.", 4),
    ("Ingredients: Milk, active culture, emulsifier (INS 471).", 4),
    ("Ingredients: Milk, active culture, stabilizer (INS 440).", None),        # weak/unlisted marker: still uncertain
])
def test_other_milk_and_culture_lists_keep_their_current_behaviour(text, expect):
    r = a(text)
    assert (r.group if r.answered else None) == expect, text


@pytest.mark.parametrize("text", [
    "Ingredients: Dahi, active culture.",                  # product words do not trigger the rule
    "Ingredients: Active culture.",                        # culture alone
    "Ingredients: Milk, water.",                           # not a culture
    "Ingredients: Water, active culture.",
])
def test_the_rule_is_not_keyed_off_product_words_or_partial_lists(text):
    assert not a(text).answered


def test_single_milk_and_single_dahi_keep_their_existing_group_1():
    assert a("Ingredients: Milk.").group == 1 and a("Ingredients: Dahi.").group == 1
