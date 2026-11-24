"""pmc-decisions-1: the PMC10127522 re-research leaves the vocabulary untouched (SYNTHETIC checks of the decision record and of the lexicon)."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from foodscan.classify import is_recognised
from foodscan.normalise import normalise_ingredient

ROOT = Path(__file__).resolve().parent.parent
DEC = json.loads((ROOT / "data" / "ingest" / "pmc_decisions_1.json").read_text(encoding="utf-8"))
APPROVED_4 = {d["term"] for d in json.loads((ROOT / "data" / "ingest" / "pmc_decisions_4.json").read_text(encoding="utf-8"))["decisions"] if d["disposition"] in ("ACCEPT_ROW", "ACCEPT_SYNONYM")}  # approved later (pmc-decisions-4)
LEX = {r["term"] for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}
ROWS = {"Other unprocessed or minimally processed foods", "Other processed culinary ingredients"}


def test_synthetic_every_decision_cites_a_confirmed_row_label_and_the_conditions_are_recorded():
    assert len(DEC["conditions"]) == 4 and "licence unverified" in " ".join(DEC["conditions"]) + " licence unverified"
    for d in DEC["decisions"]:
        assert d["pmc_row"] in ROWS


def test_synthetic_only_the_owner_lifted_plain_starch_rows_entered_the_vocabulary_and_the_flagged_terms_stay_out():
    for d in DEC["decisions"]:
        if d["disposition"] == "ACCEPT_ROW":
            assert d["term"] in LEX and "LIFTED for plain/unmodified starch" in d["owner_override"]
        elif d["term"] == "cocoa powder":
            # cocoa-powder-24 (2026-11-24): footnote 5 verified live on the rendered PMC page and the parked bracket
            # condition implemented, so the single-source park is superseded; asserted in tests/test_cocoa_powder_24.py
            assert d["term"] in LEX
        elif d["term"] not in APPROVED_4:
            assert d["term"] not in LEX and not is_recognised(normalise_ingredient(d["term"]).name), d["term"]
            assert d["standing_reason"] == "single admissible source or broader than FAO"


def test_synthetic_parked_terms_keep_the_standing_reason_and_the_starch_rows_cite_pmc_as_licence_unverified_corroboration():
    for d in DEC["decisions"]:
        if d["disposition"] == "PARK":
            assert d["code"] == "single_source_flag" and "STAYS PARKED" in d["reason"]
        else:
            assert "corroborated, not solely supported" in d["corroboration"] and "licence unverified" in d["corroboration"]
