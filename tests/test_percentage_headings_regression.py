"""Percentage-bearing section headings and silent ingredient loss (reported against the live deployment).

REAL_LABEL is the text of a real millet puff pack (tests/fixtures/millet_puff_label.jpg), typed from the
photo. Controls B, C and D are variants of it. The generated inputs at the bottom are SYNTHETIC.

Property pinned here: no part of the input is silently discarded. Every word after the "Ingredients" heading
is either in an extracted ingredient, a section label, a "Contains" declaration, text after a stop phrase
(Contains / Allergen / Manufactured / Best before / Nutrition ...), or in the explicit `ignored` list.
"""
import random
import re

import pytest

from foodscan import cli
from foodscan.parser import _LEAD_IN, _STOP, parse_ingredient_list
from foodscan.pipeline import analyse_text

SECTION_1 = "Puff 88%: Supergrain Blend (Jowar, Foxtail Millet, Corn, Rice)(72%), Rice Bran Oil (16%)."
SECTION_2 = ("Seasoning 12%: Vegetables and Spices (Onion, Garlic, Tomato, Chilli, Amchur, Tamarind), Salt, "
             "Natural and Nature Identical Flavours, Raw Sugar, Acidity Regulators (INS330, INS296, INS334), "
             "Potassium Chloride - Salt Substitute (INS 508), Rosemary Extract - Antioxidant (INS 392).")
CLAIM = "THIS PRODUCT CONTAINS 37% MILLETS"

REAL_LABEL = f"Ingredients: {SECTION_1} {SECTION_2} {CLAIM}"                                  # A
PLAIN_HEADINGS = REAL_LABEL.replace("Puff 88%:", "Puff:").replace("Seasoning 12%:", "Seasoning:")   # B
SINGLE_PERCENT = "Seasoning 12%: Salt, Raw Sugar, Natural and Nature Identical Flavours."           # C
SWAPPED = f"Ingredients: {SECTION_2} {SECTION_1} {CLAIM}"                                           # D


def heading_text_in_items(p):
    return [i for i in p.items if ":" in i or re.search(r"\b(Puff|Seasoning)\b\s*\d*%?\s*$", i.split("(")[0].strip())]


def test_A_exact_label_all_nine_ingredients_two_sections_group4():
    p = parse_ingredient_list(REAL_LABEL)
    assert len(p.items) == 9
    assert [s.label for s in p.sections] == ["Puff 88%", "Seasoning 12%"]
    assert [len(s.items) for s in p.sections] == [2, 7]
    assert not heading_text_in_items(p)
    assert p.items[0] == "Supergrain Blend (Jowar, Foxtail Millet, Corn, Rice)(72%)"
    assert not any("THIS PRODUCT" in i or "MILLETS" in i for i in p.items)
    a = analyse_text(REAL_LABEL, source="text")
    assert a.answered and a.group == 4
    assert any("Flavours" in d.ingredient and d.section == "Seasoning 12%" for d in a.drivers)


def test_B_plain_headings_same_result_as_percentage_headings():
    p = parse_ingredient_list(PLAIN_HEADINGS)
    assert len(p.items) == 9 and [s.label for s in p.sections] == ["Puff", "Seasoning"]
    assert not heading_text_in_items(p)
    assert analyse_text(PLAIN_HEADINGS, source="text").group == 4
    assert p.items == parse_ingredient_list(REAL_LABEL).items          # headings differ, ingredients identical


def test_C_single_percentage_heading_is_not_glued_into_item_one():
    p = parse_ingredient_list(SINGLE_PERCENT, assume_list=True)
    assert p.items == ["Salt", "Raw Sugar", "Natural and Nature Identical Flavours"]
    assert [s.label for s in p.sections] == ["Seasoning 12%"]
    assert not heading_text_in_items(p)
    assert analyse_text(SINGLE_PERCENT, source="text").group == 4


def test_D_order_swapped_nothing_is_dropped():
    p = parse_ingredient_list(SWAPPED)
    assert len(p.items) == 9
    assert [s.label for s in p.sections] == ["Seasoning 12%", "Puff 88%"]
    assert [len(s.items) for s in p.sections] == [7, 2]
    assert not heading_text_in_items(p)
    assert analyse_text(SWAPPED, source="text").group == 4


@pytest.mark.parametrize("text", [REAL_LABEL, PLAIN_HEADINGS, SWAPPED])
def test_the_claim_line_is_not_an_ingredient(text):
    p = parse_ingredient_list(text)
    assert p.declarations == ["CONTAINS 37% MILLETS"]


# ---- never drop a segment silently ---------------------------------------------------------------------------
def test_unlabelled_text_after_a_full_stop_is_flagged_not_dropped():
    t = "Ingredients: Rice, salt. Sugar, natural flavour."
    p = parse_ingredient_list(t)
    assert p.items == ["Rice", "salt"]
    assert p.ignored == ["Sugar, natural flavour."]
    a = analyse_text(t)
    assert a.ignored == ["Sugar, natural flavour."]
    assert not a.answered and "looks like more ingredients" in a.reason     # a Group 3 call would hide the flavour marker
    assert any("not read as ingredients" in w for w in a.warnings)


