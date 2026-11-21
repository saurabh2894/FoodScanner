"""pmc-decisions-3 (documentation-only record). The whey rows were proposed in this round and are now APPROVED AND MERGED (claude/markers-2); this test asserts the merged state. SYNTHETIC checks."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
DEC = json.loads((ROOT / "data" / "ingest" / "pmc_decisions_3.json").read_text(encoding="utf-8"))["decisions"]
MARKERS = {r["term"]: r for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "markers.csv").open(encoding="utf-8-sig", newline=""))}
LEX = {r["term"] for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}


def test_synthetic_whey_powder_and_whey_solids_are_present_as_strong_derived_substance_markers():
    for t in ("whey powder", "whey solids"):
        assert MARKERS[t]["marker_class"] == "derived_substance" and MARKERS[t]["strength"] == "strong" and "licence unverified" in MARKERS[t]["source"]
    a = analyse_text("Ingredients: Rice, whey powder.", source="text")
    assert a.answered and a.group == 4


def test_synthetic_the_decision_record_marks_whey_as_approved_and_merged_and_every_other_term_parked_with_a_reason():
    for d in DEC:
        assert d["sources_say"] and d["result"]
        if d["term"] in ("whey powder", "whey solids"):
            assert d["disposition"].startswith("APPROVED AND MERGED")
        else:
            assert d["disposition"] == "PARK" and d["term"] not in LEX and d["term"] not in MARKERS
