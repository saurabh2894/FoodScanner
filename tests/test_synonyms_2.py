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
PARKED = [r["alias"] for r in csv.DictReader((EV / "parked.csv").open(encoding="utf-8", newline=""))]


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return (a.group if a.answered else None), a


def test_synthetic_exactly_23_rows_are_applied_with_pinpoint_provenance_and_14_aliases_are_parked():
    assert len(ROWS) == 23 and len(PARKED) == 14
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


def test_synthetic_the_bok_choy_alias_is_excluded_because_it_would_break_the_canonical_row():
    assert "bok choy" not in SYN and "bok choy" in PARKED
    assert g("Bok Choy Cabbage")[0] == 1                                       # the canonical row is still recognised


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
