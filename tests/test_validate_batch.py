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
    # UPDATED (per-form-2b): 'cow milk' became a lexicon row (species-head milk recognition), so the probe term moved, as the run_flip assertion instructs. 'synthetic vinegar' is the one unassessed item of the
    # frozen b1/N10 list; with a row for it that list becomes fully recognised and moves None -> 3. Same purpose: the harness detects and blocks a group flip.
    rows = [{"term": "synthetic vinegar", "kind": "whole_food", "source": "PROVISIONAL: test"}]
    _, a = run_flip(rows)
    assert a["flips"] == ["b1/N10"] and a["group_flips"] == {"b1/N10": [None, 3]} and a["unexplained"] == []


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
    assert sorted(p.name for p in out.iterdir()) == ["ambiguity_queue.csv", "flip_after.json", "flip_before.json", "gate_report.json", "gate_report.md", "lexicon_candidate_rows.csv", "synonyms_candidate_rows.csv"]
    assert (out / "lexicon_candidate_rows.csv").read_text().splitlines()[0] == "term,kind,source"
    assert vb.main(["--staged", str(tmp_path / "staged_rows.csv"), "--decisions", str(tmp_path / "decisions.csv"), "--candidates", str(cand), "--out", str(out)]) == 2   # refuses to overwrite


# ---- variant policy (SYNTHETIC lexicon and staged rows; unit tests of the policy mechanics, not coverage evidence) ----
LEX = [{"term": "zing", "kind": "herb_spice", "source": "x"}, {"term": "quill", "kind": "herb_spice", "source": "x"}]
POL = {"policy_id": "variant-policy-test",
       "synonyms": {"zing seed": {"to": "zing", "basis": "same ingredient, same plant part (seed), same form as the existing row"}},
       "separate_rows": {"quill leaf": "different plant part from quill seed", "quill seed": "different plant part from quill leaf"},
       "parked": {"flax seed": {"reason_code": "overlaps_conditioned_clause", "reason": "boundary unresolved"}}}


def _staged(*terms):
    return [staged_row(term=t, fdc=f"fdc_sr_legacy:{i}", desc=f"Spices, {t}", fid=str(i)) for i, t in enumerate(terms, 1)]


def _cands(*terms):
    return {f"fdc_sr_legacy:{i}": {"candidate_id": f"fdc_sr_legacy:{i}", "dataset": "sr_legacy", "fdc_id": str(i), "description": f"Spices, {t}"} for i, t in enumerate(terms, 1)}


def test_policy_maps_same_part_variant_to_a_synonym_keeps_other_parts_and_parks_boundary_terms():
    terms = ("zing seed", "quill leaf", "quill seed", "flax seed")
    staged = _staged(*terms)
    dups = vb.check_duplicates(staged, LEX, [], lambda t: False)
    r = vb.apply_policy(staged, dups, POL, LEX, [], _cands(*terms))
    assert r["errors"] == []
    assert [(x["from"], x["to"]) for x in r["synonym_rows"]] == [("zing seed", "zing")]
    assert r["synonym_rows"][0]["source"].startswith("PROVISIONAL: alias of existing lexicon row \"zing\"") and "FDC id 1 \"Spices, zing seed\"" in r["synonym_rows"][0]["source"]
    assert [(q["term"], q["origin"], q["reason_code"]) for q in r["queue"]] == [("flax seed", "policy", "overlaps_conditioned_clause")]


def test_policy_blocks_an_unpoliced_variant_so_the_inconsistency_cannot_return():
    staged = _staged("quill leaf")                       # a variant of existing 'quill' that the policy does not mention
    dups = vb.check_duplicates(staged, LEX, [], lambda t: False)
    assert "variant_of" in dups["quill leaf"]
    r = vb.apply_policy(staged, dups, {"policy_id": "p", "synonyms": {}, "separate_rows": {}, "parked": {}}, LEX, [], _cands("quill leaf"))
    assert any("quill leaf" in e and "neither maps it to a synonym nor keeps it as a separate row" in e for e in r["errors"])


def test_policy_errors_are_reported_for_bad_targets_stale_entries_and_double_dispositions():
    staged = _staged("zing seed")
    dups = vb.check_duplicates(staged, LEX, [], lambda t: False)
    bad = {"policy_id": "p", "synonyms": {"zing seed": {"to": "nonexistent", "basis": "b"}, "ghost seed": {"to": "zing", "basis": "b"}},
           "separate_rows": {"zing seed": "x", "ghost leaf": "y"}, "parked": {"zing seed": {"reason_code": "c", "reason": "r"}}}
    errs = " | ".join(vb.apply_policy(staged, dups, bad, LEX, [], _cands("zing seed"))["errors"])
    assert "target is not an existing lexicon row" in errs and "'ghost seed' is not a staged term" in errs and "'ghost leaf' is not a staged term" in errs and "two different dispositions" in errs
    existing = vb.apply_policy(staged, dups, {"policy_id": "p", "synonyms": {"zing seed": {"to": "zing", "basis": "b"}}, "separate_rows": {}, "parked": {}}, LEX,
                               [{"from": "zing seed", "to": "zing", "source": "x"}], _cands("zing seed"))
    assert any("already exists" in e for e in existing["errors"])


def test_real_policy_file_is_consistent_with_the_rule_and_with_itself():
    pol = vb.load_policy(REPO_ROOT / "data" / "ingest" / "variant_policy_1.json")
    assert pol["policy_id"] == "variant-policy-1"
    sets = [set(pol["synonyms"]), set(pol["separate_rows"]), set(pol["parked"])]
    assert not (sets[0] & sets[1]) and not (sets[0] & sets[2]) and not (sets[1] & sets[2])
    assert "poppy seed" in pol["parked"] and pol["parked"]["poppy seed"]["reason_code"] == "overlaps_conditioned_clause"
    assert {"coriander leaf", "coriander seed", "dill weed", "dill seed", "peppermint", "spearmint"} <= set(pol["separate_rows"])
    assert set(pol["synonyms"]) == {"anise seed", "caraway seed", "cumin seed", "fenugreek seed"}
    assert "coriander" not in pol["synonyms"] and "dill" not in pol["synonyms"]            # bare ambiguous base terms are never widened
    assert all("seed" in t for t in pol["synonyms"])                                         # only same-part (seed) forms become synonyms


def test_append_synonyms_keeps_existing_bytes_and_quotes(tmp_path):
    f = tmp_path / "synonyms.csv"
    f.write_bytes(b"from,to,source\r\na,b,c")
    vb.append_synonyms(f, [{"from": "x seed", "to": "x", "source": 'has "quotes", commas'}])
    with f.open(encoding="utf-8", newline="") as fh:               # portable on 3.12 (Path.read_text(newline=) is 3.13+); newline="" keeps the CRLF and the quoting intact
        rows = list(csv.DictReader(fh))
    assert rows[-1] == {"from": "x seed", "to": "x", "source": 'has "quotes", commas'} and rows[0]["from"] == "a"
