"""dairy-rows-1 (SYNTHETIC): five whole_food rows (sheep milk, duck eggs, goose eggs, quail eggs, turkey eggs), class-instance of the FAO animal milk / eggs clauses (no species named by a source read).
Held and not added: human milk, instant dry milk, egg powder exception, species constants, synonyms. Measured gaps shared with the existing milk and egg rows are pinned in the evaluation README, not here."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from foodscan.pipeline import analyse_text

ROWS = ["sheep milk", "duck eggs", "goose eggs", "quail eggs", "turkey eggs"]


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return (a.group if a.answered else None), a


@pytest.mark.parametrize("t", ROWS)
def test_synthetic_new_rows_are_group_1_with_the_single_food_driver(t):
    group, a = g(t)
    assert group == 1 and a.drivers[0].detail == "single recognised unprocessed food", t


@pytest.mark.parametrize("t", ["Human Milk", "Instant Skimmed Milk Powder", "Sheep", "Egg Powder", "Sheep Milk Powder", "Sheep Milk Solids", "Duck Egg Yolk", "Sheep Cheese", "Rice, Duck Eggs", "Duck Eggs (Cow Milk)", "Sheep Milk (XQ9)"])
# UPDATED (animal-guard-1): "Duck" left this list because `duck` is now a lexicon row (a meat/poultry label); the egg and milk forms below are unchanged.
def test_synthetic_held_and_unrecognised_forms_abstain(t):
    assert g(t)[0] is None, t


@pytest.mark.parametrize("t", ROWS)
def test_synthetic_comma_salt_or_sugar_is_group_3_and_unknown_bracket_abstains(t):
    assert g(t + ", salt")[0] == 3 and g(t + ", sugar")[0] == 3 and g(t + " (XQ9)")[0] is None, t


def test_synthetic_row_provenance_is_class_instance_with_the_verified_clauses():
    root = Path(__file__).resolve().parent.parent
    rows = {r["term"]: r["source"] for r in csv.DictReader((root / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}
    for t in ROWS:
        s = rows[t]
        assert s.startswith("PROVISIONAL (dairy-rows-1)") and "or of or from animals (muscle, fat, offal, eggs, milk)" in s and "class-instance" in s and "NAMED" not in s and "FDC id" in s, t
    assert "fresh, powdered or pasteurized milk" in rows["sheep milk"] and all("fresh, powdered, chilled or frozen eggs" in rows[t] for t in ROWS[1:])
