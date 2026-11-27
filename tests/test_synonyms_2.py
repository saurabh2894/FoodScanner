"""synonyms-2 (reviewed alias-1 set; PROPOSAL branch). SYNTHETIC checks: the 23 applied aliases route to their canonical rows and nothing else; the parked aliases get no entry and stay unassessed."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from foodscan.classify import is_recognised
from foodscan.normalise import normalise_ingredient
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
EV = ROOT / "evaluation" / "synonyms_2"
SYN = {r["from"]: r for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "synonyms.csv").open(encoding="utf-8-sig", newline=""))}
ROWS = list(csv.DictReader((EV / "synonym_rows.csv").open(encoding="utf-8", newline="")))
# UPDATED (engine-fixes-1): 'bok choy' was gate-excluded in synonyms-2 (prefix-of-target rewrite defect); the engine is now target-safe and the row is re-added, so it leaves the parked list (13 remain parked).
# scoped-powder-5: Maida now has exact FSSAI2.4.2 naming evidence. The old parked.csv is retained as history; all other parked aliases remain negative controls.
# nalt-names-6: current NALT Product 16207 explicitly gives chick peas as the same chickpea food. The parked.csv is retained as history; every other hold remains.
PARKED = [r["alias"] for r in csv.DictReader((EV / "parked.csv").open(encoding="utf-8", newline="")) if r["alias"] not in {"bok choy", "maida", "chick peas", "tumeric", "gingelly oil", "refined palmolien oil"}]
# palmolien-24: "refined palmolien oil" leaves the old parked list (Indian trade spelling of palmolein, evidence in the synonyms.csv note); 8 remain parked.


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return (a.group if a.answered else None), a


# indian-alias-24c: FSSAI Chapter 2.2 'TIL OIL (Gingelly or sesame oil)' now names gingelly oil, so it leaves the parked list.
# nalt-names-7: current Product30814 names tumeric as turmeric. Only that spelling leaves the old parked list.
def test_synthetic_23_historical_rows_remain_and_10_other_aliases_are_parked():
    assert len(ROWS) == 23 and len(PARKED) == 8
    for r in ROWS:
        assert SYN[r["from"]]["to"] == r["to"] and r["source"].startswith("PROVISIONAL: alias of existing lexicon row") and "recognition routing only" in r["source"]
        assert "FDC id" in r["source"] and ("food_attribute.csv row" in r["source"] or "bracketed alternate name in the FDC description" in r["source"])
    assert not (set(PARKED) & set(SYN))                                       # parked aliases have NO synonyms entry


@pytest.mark.parametrize("a", [r["from"] for r in ROWS])
def test_synthetic_every_applied_alias_is_recognised_as_its_canonical_row(a):
    row = next(r for r in ROWS if r["from"] == a)
    assert normalise_ingredient(a).name == normalise_ingredient(row["to"]).name and is_recognised(normalise_ingredient(row["to"]).name)      # hyphenated targets are normalised to spaces by the pipeline


@pytest.mark.parametrize("a", PARKED)
def test_synthetic_negative_parked_aliases_stay_unrecognised_and_unassessed(a):
    group, an = g(a)
    assert group is None and not is_recognised(normalise_ingredient(a).name) and a.lower() in " ".join(u.lower() for u in an.unassessed)


@pytest.mark.parametrize("alias,target", [("lychee", "litchis"), ("kangkong", "water convolvulus"), ("moth bean", "mothbeans"), ("sucrose", "sugar"), ("mandarin oranges", "tangerines"), ("pak choi", "bok choy cabbage")])
def test_synthetic_an_alias_behaves_exactly_like_its_target_in_every_form(alias, target):
    for f in ("{x}", "salted {x}", "{x} (sugar)", "{x} (pickled)", "{x} (XQ9)", "{x} powder", "100% {x} powder", "Rice, {x}", "{x}, salt"):
        assert g(f.format(x=alias))[0] == g(f.format(x=target))[0], f


def test_synthetic_conditions_of_the_canonical_row_apply_unchanged_through_the_alias():
    assert g("Lychee")[0] == 1 and g("Salted Lychee")[0] == 3 and g("Lychee (pickled)")[0] is None and g("Lychee Powder")[0] is None and g("100% Lychee Powder")[0] == 1
    assert g("Sucrose")[0] == 2 and g("Moth Bean (salted)")[0] == 3


def test_synthetic_the_bok_choy_alias_is_re_added_and_the_canonical_row_is_unchanged():
    assert SYN["bok choy"]["to"] == "bok choy cabbage" and "FDC id 170390" in SYN["bok choy"]["source"]
    assert normalise_ingredient("bok choy cabbage").name == "bok choy cabbage" and normalise_ingredient("bok choy").name == "bok choy cabbage"
    assert g("Bok Choy Cabbage")[0] == 1 and g("Bok Choy")[0] == 1


def test_synthetic_the_committed_applied_gate_is_clean():
    C = json.loads((EV / "applied_gate" / "applied_gate.json").read_text(encoding="utf-8"))
    assert C["verdict"] == "READY_FOR_REVIEW" and not C["blockers"] and C["drift"]["differences"] == {} and C["lexicon_unchanged"]
    assert len(C["after_build_proof"]) == 23 and all(v["recognised_after"] and not v["recognised_before"] for v in C["after_build_proof"].values())
    sx = C["synonyms_additions"]
    assert sx["base_lines_all_kept_in_order"] and sx["added_rows"] == 23 and sx["added_froms_match"] and C["synonyms_markers_untouched"]["markers.csv"]
    for k in ("frozen_66", "out_of_sample"):
        assert C[k]["unexplained"] == [] and C[k]["abstain_to_4"] == [] and C[k]["abstain_to_1"] == [] and C[k]["other_group_change"] == []
        assert all(c["group"][0] == c["group"][1] and c["status"][0] == c["status"][1] for c in C[k]["changed"])
    assert C["alias_equals_target"]["mismatches"] == [] and C["alias_equals_target"]["compared"] == 23 * 12
