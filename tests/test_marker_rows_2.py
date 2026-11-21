"""marker-rows-2 as merged (CLASSIFICATION-BEARING; SYNTHETIC unit cases): whey powder and whey solids, owner-approved strong markers."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
SPEC = json.loads((ROOT / "data" / "ingest" / "marker_rows_2.json").read_text(encoding="utf-8"))
MARKERS = {r["term"]: r for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "markers.csv").open(encoding="utf-8-sig", newline=""))}


def g(text):
    a = analyse_text(text, source="text")
    return (a.group if a.answered else None), a


@pytest.mark.parametrize("r", SPEC["rows"], ids=lambda r: r["term"])
def test_synthetic_each_whey_row_is_strong_provisional_and_quotes_both_clauses_class_level_and_the_dried_form_inference(r):
    m = MARKERS[r["term"]]
    assert m["marker_class"] == "derived_substance" and m["strength"] == "strong" and m["source"].startswith("PROVISIONAL: FAO 2019")
    assert SPEC["clause"]["text"] in m["source"] and SPEC["basis"]["text"] in m["source"]
    assert "class-level coverage" in m["source"] and "exact term not named by the clause" in m["source"] and "INFERENCE" in m["source"] and "licence unverified" in m["source"]
    group, a = g(f"Ingredients: Rice, {r['term']}, salt.")
    assert group == 4 and any(r["term"] in d.detail for d in a.drivers)


@pytest.mark.parametrize("text", ["Ingredients: Milk, water.", "Ingredients: Rice, salt.", "Ingredients: Beans."])
def test_synthetic_lists_without_whey_are_untouched(text):
    group, a = g(text)
    assert group != 4 and not any("whey" in d.detail for d in a.drivers)


def test_synthetic_negative_the_marker_does_not_fire_on_a_bare_whey_or_on_whey_free_wording():
    assert "whey powder" in MARKERS and "whey" not in MARKERS                      # the approved rows are the two dried forms only
    group, a = g("Ingredients: Rice, salt. Contains milk.")
    assert group == 3 and not any("whey" in d.detail for d in a.drivers)
