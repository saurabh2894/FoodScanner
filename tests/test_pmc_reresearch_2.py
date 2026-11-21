"""pmc-decisions-2 (SYNTHETIC cases): one plain culinary row (coconut fat) entered the vocabulary; every other re-researched term stays out with its reason."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from foodscan.classify import is_recognised
from foodscan.normalise import normalise_ingredient
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
DEC = json.loads((ROOT / "data" / "ingest" / "pmc_decisions_2.json").read_text(encoding="utf-8"))["decisions"]
LEX = {r["term"]: r for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return (a.group if a.answered else None), a


def test_synthetic_coconut_fat_is_a_plain_culinary_row_with_the_fao_clause_and_licence_unverified_pmc_corroboration():
    r = LEX["coconut fat"]
    assert r["kind"] == "culinary" and "Vegetable oils crushed from seeds, nuts or fruit" in r["source"] and "PMC10127522" in r["source"] and "licence unverified" in r["source"] and "not solely supported" in r["source"]
    assert g("Coconut fat")[0] == 2 and g("Rice, coconut fat")[0] == 3


def test_synthetic_negative_hydrogenated_or_fractionated_forms_are_never_read_as_plain_coconut_fat():
    group, a = g("Rice, hydrogenated coconut fat")
    assert group == 4 and any("hydrogenated" in d.detail for d in a.drivers)                    # the existing strong marker decides
    assert not is_recognised(normalise_ingredient("fractionated coconut fat").name)


def test_synthetic_every_other_re_researched_term_stays_out_with_a_recorded_reason():
    for d in DEC:
        if d["disposition"] == "ACCEPT_ROW":
            assert d["term"] in LEX
        elif d["term"] in ("dehydrated onion", "onions flakes"):
            assert normalise_ingredient(d["term"]).name == "onion"                      # dehydrated-policy-1: term-level synonym, owner-approved; no descriptor
        else:
            assert d["term"] not in LEX and not is_recognised(normalise_ingredient(d["term"]).name), d["term"]
            assert d["code"] in ("single_source_flag", "owner_decision_descriptor", "no_source_for_qualifier", "no_source_for_form") and d["reason"]
    assert g("Rice, glucose syrup")[0] is None                                               # glucose syrup is NOT classified: PMC alone, flagged
