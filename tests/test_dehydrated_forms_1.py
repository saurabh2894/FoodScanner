"""dehydrated-policy-1 (owner decision 2026-11-21): term-level mappings only; NO free-floating 'dehydrated' or generic 'flakes' descriptor (SYNTHETIC cases)."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from foodscan.classify import is_recognised
from foodscan.normalise import normalise_ingredient
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
POL = json.loads((ROOT / "data" / "ingest" / "dehydrated_policy_1.json").read_text(encoding="utf-8"))
SYN = {r["from"]: r for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "synonyms.csv").open(encoding="utf-8-sig", newline=""))}
DESC = {r["word"].lower() for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "descriptors.csv").open(encoding="utf-8-sig", newline=""))}


def rec(t):
    return bool(is_recognised(normalise_ingredient(t).name))


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return (a.group if a.answered else None), a


@pytest.mark.parametrize("r", POL["rows"], ids=lambda r: r["from"])
def test_synthetic_each_term_maps_to_onion_with_its_own_provenance(r):
    s = SYN[r["from"]]
    assert s["to"] == "onion" and s["source"].startswith("PROVISIONAL: alias of existing lexicon row") and "Onions, dehydrated flakes" in s["source"] and "dried" in s["source"] and "PMC10127522" in s["source"] and "licence unverified" in s["source"]
    assert normalise_ingredient(r["from"]).name == "onion" and rec(r["from"])


def test_synthetic_no_free_floating_dehydrated_or_flakes_descriptor_exists():
    assert "dehydrated" not in DESC and "flakes" not in DESC and "flake" not in DESC


def test_synthetic_behaviour_matches_dried_onion_exactly():
    assert g("Dehydrated onion")[0] == g("Dried onion")[0] == 1
    assert g("Rice, onion flakes, salt")[0] == g("Rice, dried onion, salt")[0] == 3


@pytest.mark.parametrize("t", POL["must_stay_unmapped"])
def test_synthetic_negative_other_dehydrated_and_flakes_forms_are_not_captured_by_the_new_mappings(t):
    assert t not in SYN or SYN[t]["to"] != "onion"
    assert normalise_ingredient(t).name != "onion"                                   # none of them is rewritten to onion


@pytest.mark.parametrize("t", POL["must_stay_unrecognised"])
def test_synthetic_negative_processed_onion_forms_stay_unrecognised(t):
    assert not rec(t)


def test_synthetic_dehydrated_vegetable_stays_unassessed_and_the_list_abstains():
    group, a = g("Rice, dehydrated vegetable")
    assert group is None and any("dehydrated vegetable" in u.lower() for u in a.unassessed)