def test_ignored_text_that_looks_like_more_ingredients_cannot_end_in_group1_to_3():
    for t in ["Ingredients: Rice, salt. Sugar, vinegar.", "Ingredients: Rice, salt. Khaand, amchur, tamarind."]:
        a = analyse_text(t)
        assert not a.answered, t


def test_group4_stands_when_a_marker_is_already_present_but_the_text_is_flagged():
    a = analyse_text("Ingredients: Rice, natural flavour. Sugar, vinegar.")
    assert a.answered and a.group == 4
    assert any("looks like more of the list" in w for w in a.warnings)
    assert a.ignored == ["Sugar, vinegar."]


@pytest.mark.parametrize("tail, unread", [
    ("Enjoy hot with butter.", ["Enjoy hot with butter."]),
    ("Directions: add hot water, stir.", ["Directions: add hot water, stir."]),
    ("*As flavouring agent.", ["*As flavouring agent."]),
    ("Serving suggestion: with butter.", ["Serving suggestion: with butter."]),
    # "store in" is a stop phrase: it takes the "Note:" label with it, so the whole sentence is stop-phrase tail
    ("Note: store in a cool place, away from light.", []),
])
def test_prose_footnotes_and_directions_do_not_change_the_verdict(tail, unread):
    a = analyse_text("Ingredients: Rice, salt. " + tail)
    assert a.answered and a.group == 3
    assert a.ignored == unread and a.warnings == []


def test_nothing_ignored_when_everything_was_read():
    for t in (REAL_LABEL, PLAIN_HEADINGS, SWAPPED, SINGLE_PERCENT, "Ingredients: Milk"):
        assert parse_ingredient_list(t, assume_list=True).ignored == [], t


def test_cli_prints_the_unread_text(tmp_path, capsys):
    f = tmp_path / "l.txt"
    f.write_text("Ingredients: Rice, salt. Enjoy hot with butter.")
    cli.main(["classify", "--text", str(f)])
    out = capsys.readouterr().out
    assert "Not read as ingredients" in out and "Enjoy hot with butter" in out


# ---- the property: coverage ---------------------------------------------------------------------------------
def words(s):
    return set(re.findall(r"[a-z]+", s.lower()))


def uncovered_words(text):
    """Words after the heading that are in no ingredient, label, declaration, ignored text or stop-phrase tail."""
    m = re.search(r"ingredients?\s*[:\-]?\s*", text, re.I)
    body = text[m.end():] if m else text
    stop = _STOP.search(body)
    lead = _LEAD_IN.search(body[: stop.start()]) if stop else None      # a stop phrase takes its lead-in with it
    tail = body[(lead.start(1) if lead else stop.start()):] if stop else ""
    p = parse_ingredient_list(text, assume_list=True)
    seen = set()
    for s in p.sections:
        seen |= words(s.label or "")
        for it in s.items:
            seen |= words(it)
    for part in p.declarations + p.ignored:
        seen |= words(part)
    return words(body) - seen - words(tail)


FIXED = [REAL_LABEL, PLAIN_HEADINGS, SWAPPED, SINGLE_PERCENT,
         "Ingredients: Rice, salt. Sugar, natural flavour.", "Ingredients: Rice, salt. Enjoy hot with butter.",
         "Ingredients: Rice, Rice Bran Oil Seasoning : Onion, Garlic, Flavour.",
         "Ingredients: Rice. Seasoning 12%: Salt. Enjoy hot. Coating: Sugar."]


@pytest.mark.parametrize("text", FIXED)
def test_no_word_is_silently_dropped_fixed_inputs(text):
    assert uncovered_words(text) == set(), text


def test_no_word_is_silently_dropped_generated_inputs():
    """SYNTHETIC: 400 random combinations of labelled / percentage / unlabelled / prose segments."""
    rng = random.Random(20261120)
    labels = ["", "", "Seasoning: ", "Puff 88%: ", "Noodles: ", "Masala tastemaker: ", "Coating 12.5%: ", "Tastemaker 5%: ", "Note: ", "Directions: "]
    bodies = ["Rice, salt", "Sugar, natural flavour", "Wheat flour, palm oil (palmolein), stabiliser (INS 452(i))", "Enjoy hot with butter",
              "mixed spices, flavour enhancers (INS 627, INS 631), colour (INS 150d)", "Milk", "Khaand, amchur, tamarind"]
    tails = ["", "", " Contains wheat.", " THIS PRODUCT CONTAINS 37% MILLETS", " Manufactured by Example Foods."]
    for _ in range(400):
        n = rng.randint(1, 4)
        segs = [rng.choice(labels) + rng.choice(bodies) for _ in range(n)]
        sep = rng.choice([". ", ".\n", "\n", ". "])
        text = "Ingredients: " + sep.join(segs) + rng.choice([".", ""]) + rng.choice(tails)
        assert uncovered_words(text) == set(), text
