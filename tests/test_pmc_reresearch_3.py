"""pmc-decisions-3: nothing from this round entered the vocabulary; the whey marker rows are a PROPOSAL only (SYNTHETIC checks)."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
DEC = json.loads((ROOT / "data" / "ingest" / "pmc_decisions_3.json").read_text(encoding="utf-8"))["decisions"]
PROP = json.loads((ROOT / "data" / "ingest" / "marker_rows_2_proposal.json").read_text(encoding="utf-8"))
MARKERS = {r["term"] for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "markers.csv").open(encoding="utf-8-sig", newline=""))}


def test_synthetic_the_whey_marker_rows_are_a_proposal_and_not_in_markers_csv():
    assert PROP["batch_id"].endswith("PROPOSAL") and "NOT approved" in PROP["note"]
    for r in PROP["rows"]:
        assert r["term"] not in MARKERS and "licence unverified" in r["coverage"]
    assert analyse_text("Ingredients: Rice, whey powder.", source="text").group is None


def test_synthetic_every_decision_has_a_disposition_and_a_reason():
    assert {d["disposition"].split(" ")[0] for d in DEC} <= {"PARK", "PROPOSAL"}
    assert all(d["sources_say"] and d["result"] for d in DEC)
