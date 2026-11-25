"""demand-bulk-1 as merged (SYNTHETIC unit cases; not labels, never counted as coverage): the 7 rows and 1 synonym behave as their kinds say, existing markers keep priority,
and every parked, label-bound or marker-proposal term stays UNRECOGNISED (a decision file entry must never leak into the vocabulary)."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from foodscan.classify import is_recognised
from foodscan.normalise import normalise_ingredient
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
DEC = json.loads((ROOT / "data" / "ingest" / "demand_decisions_1.json").read_text(encoding="utf-8"))["decisions"]
LEX = {r["term"]: r for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}

# pmc-decisions-4 (owner-approved 2026-11-21, merged): these terms were PARK / single-source / proposed in earlier records and are now placed by the updated rule.
APPROVED_4 = {d["term"] for d in json.loads((ROOT / "data" / "ingest" / "pmc_decisions_4.json").read_text(encoding="utf-8"))["decisions"] if d["disposition"] in ("ACCEPT_ROW", "ACCEPT_SYNONYM")}


def rec(t: str) -> bool:
    return bool(is_recognised(normalise_ingredient(t).name))


def grp(text: str):
    a = analyse_text(text, source="text")
    return (a.group if a.answered else None), a


@pytest.mark.parametrize("d", [d for d in DEC if d["disposition"] == "ACCEPT_ROW"], ids=lambda d: d["term"])
def test_synthetic_accepted_rows_are_merged_provisional_with_the_verbatim_clause(d):
    t = d.get("row_term", d["term"])
    r = LEX[t]
    # class-bulk-1 retyped 'beans' to the legume kind and class-bulk-2 retyped 'cabbage' to the vegetable kind (both from whole_food) (same whole-food behaviour plus the item-level salt/sugar/brine guard); the record keeps the original kind
    assert (r["kind"] == d["kind"] or (t == "beans" and d["kind"] == "whole_food" and r["kind"] == "legume") or (t == "cabbage" and d["kind"] == "whole_food" and r["kind"] == "vegetable")) and r["source"].startswith("PROVISIONAL: FAO 2019") and d["clause"] in r["source"] and "demand-decisions-1" in r["source"]
    assert rec(d["term"]) and rec(t)


def test_synthetic_kinds_drive_the_group_exactly_as_the_source_clause_says():
    assert grp("Ingredients: Beans")[0] == 1                               # legumes such as beans
    assert grp("Ingredients: Beans, water, salt.")[0] == 3                 # Group 2 salt added to a Group 1 food, water ignored
    assert grp("Ingredients: Cabbage")[0] == 1
    assert grp("Ingredients: Wheat flour.")[0] == 1                        # single flour
    g, a = grp("Ingredients: Wheat flour, salt.")
    assert g is None and "flour-based list" in a.reason                    # kind flour: multi-item lists abstain, never forced
    assert grp("Ingredients: Edible peanut oil.")[0] == 2                  # the descriptor word 'edible' is ignored, oil is Group 2


def test_synthetic_standing_exclusions_stay_out_cranberry_and_the_modified_starch_marker_is_untouched():
    assert not rec("cranberry") and "cranberry" not in LEX                                          # lexicon-1 senior-review exclusion that still stands
    assert "starch" in LEX and LEX["starch"]["kind"] == "culinary"                                   # hold lifted for plain starch only (owner, 2026-11-21)


def test_synthetic_existing_marker_keeps_priority_over_a_starch_in_the_list():
    g, a = grp("Ingredients: Modified starch, rice.")
    assert g == 4 and any("modified starch" in d.detail.lower() or "modified starch" in d.ingredient.lower() for d in a.drivers)


def test_synthetic_the_synonym_maps_potable_water_to_water_and_nothing_else():
    assert normalise_ingredient("potable water").name == "water" and rec("potable water")
    assert not rec("potable") and not rec("mineral water x")


@pytest.mark.parametrize("d", [d for d in DEC if d["disposition"] in ("PARK", "LABEL_BOUND", "MARKER_PROPOSAL")], ids=lambda d: d["term"])
def test_synthetic_negative_no_parked_label_bound_or_marker_proposal_term_is_recognised(d):
    if d["term"] == "carbonated water":
        from foodscan.classify import lookup
        assert lookup(d["term"])["kind"] == "named_water"
        assert grp("Ingredients: Carbonated Water.")[0] == 1
        assert not analyse_text("Ingredients: Carbonated Water, Sugar.", source="text").answered
        return
    if d["term"] == "cocoa powder":
        # cocoa-powder-24 (2026-11-24): PMC10127522 footnote 5 verified live on the rendered PMC page and the
        # pmc-reresearch-4 park condition implemented (cocoa_powder_residual); asserted in tests/test_cocoa_powder_24.py
        return
    if d["term"] in ("apple juice", "grape juice", "orange juice", "pineapple juice"):
        # fruit-forms-23: recognition does not lift the bare-form placement hold.
        from foodscan.classify import lookup
        assert lookup(normalise_ingredient(d["term"]).name)["kind"] == "fruit_juice"
        a = analyse_text("Ingredients: " + d["term"] + ".", source="text")
        assert not a.answered and d["term"] in a.unplaced
        return
    if d["term"] == "tumeric":
        # Current NALT Product30814 explicitly lists this spelling of turmeric, a spice.
        assert normalise_ingredient(d["term"]).name == "turmeric"
        assert grp("Ingredients: Tumeric.")[0] == grp("Ingredients: Turmeric.")[0]  # recognition-only alias, no new standalone-spice rule
        return
    if d["term"] == "maida":
        # scoped-powder-5: FSSAI2.4.2 names this exact food identity.
        # Qualified/protein-rich/durum forms remain negative controls in test_scoped_names_5.
        assert normalise_ingredient(d["term"]).name == "refined wheat flour"
        assert grp("Ingredients: Maida.")[0] == 1
        return
    if d["term"] in ("pasteurized cow milk", "pasteurised cow milk"):
        # per-form-2b (owner decision 2026-11-21: species-head milk recognition): recognised ONLY as the milk row 'cow milk' (descriptor 'pasteurized/pasteurised' dropped)
        from foodscan.classify import lookup
        assert lookup(normalise_ingredient(d["term"]).name)["term"] == "cow milk", d["term"]
        return
    if d["term"] in APPROVED_4:
        return                                                              # approved and merged later (pmc-decisions-4); asserted in tests/test_pmc_reresearch_4.py
    if d["term"] in ("dehydrated onion", "onions flakes") and rec(d["term"]):
        assert normalise_ingredient(d["term"]).name == "onion", d["term"]         # dehydrated-policy-1: term-level mapping to the source-supported dried onion, one per term
        return
    if d["term"] == "coconut fat" and rec(d["term"]):
        # pmc-decisions-2: recognised ONLY as the plain culinary row (FAO Group 2 oils clause + PMC10127522 corroboration)
        from foodscan.classify import lookup
        assert lookup(normalise_ingredient(d["term"]).name)["kind"] == "culinary", d["term"]
        return
    if d["term"] in ("starch", "tapioca starch") and rec(d["term"]):
        # owner lift 2026-11-21 (pmc-decisions-1): recognised ONLY as the plain culinary row
        from foodscan.classify import lookup
        assert lookup(normalise_ingredient(d["term"]).name)["kind"] == "culinary", d["term"]
        return
    if d.get("code") == "held_category_C" and rec(d["term"]):
        # superseded by the owner-approved unplaced kind (recognition only, never placed): recognised ONLY as that kind
        from foodscan.classify import lookup
        assert lookup(normalise_ingredient(d["term"]).name)["kind"] == "unplaced", d["term"]
        return
    assert not rec(d["term"]), f"{d['term']!r} ({d['disposition']}) must stay unrecognised until the owner decides"


def test_synthetic_parked_and_label_bound_terms_decide_nothing_but_an_approved_marker_still_does():
    g, a = grp("Ingredients: Cocoa butter, apple juice, yeast extract, glucose syrup.")
    assert g == 4 and any("glucose syrup" in d.detail for d in a.drivers)   # fardet-markers-24: glucose syrup is now a marker (second admissible source); the rest is unplaced
    g, a = grp("Ingredients: Cocoa butter, wheat gluten, apple juice, yeast extract, glucose syrup.")
    assert g == 4 and any("wheat gluten" in d.detail for d in a.drivers)    # wheat gluten became an owner-approved strong marker (marker-rows-1); the rest stays unplaced
