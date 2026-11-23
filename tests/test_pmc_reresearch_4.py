"""pmc-reresearch-4 (owner-approved 2026-11-21, merged): approved rows/synonyms/markers are shipped; PARK (incl. cocoa powder and dry fruits, parked by the owner) and CONFLICT terms are not. SYNTHETIC checks."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEC = json.loads((ROOT / "data" / "ingest" / "pmc_decisions_4.json").read_text(encoding="utf-8"))["decisions"]
RES = ROOT / "src" / "foodscan" / "resources"


def _col(name, col="term"):
    return {r[col] for r in csv.DictReader((RES / name).open(encoding="utf-8-sig", newline=""))}


def test_synthetic_every_decision_has_a_known_disposition_and_a_reason_when_not_staged():
    for d in DEC:
        assert d["disposition"] in {"ACCEPT_ROW", "ACCEPT_SYNONYM", "HELD", "CONFLICT", "PARK"}
        if d["disposition"] in {"PARK", "CONFLICT", "HELD"}:
            assert d.get("reason")


def test_synthetic_approved_terms_are_shipped_and_parked_or_conflicted_terms_are_not():
    lex, mk, syn = _col("lexicon.csv"), _col("markers.csv"), _col("synonyms.csv", "from")
    for d in DEC:
        t, k = d["term"], d["disposition"]
        if t == "carbonated water":
            # named-water-23 exact primary support supersedes no-source finding only.
            from foodscan.pipeline import analyse_text
            assert t in lex and t not in syn and t not in mk
            assert analyse_text("Ingredients: Carbonated Water.", source="text").group == 1
            assert not analyse_text("Ingredients: Carbonated Water (Sugar).", source="text").answered
            continue
        if k == "ACCEPT_ROW":
            assert t in lex, t
        elif k == "ACCEPT_SYNONYM":
            assert t in syn, t
        else:
            assert t not in lex and t not in syn and t not in mk, t


def test_synthetic_the_three_withdrawn_marker_proposals_are_held_with_the_exact_gap_and_are_not_markers():
    held = {d["term"]: d for d in DEC if d["disposition"] == "HELD"}
    assert set(held) == {"glucose syrup", "liquid glucose", "texturized soy protein"}
    assert "product-level coding alone insufficient" in held["glucose syrup"]["reason"] and "product-level coding alone insufficient" in held["liquid glucose"]["reason"]
    assert "class membership not established for the texturized form" in held["texturized soy protein"]["reason"]
    mk = _col("markers.csv")
    assert not (set(held) & mk)


def test_synthetic_the_conflict_is_flagged_not_parked():
    c = [d for d in DEC if d["disposition"] == "CONFLICT"]
    assert [d["term"] for d in c] == ["defatted soya"] and "PMC10127522" in c[0]["reason"]
