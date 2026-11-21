"""pmc-reresearch-4 (PROPOSAL record). Nothing in the decisions file is merged: no staged term may be present in lexicon, markers or synonyms. SYNTHETIC checks."""
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
        assert d["disposition"] in {"ACCEPT_ROW", "ACCEPT_SYNONYM", "MARKER_PROPOSAL", "CONFLICT", "PARK"}
        if d["disposition"] in {"PARK", "CONFLICT", "MARKER_PROPOSAL"}:
            assert d.get("reason")


def test_synthetic_no_proposed_term_is_in_the_shipped_tables():
    lex, mk, syn = _col("lexicon.csv"), _col("markers.csv"), _col("synonyms.csv", "from")
    for d in DEC:
        t = d["term"]
        assert t not in mk, t
        if d["disposition"] in {"PARK", "CONFLICT", "MARKER_PROPOSAL"}:
            assert t not in lex and t not in syn, t


def test_synthetic_marker_proposal_files_name_only_the_three_marker_terms():
    got = set()
    for f in ("marker_proposals_4a.json", "marker_proposals_4b.json"):
        got |= {r["term"] for r in json.loads((ROOT / "data" / "ingest" / f).read_text(encoding="utf-8"))["rows"]}
    assert got == {d["term"] for d in DEC if d["disposition"] == "MARKER_PROPOSAL"}


def test_synthetic_the_conflict_is_flagged_not_parked():
    c = [d for d in DEC if d["disposition"] == "CONFLICT"]
    assert [d["term"] for d in c] == ["defatted soya"] and "PMC10127522" in c[0]["reason"]
