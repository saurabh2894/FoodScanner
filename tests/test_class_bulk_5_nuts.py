"""class-bulk-5 (SYNTHETIC): twenty nut_seed rows staged from the senior-reviewed FDC 'Nut and Seed Products' accepts (evaluation/junior_reviews_2/05_nuts_review.md).
Placement rests on the FAO Group 1 clause 'tree and ground nuts and other oily seeds (with no added salt or sugar)'; the item-level salt/sugar guard of the nut_seed kind applies.
Held (not rows): lotus, breadfruit, breadnut and sisymbrium seeds (oily-seed membership unsupported). Forms the vocabulary lacks (butters, flours, oil roasted, singular/plural label variants) stay unrecognised."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from foodscan.classify import lookup
from foodscan.pipeline import analyse_text

ROWS = ["acorns", "beechnuts", "brazil nuts", "butternuts", "cashew nuts", "chestnuts", "chia seeds", "ginkgo nuts", "hazelnuts", "hickory nuts", "macadamia nuts", "pecans", "pili nuts", "pine nuts",
        "pistachio nuts", "safflower seeds", "sesame seeds", "sunflower seeds", "walnuts", "watermelon seeds"]


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return (a.group if a.answered else None), a


@pytest.mark.parametrize("t", ROWS)
def test_synthetic_staged_nut_rows_are_group_1_when_plain(t):
    group, a = g(t)
    assert group == 1 and lookup(t)["kind"] == "nut_seed", t
    assert g("roasted " + t)[0] == 1 and g("unsalted " + t)[0] == 1


@pytest.mark.parametrize("t", ROWS)
def test_synthetic_added_salt_or_sugar_is_group_3_at_item_level(t):
    assert g("salted " + t)[0] == 3 and g(t + ", salt")[0] == 3 and g(t + ", sugar")[0] == 3, t


@pytest.mark.parametrize("t", ["Lotus Seeds", "Breadfruit Seeds", "Breadnut Seeds", "Sisymbrium Seeds", "Almond Butter", "Cashew Nut Butter", "Tahini", "Chestnut Flour", "Sesame Flour", "Oil Roasted Cashew Nuts", "Honey Roasted Pecans", "Peanuts", "Coconut"])
def test_synthetic_held_and_other_forms_stay_unrecognised(t):
    assert g(t)[0] is None, t


def test_synthetic_row_provenance_states_clause_inference_condition_and_fdc_ids():
    root = Path(__file__).resolve().parent.parent
    rows = {r["term"]: r["source"] for r in csv.DictReader((root / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}
    for t in ROWS:
        s = rows[t]
        assert s.startswith("PROVISIONAL (class-bulk-5)") and "tree and ground nuts and other oily seeds (with no added salt or sugar)" in s, t
        assert "class-instance" in s and "CONDITION KEPT" in s and "FDC id" in s and "NAMED" not in s, t
    assert s.count("FDC id") >= 1 and rows["chestnuts"].count("FDC id") == 8 and "starchy low-fat nut" in rows["chestnuts"] and "starchy low-fat nut" in rows["ginkgo nuts"]
    assert "169408" in rows["chestnuts"] and "169413" in rows["chestnuts"]
