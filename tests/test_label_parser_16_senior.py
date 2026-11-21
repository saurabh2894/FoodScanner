"""label-parser-16 senior correction (SYNTHETIC). A footnote mark (#, ##, *, **, dagger, double dagger, the OCR closing quote U+201D) is removed only at a well-defined boundary of an item or sub-item: the end of
the text, before a closing bracket, comma, semicolon, colon or full stop, before an opening bracket (a percentage or sub-list), before '&' or the connectors 'and' / 'or'. A mark inside a multi-word phrase is left untouched, so
text that abstained before still abstains; the raw input is never changed. Quoted phrases keep their closing quote."""
from __future__ import annotations

import pytest

from foodscan.normalise import normalise_ingredient, strip_footnotes
from foodscan.pipeline import analyse_text

CQ = "\u201d"


def run(text):
    return analyse_text(f"Ingredients: {text}.", source="text")


@pytest.mark.parametrize("t", [f"Rice{CQ} Flour", f"Sunflower{CQ} Oil", f"Skimmed{CQ} Milk Powder", "Rice# Flour", "Rice* Flour", "Rice## Flour", f"Rice \u201cand\u201d Flour", "Wheat\u2020 Flour"])
def test_synthetic_a_mark_inside_a_multi_word_phrase_is_not_removed_and_the_item_abstains(t):
    a = run(t)
    assert not a.answered and a.group is None, t
    assert strip_footnotes(t) == t and normalise_ingredient(t).raw == t


@pytest.mark.parametrize("t,expect", [("Rice#", "rice"), ("Rice**", "rice"), (f"Rice{CQ}", "rice"), ("Rice* (23%)", "rice"), ("Sugar\u2020", "sugar"), ("Salt\u2021", "salt")])
def test_synthetic_a_mark_at_the_end_or_before_a_percentage_is_removed(t, expect):
    assert normalise_ingredient(t).name == expect and normalise_ingredient(t).raw == t


@pytest.mark.parametrize("t", ["Vitamins# and Minerals##", f"Vitamins{CQ} and Minerals**", f"Vitamins{CQ} & Minerals**"])
def test_synthetic_vitamins_and_minerals_with_marks_still_resolve_as_separate_unplaced_entries(t):
    a = run(t)
    assert len(a.ingredients) == 2 and a.unassessed == [] and len(a.unplaced) == 2 and not a.answered, t
    assert [normalise_ingredient(i).name for i in a.ingredients] == ["vitamins", "minerals"], t


def test_synthetic_lists_with_boundary_marks_keep_their_groups():
    assert run("Rice#, Sugar").group == 3 and run("Rice*").group == 1 and run(f"Rice{CQ}").group == 1 and run("Sugar\u2020, Salt\u2021").group in (2, None)


def test_synthetic_quoted_phrases_keep_the_closing_quote():
    assert strip_footnotes(f"\u201cRice{CQ} Flour") == f"\u201cRice{CQ} Flour"
    assert strip_footnotes(f"\u201cRice{CQ}") == f"\u201cRice{CQ}"
