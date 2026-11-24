"""pool-a-24 (SYNTHETIC): four culinary rows (coconut cream, milk cream, unsweetened baking chocolate, gelatin powder), all exact-named in
PMC10127522 table footnote 5 under 'Other processed culinary ingredients' (Group 2; licence unverified: short quote only, corroborating) and
class-instances of the FAO 2019 Group 2 general definition. Placement rule 2026-11-21: one strong applicable primary NOVA source suffices.
Conditions: plain foods only. The cocoa-powder-24 mechanism is generalised (plain_culinary_residual over _PLAIN_CONDITION_CULINARY): brackets
beyond a share or the word 'unsweetened' abstain; 'unsweetened' is part of the baking-chocolate row term, so bare 'baking chocolate' abstains."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from foodscan.pipeline import analyse_text

ROWS = ["coconut cream", "milk cream", "unsweetened baking chocolate", "gelatin powder"]


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return (a.group if a.answered else None), a


@pytest.mark.parametrize("t", ROWS)
def test_synthetic_plain_rows_are_group_2_with_the_single_culinary_driver(t):
    group, a = g(t)
    assert group == 2 and a.drivers[0].detail == "single processed culinary ingredient", t


@pytest.mark.parametrize("t", ROWS)
def test_synthetic_percentage_and_unsweetened_brackets_are_group_2(t):
    assert g(f"{t.title()} (4%)")[0] == 2, t
    assert g(f"{t} (unsweetened)")[0] == 2, t


@pytest.mark.parametrize("t", ROWS)
def test_synthetic_bracket_additions_abstain_with_the_plain_food_condition(t):
    group, a = g(f"{t} (Sugar)")
    assert group is None and f"not established as plain {t}" in a.reason, (t, a.reason)


def test_synthetic_conditioned_and_mixed_forms_stay_abstained():
    # sweetened/branded cream forms, dessert mixes and bare/ambiguous names are not the plain rows
    for f in ("cream of coconut", "whipped cream", "aerosol cream", "baking chocolate", "sweetened baking chocolate",
              "jelly crystals", "gelatin dessert", "cream", "gelatin", "agar agar"):
        assert g(f)[0] is None, f


def test_synthetic_existing_neighbours_are_unchanged():
    assert g("cocoa powder")[0] == 2 and g("Cocoa Powder (Sugar)")[0] is None
    assert g("cocoa butter")[0] == 2 and g("vinegar")[0] == 2


def test_synthetic_row_provenance_has_clause_and_condition_notes():
    root = Path(__file__).resolve().parent.parent
    rows = {r["term"]: r["source"] for r in csv.DictReader((root / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}
    for t in ROWS:
        s = rows[t]
        assert s.startswith("PROVISIONAL (pool-a-24)") and "pressing, centrifuging, refining, extracting or mining" in s, t
        assert "PMC10127522" in s and "footnote 5" in s and "class-instance" in s and "NAMED" not in s, t
        assert "plain_culinary_residual" in s and "NOT covered" in s and "not a strong marker" in s, t
    assert "centrifuging" in rows["milk cream"] and "research/09" in rows["milk cream"]
    assert 'WITH the "unsweetened" condition' in rows["unsweetened baking chocolate"]
