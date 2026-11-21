"""scripts/synonym_batch.py gate mechanics (SYNTHETIC policies; the real policy is exercised by tests/test_plural_synonyms_1.py)."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
for p in (REPO, REPO / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import synonym_batch as sb


def gate(rows, neg=(), unrec=()):
    pol = {"policy_id": "p", "rows": [{"rule": "r", "basis": "same ingredient, same plant part, same form", **r} for r in rows], "must_stay_unmapped": list(neg), "must_stay_unrecognised": list(unrec)}
    with tempfile.TemporaryDirectory() as td:
        return sb.run_gate(pol, REPO / "src", REPO / "evaluation", Path(td))


def test_synthetic_good_row_passes_and_is_attributed_with_no_flip():
    g = gate([{"from": "zorbium seeds", "to": "cumin"}], neg=["zorbium leaves"])
    assert g["verdict"] == "READY_FOR_REVIEW" and g["flip"]["changed_counts"]["group"] == 0 and g["rows"][0]["source"].startswith("PROVISIONAL: alias of existing lexicon row")


def test_synthetic_bad_rows_block_the_gate():
    assert any("not an existing lexicon row" in e for e in gate([{"from": "zorbium seeds", "to": "no such row"}])["errors"])
    assert gate([{"from": "cumin", "to": "cumin"}])["dropped"] == [{"from": "cumin", "why": "already a lexicon term"}]
    assert any("listed twice" in e for e in gate([{"from": "zorbium seeds", "to": "cumin"}, {"from": "zorbium seeds", "to": "cumin"}])["errors"])
    d = gate([{"from": "curry leaves", "to": "dried curry leaves"}])                     # the real drift case: an alias that rewrites an existing row's own name
    assert d["verdict"] == "BLOCKED" and any("existing terms whose normalised name" in e for e in d["errors"])


def test_synthetic_a_processed_form_control_that_becomes_recognised_blocks():
    g = gate([{"from": "zorbium seed", "to": "cumin"}], unrec=["zorbium seed"])
    assert g["verdict"] == "BLOCKED" and any("processed-form controls became recognised" in e for e in g["errors"])
