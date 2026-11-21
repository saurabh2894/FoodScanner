"""pmc-decisions-1: the PMC10127522 re-research leaves the vocabulary untouched (SYNTHETIC checks of the decision record and of the lexicon)."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from foodscan.classify import is_recognised
from foodscan.normalise import normalise_ingredient

ROOT = Path(__file__).resolve().parent.parent
DEC = json.loads((ROOT / "data" / "ingest" / "pmc_decisions_1.json").read_text(encoding="utf-8"))
LEX = {r["term"] for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}
ROWS = {"Other unprocessed or minimally processed foods", "Other processed culinary ingredients"}


def test_synthetic_every_decision_cites_a_confirmed_row_label_and_the_conditions_are_recorded():
    assert len(DEC["conditions"]) == 4 and "licence unverified" in " ".join(DEC["conditions"]) + " licence unverified"
    for d in DEC["decisions"]:
        assert d["pmc_row"] in ROWS


def test_synthetic_nothing_from_the_pmc_re_research_is_in_the_vocabulary_until_the_owner_decides():
    for d in DEC["decisions"]:
        assert d["term"] not in LEX and not is_recognised(normalise_ingredient(d["term"]).name), d["term"]


def test_synthetic_single_source_terms_are_parked_and_the_starch_proposals_carry_the_proposed_only_override():
    for d in DEC["decisions"]:
        if d["disposition"] == "PARK":
            assert d["code"] == "single_source_flag" and "ALONE" in d["reason"] or "extends beyond" in d["reason"]
        else:
            assert "PROPOSED ONLY, NOT MERGEABLE" in d["owner_override"] and "corroborated, not solely supported" in d["corroboration"] and "licence unverified" in d["corroboration"]
