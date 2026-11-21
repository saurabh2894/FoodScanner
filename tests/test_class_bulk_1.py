"""class-bulk-1 / Batch 1 Legumes (PROPOSAL record; nothing is merged). SYNTHETIC unit cases for scripts/class_batch.py and checks on the committed batch outputs."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import class_batch as cb  # noqa: E402

RULE = json.loads((ROOT / "data" / "ingest" / "class_legumes_1.json").read_text(encoding="utf-8"))
OUT = ROOT / "evaluation" / "class_bulk_1" / "legumes"
RES = ROOT / "src" / "foodscan" / "resources"


def row(desc, cat="Legumes and Legume Products"):
    return {"description": desc, "food_category": cat}


def dec(desc, attrs=None, cat="Legumes and Legume Products"):
    return cb.decide(row(desc, cat), attrs or {"portions": []}, RULE)


def test_synthetic_plain_dry_and_raw_forms_are_accepted_with_a_derived_term():
    assert dec("Beans, Dry, Pinto (0% moisture)")["term"] == "pinto beans"
    assert dec("Beans, kidney, red, mature seeds, raw")["term"] == "red kidney beans"
    assert dec("Lentils, dry")["decision"] == "ACCEPT"
    assert dec("Beans, great northern, mature seeds, raw (Includes foods for USDA's Food Distribution Program)")["term"] == "great northern beans"
    assert dec("Beans, Dry, Light Red Kidney (0% moisture)")["decision"] == "ACCEPT"      # 'light' is a colour shade here, not a reduced-fat word


def test_synthetic_processed_product_and_queue_words_never_accept():
    for d in ("Beans, black, canned, sodium added, drained and rinsed", "Lentils, mature seeds, cooked, boiled, without salt", "Peanuts, spanish, oil-roasted, with salt",
              "Soybeans, mature seeds, roasted, salted", "Baked beans, Original, canned, with pork", "Tofu, raw, firm, prepared with calcium sulfate", "Miso", "Hummus, commercial",
              "Soymilk, original and vanilla, unfortified", "Peanut butter, smooth style, with salt", "Soy protein isolate", "Chicken, meatless, breaded, fried"):
        assert dec(d)["decision"] == "REJECT", d
    for d in ("Peanuts, all types, raw", "Chickpea flour (besan)", "Soy flour, full-fat, raw", "Soy meal, defatted, raw", "Carob flour"):
        assert dec(d)["decision"] == "QUEUE", d


def test_synthetic_a_plain_form_that_the_name_does_not_state_is_queued_not_accepted():
    assert dec("Pigeon peas (red gram)")["decision"] == "QUEUE"
    assert dec("Beans, Dry, Brown (0% moisture)")["decision"] == "QUEUE"        # bare colour class
    assert dec("Beans, french, mature seeds, raw")["decision"] == "QUEUE"       # pod versus seed
    assert dec("Lentils, raw", {"portions": ["cup cooked"]})["decision"] == "QUEUE"   # an attribute contradicts the plain form


def test_synthetic_other_categories_are_out_of_scope():
    assert dec("Lentils, raw", cat="Vegetables and Vegetable Products")["decision"] == "OUT_OF_SCOPE"


def test_synthetic_the_committed_decisions_match_the_rule_and_every_row_repeats_the_verbatim_clause():
    S = list(csv.DictReader((OUT / "staged_rows.csv").open(encoding="utf-8", newline="")))
    assert S and all(RULE["clause"]["text"] in r["source"] and r["source"].startswith("PROVISIONAL") and r["kind"] == "whole_food" for r in S)
    D = list(csv.DictReader((OUT / "decisions.csv").open(encoding="utf-8", newline="")))
    assert len(D) == 351
    for d in D:
        again = cb.decide({"description": d["description"], "food_category": d["food_category"]}, {"portions": [p for p in d["portions"].split("|") if p]}, RULE)
        assert (again["decision"] == "ACCEPT") == (d["decision"] == "ACCEPT") or d["reason_code"] == "dedupe_stays_out", d["description"]


def test_synthetic_the_gate_results_are_clean_and_the_proposal_is_not_merged():
    C = json.loads((OUT / "class_gate" / "class_gate.json").read_text(encoding="utf-8"))
    assert C["verdict"] == "READY_FOR_REVIEW" and not C["blockers"] and C["drift"]["differences"] == []
    for k in ("frozen_66", "out_of_sample"):
        assert C[k]["unexplained"] == [] and C[k]["abstain_to_4"] == []
    lex = {r["term"] for r in csv.DictReader((RES / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}
    assert not (set(C["rows"]) & lex)                       # proposal only: no staged row is in the shipped lexicon
    syn = {r["from"] for r in csv.DictReader((RES / "synonyms.csv").open(encoding="utf-8-sig", newline=""))}
    cand = list(csv.DictReader((OUT / "synonym_candidates.csv").open(encoding="utf-8", newline="")))
    assert cand and not ({r["from"] for r in cand} & syn)   # synonym candidates are not merged (synonyms.csv untouched)


def test_synthetic_negative_controls_are_not_read_as_a_staged_term():
    C = json.loads((OUT / "class_gate" / "class_gate.json").read_text(encoding="utf-8"))
    assert len(C["negative_controls"]) >= 20
    for n, v in C["negative_controls"].items():
        assert not v["read_as_staged_term"] and not v["changed"], n
