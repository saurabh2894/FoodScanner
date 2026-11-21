"""The unplaced kind (recognised BY NAME only; no source places the item). Constraints, each pinned here (SYNTHETIC cases):
 1. an unplaced item never suppresses a list-level abstention and never lets the rest of the list answer;
 2. it is never a classification: not a driver, not counted as classified in any metric, not in "unassessed";
 3. it is shown distinctly (Analysis.unplaced; the page has its own section);
 4. a strong marker still decides Group 4 (unplaced only ever ADDS an abstention)."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from foodscan.pipeline import _ocr_yield, analyse_text

ROOT = Path(__file__).resolve().parent.parent
UNPLACED = [r["term"] for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline="")) if r["kind"] == "unplaced"]


def an(text):
    return analyse_text(text, source="text")


def test_synthetic_the_unplaced_rows_exist_and_each_source_carries_its_abstention_reason():
    assert set(UNPLACED) >= {"vitamins and minerals", "vitamins & minerals", "vitamins", "minerals", "sprouted ragi", "sprouted jowar"}
    for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline="")):
        if r["kind"] == "unplaced":
            assert r["source"].startswith("PROVISIONAL") and "UNPLACED (recognition only, no group effect)" in r["source"] and "abstention reason: no source places" in r["source"]


@pytest.mark.parametrize("text", ["Ingredients: Rice, salt, vitamins and minerals.", "Ingredients: Beans, sprouted ragi.", "Ingredients: Vitamins.", "Ingredients: Sprouted jowar", "Ingredients: Rice, banana powder, minerals."])
def test_synthetic_an_unplaced_item_forces_an_abstention_the_rest_of_the_list_cannot_override(text):
    a = an(text)
    assert not a.answered and a.group is None and "recognised by name only" in a.reason and a.unplaced


def test_synthetic_the_same_lists_without_the_unplaced_item_answer_so_the_item_is_the_only_cause():
    assert an("Ingredients: Rice, salt.").group == 3 and an("Ingredients: Rice, salt, vitamins and minerals.").group is None
    assert an("Ingredients: Beans.").group == 1 and an("Ingredients: Beans, sprouted ragi.").group is None


def test_synthetic_unplaced_items_are_never_drivers_never_unassessed_and_never_classified_coverage():
    a = an("Ingredients: Rice, salt, vitamins and minerals.")
    assert not any("vitamin" in d.ingredient.lower() or "mineral" in d.ingredient.lower() for d in a.drivers)
    assert not any("vitamin" in u.lower() or "mineral" in u.lower() for u in a.unassessed)
    assert [u.lower() for u in a.unplaced] == ["vitamins", "minerals"]
    assert a.completeness["assessed"]["not_assessed"] == 2 and a.completeness["assessed"]["items"] == 4          # counted as NOT assessed
    assert _ocr_yield(a) == 2                                                                                      # rice and salt only: unplaced items add no yield


def test_synthetic_a_strong_marker_still_decides_group_4_and_the_unplaced_item_stays_listed_apart():
    a = an("Ingredients: Water, fructose, vitamins and minerals.")
    assert a.answered and a.group == 4 and [u.lower() for u in a.unplaced] == ["vitamins", "minerals"]
    assert not any("vitamin" in d.ingredient.lower() for d in a.drivers)


def test_synthetic_the_two_grain_pair_now_splits_into_two_unplaced_items_and_the_list_still_abstains():
    a = an("Ingredients: Multigrain Flour Blend (45.7%) [Sprouted Ragi & Jowar (23.4%), Rice & Oat (22.3%)], Vitamins and Minerals.")
    assert [u.lower() for u in a.unplaced] == ["sprouted ragi", "sprouted jowar", "vitamins", "minerals"]
    assert a.unassessed == ["Multigrain Flour Blend (45.7%) (group name; its contents were assessed separately)"]
    assert not a.answered and "recognised by name only" in a.reason                       # recognition is not classification: the split resolves nothing
