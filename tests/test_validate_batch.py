"""WS4 validation gate (scripts/validate_batch.py): schema, provenance, duplicates, ambiguity queue, and the before/after flip harness in two fresh processes."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
for p in (REPO_ROOT, REPO_ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import pytest

from scripts import clause_tier as ct
from scripts import validate_batch as vb

RULE = ct.load_rule()
CLAUSE = RULE["clause"]["text"]
SRC = REPO_ROOT / "src"
EVAL = REPO_ROOT / "evaluation"


def staged_row(term="basil", kind="herb_spice", fdc="fdc_sr_legacy:7", desc="Basil, fresh", fid="7"):
    return {"term": term, "kind": kind, "fdc_ids": fdc, "rule_id": RULE["rule_id"],
            "source": f"PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 \"{CLAUSE}\"; exact term not named by the clause; name from USDA FoodData Central (CC0 1.0): sr_legacy FDC id {fid} \"{desc}\""}


CAND = {"fdc_sr_legacy:7": {"candidate_id": "fdc_sr_legacy:7", "fdc_id": "7", "description": "Basil, fresh"}}


def test_schema_accepts_a_clean_row_and_names_each_failure():
    assert vb.check_schema([staged_row()], RULE) == {}
    bad = [staged_row(term="Basil "), staged_row(term="ba5il"), staged_row(kind="spice"), {**staged_row(), "source": "from FDC"},
           {**staged_row(), "source": "PROVISIONAL: no clause here"}, {**staged_row(), "fdc_ids": ""}]
    errs = vb.check_schema(bad, RULE)
    assert set(errs) == {"Basil ", "ba5il", "basil"} and len(errs["basil"]) == 5          # the bad rows that share the term 'basil' are all reported, none hides another
    flat_msgs = " | ".join(m for v in errs.values() for m in v)
    for needle in ("not clean lowercase", "is not one of", "does not start with PROVISIONAL", "verbatim clause", "missing column or value: fdc_ids"):
        assert needle in flat_msgs, needle


def test_provenance_needs_ids_present_in_candidates_and_repeated_in_the_source():
    assert vb.check_provenance([staged_row()], CAND) == {}
    assert "not in candidates.csv" in vb.check_provenance([staged_row(fdc="fdc_sr_legacy:99")], CAND)["basil"][0]
    assert "does not repeat" in vb.check_provenance([staged_row(desc="Basil, dried")], CAND)["basil"][0]
    assert "no FDC candidate ids" in vb.check_provenance([{**staged_row(), "fdc_ids": ""}], CAND)["basil"][0]


def test_duplicates_exact_synonym_recognised_and_variants():
    lexicon = [{"term": "cumin", "kind": "herb_spice"}, {"term": "ginger", "kind": "herb_spice"}]
    synonyms = [{"from": "jeera", "to": "cumin"}]
    rec = lambda t: t == "garlic powder"
    rows = [staged_row("ginger"), staged_row("jeera"), staged_row("garlic powder"), staged_row("cumin seed"), staged_row("basil")]
    d = vb.check_duplicates(rows, lexicon, synonyms, rec)
    assert "exact lexicon term" in d["ginger"]["duplicate"] and "alias of 'cumin'" in d["jeera"]["duplicate"] and "already recognised" in d["garlic powder"]["duplicate"]
    assert d["cumin seed"]["variant_of"] == ["cumin"] and "duplicate" not in d["cumin seed"]
    assert "basil" not in d


def test_ambiguity_queue_passes_ws3_queue_rows_and_parks_conflicts_and_marker_terms():
    decisions = [{"candidate_id": "x:1", "description": "Spices, curry powder", "decision": "QUEUE", "reason_code": "form_embedded_in_name", "reason": "blend?", "term": ""},
                 {"candidate_id": "x:2", "description": "Spices, bay leaf", "decision": "ACCEPT", "reason_code": "c", "reason": "r", "term": "bay leaf"}]
    lexicon = [{"term": "oregano", "kind": "culinary"}]
    markers = [{"term": "colour"}]
    q = vb.ambiguity([staged_row("oregano", "herb_spice"), staged_row("colour")], decisions, lexicon, markers)
    codes = sorted((x["origin"], x["reason_code"]) for x in q)
    assert codes == [("clause_tier", "form_embedded_in_name"), ("gate", "equals_marker_term"), ("gate", "kind_conflict")]


def test_append_rows_keeps_existing_bytes_quotes_properly_and_repairs_a_missing_newline(tmp_path):
    f = tmp_path / "lexicon.csv"
    f.write_bytes(b"term,kind,source\nsalt,culinary,\"x, y\"")                         # no trailing newline
    vb.append_rows(f, [{"term": "basil", "kind": "herb_spice", "source": 'PROVISIONAL: "q", z'}])
    rows = list(csv.DictReader(f.open(encoding="utf-8")))
    assert [r["term"] for r in rows] == ["salt", "basil"] and rows[1]["source"] == 'PROVISIONAL: "q", z' and rows[0]["source"] == "x, y"


def test_cores_strip_descriptors_and_plurals():
    assert "cow milk" in vb.cores("Pasteurized Cow Milk (3%)", {"pasteurized"})
    assert "almond" in vb.cores("Almonds", set())


def run_flip(rows):
    # These probes depend on the frozen corpus and on the term still being open: if a probe term is ever added to the lexicon, pick another open term
    # from evaluation/demand_inventory_1/ (the assertion below says so instead of failing obscurely).
    from foodscan.classify import is_recognised
    from foodscan.normalise import normalise_ingredient
    for r in rows:
        assert not is_recognised(normalise_ingredient(r["term"]).name), f"probe term {r['term']!r} is in the lexicon now: choose another open term from evaluation/demand_inventory_1/"
    with tempfile.TemporaryDirectory() as td:
        runs = vb.flip_check(rows, SRC, EVAL, Path(td))
    desc = {r["word"].lower() for r in vb.read_csv(SRC / "foodscan" / "resources" / "descriptors.csv")}
    return runs, vb.attribute(runs["before"], runs["after"], rows, desc)


def test_flip_harness_reports_a_harmless_row_with_attributed_unassessed_drops_only():
    rows = [{"term": "cocoa solids", "kind": "herb_spice", "source": "PROVISIONAL: test"}]           # unassessed on 5 frozen inputs, changes no group
    runs, a = run_flip(rows)
    assert len(runs["before"]) == 66 and a["changed_counts"]["unassessed"] == 5 and a["flips"] == [] and a["unexplained"] == []
    assert all(v["attributed_to_rows"] == ["cocoa solids"] for v in a["unassessed_attribution"].values())


def test_flip_harness_detects_and_blocks_a_group_flip():
    rows = [{"term": "cow milk", "kind": "whole_food", "source": "PROVISIONAL: test"}]               # b2/M02 and b3/Q06 abstain today; with this row they become Group 1
    _, a = run_flip(rows)
    assert a["flips"] == ["b2/M02", "b3/Q06"] and a["group_flips"] == {"b2/M02": [None, 1], "b3/Q06": [None, 1]} and a["unexplained"] == []


def test_flip_harness_proves_the_after_build_holds_the_change_and_refuses_otherwise(monkeypatch):
    runs, _ = run_flip([{"term": "cocoa solids", "kind": "herb_spice", "source": "PROVISIONAL: test"}])
    h = runs["harness"]
    assert h["lexicon_rows_after"] == h["lexicon_rows_before"] + 1 and h["terms_recognised_before"] == [] and h["terms_recognised_after"] == 1
    # an 'after' that silently lacks the row (the failure that invalidated a past flip check) must raise, not report 0 changes
    monkeypatch.setattr(vb, "append_rows", lambda f, rows: None)
    with pytest.raises(RuntimeError, match="harness invalid"):
        with tempfile.TemporaryDirectory() as td:
            vb.flip_check([{"term": "cocoa solids", "kind": "herb_spice", "source": "PROVISIONAL: test"}], SRC, EVAL, Path(td))


def test_flip_harness_never_touches_the_repo_resources():
    res = SRC / "foodscan" / "resources" / "lexicon.csv"
    before = hashlib.sha256(res.read_bytes()).hexdigest()
    run_flip([{"term": "cocoa solids", "kind": "herb_spice", "source": "PROVISIONAL: test"}])
    assert hashlib.sha256(res.read_bytes()).hexdigest() == before


def test_run_gate_end_to_end_and_report_writing(tmp_path):
    cand = tmp_path / "cand.csv"
    rows = [{"candidate_id": "fdc_sr_legacy:7", "dataset": "sr_legacy", "data_type": "sr_legacy_food", "fdc_id": "7", "description": "Zorbium, fresh", "description_norm": "zorbium, fresh",
             "parts": json.dumps(["zorbium", "fresh"]), "food_category_id": "2", "food_category": "Spices and Herbs", "publication_date": "2018-04-01", "dataset_release": "2018-04",
             "source_url": "https://fdc.nal.usda.gov/x.zip", "licence": "CC0 1.0 Universal"},
            {"candidate_id": "fdc_sr_legacy:8", "dataset": "sr_legacy", "data_type": "sr_legacy_food", "fdc_id": "8", "description": "Spices, curry powder", "description_norm": "spices, curry powder",
             "parts": json.dumps(["spices", "curry powder"]), "food_category_id": "2", "food_category": "Spices and Herbs", "publication_date": "2018-04-01", "dataset_release": "2018-04",
             "source_url": "https://fdc.nal.usda.gov/x.zip", "licence": "CC0 1.0 Universal"}]
    with cand.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
    decisions, staged = ct.map_candidates(rows, RULE)
    ct.write_csv(tmp_path / "decisions.csv", decisions, ["candidate_id", "dataset", "fdc_id", "description", "food_category", "decision", "reason_code", "reason", "term"], False)
    ct.write_csv(tmp_path / "staged_rows.csv", staged, ["term", "kind", "source", "fdc_ids", "rule_id"], False)
    out = tmp_path / "gate"
    code = vb.main(["--staged", str(tmp_path / "staged_rows.csv"), "--decisions", str(tmp_path / "decisions.csv"), "--candidates", str(cand), "--out", str(out)])
    assert code == 0
    g = json.loads((out / "gate_report.json").read_text())
    assert g["verdict"] == "READY_FOR_REVIEW" and g["ready"] == ["zorbium"] and [q["reason_code"] for q in g["ambiguity_queue"]] == ["form_embedded_in_name"]
    assert g["flip"]["changed_counts"]["group"] == 0 and g["clause_check"].startswith("NOT CHECKED")
    assert sorted(p.name for p in out.iterdir()) == ["ambiguity_queue.csv", "flip_after.json", "flip_before.json", "gate_report.json", "gate_report.md", "lexicon_candidate_rows.csv"]
    assert (out / "lexicon_candidate_rows.csv").read_text().splitlines()[0] == "term,kind,source"
    assert vb.main(["--staged", str(tmp_path / "staged_rows.csv"), "--decisions", str(tmp_path / "decisions.csv"), "--candidates", str(cand), "--out", str(out)]) == 2   # refuses to overwrite
