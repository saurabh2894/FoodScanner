"""marker-rows-1 as merged (CLASSIFICATION-BEARING; SYNTHETIC unit cases: hand-written, not labels, never counted as coverage)."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
SPEC = json.loads((ROOT / "data" / "ingest" / "marker_rows_1.json").read_text(encoding="utf-8"))
MARKERS = {r["term"]: r for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "markers.csv").open(encoding="utf-8-sig", newline=""))}


def g(text: str):
    a = analyse_text(text, source="text")
    return (a.group if a.answered else None), a


@pytest.mark.parametrize("r", SPEC["rows"], ids=lambda r: r["term"])
def test_synthetic_each_marker_row_is_strong_provisional_and_quotes_both_clauses_verbatim(r):
    m = MARKERS[r["term"]]
    assert m["marker_class"] == "derived_substance" and m["strength"] == "strong" and m["source"].startswith("PROVISIONAL: FAO 2019")
    assert SPEC["clause"]["text"] in m["source"] and SPEC["basis"]["text"] in m["source"] and r["coverage"] in m["source"]
    group, a = g(f"Ingredients: Rice, {r['term']}, salt.")
    assert group == 4 and any(r["term"] in d.detail for d in a.drivers)


def test_synthetic_class_level_rows_say_so_and_the_exact_named_one_says_so():
    assert "exact term IS named" in MARKERS["fructose"]["source"]
    for t in ("wheat gluten", "hydrolysed vegetable protein", "lemon juice concentrate", "apple juice concentrate"):
        assert "class-level coverage" in MARKERS[t]["source"] and "exact term not named by the clause" in MARKERS[t]["source"]


@pytest.mark.parametrize("text", [
    "Ingredients: Oats, gluten free.", "Ingredients: Wheat flour (gluten free), salt.", "Ingredients: Rice, salt. Contains gluten.",
    "Ingredients: Rice, fructooligosaccharide.", "Ingredients: Water, orange juice concentrate."])
def test_synthetic_negative_claims_allergen_lines_lookalikes_and_unapproved_juice_concentrates_are_not_markers(text):
    group, a = g(text)
    assert not any(d.detail.startswith('"') and "derived_substance" in d.detail for d in a.drivers)
    assert group != 4


def test_synthetic_a_group_1_to_3_list_without_these_terms_is_untouched():
    assert g("Ingredients: Rice, salt.")[0] == 3 and g("Ingredients: Beans")[0] == 1


@pytest.mark.xfail(strict=True, reason="KNOWN GAP: the z spelling 'hydrolyzed' does not match the approved marker row 'hydrolysed vegetable protein' (seen in dev/F07 and out-of-sample S13, both already Group 4 by other markers). A spelling synonym needs the owner's approval.")
def test_synthetic_known_gap_hydrolyzed_spelling_variant():
    assert g("Ingredients: Rice, Hydrolyzed Vegetable Protein.")[0] == 4
