"""class-bulk-1 / Batch 1 Legumes (owner-approved 2026-11-21; 21 new rows of kind legume plus the item-level guard; synonyms.csv and markers.csv are untouched). SYNTHETIC unit cases for scripts/class_batch.py and checks on the committed batch outputs."""
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


def test_synthetic_the_committed_decisions_match_the_rule_and_every_row_repeats_the_verbatim_clause_and_the_condition():
    S = list(csv.DictReader((OUT / "staged_rows.csv").open(encoding="utf-8", newline="")))
    assert S and all(RULE["clause"]["text"] in r["source"] and r["source"].startswith("PROVISIONAL") and r["kind"] == "legume" and "CONDITION KEPT AT ITEM LEVEL" in r["source"] for r in S)
    D = list(csv.DictReader((OUT / "decisions.csv").open(encoding="utf-8", newline="")))
    assert len(D) == 351
    for d in D:
        again = cb.decide({"description": d["description"], "food_category": d["food_category"]}, {"portions": [p for p in d["portions"].split("|") if p]}, RULE)
        assert (again["decision"] == "ACCEPT") == (d["decision"] == "ACCEPT") or d["reason_code"] == "dedupe_stays_out", d["description"]


def test_synthetic_the_applied_state_gate_is_clean_and_the_21_rows_are_really_in_the_lexicon():
    C = json.loads((OUT / "applied_gate" / "applied_gate.json").read_text(encoding="utf-8"))
    assert C["verdict"] == "READY_FOR_REVIEW" and not C["blockers"] and C["drift"]["differences"] == {}
    assert len(C["after_build_proof"]) == 21 and all(v["recognised_after"] and not v["recognised_before"] for v in C["after_build_proof"].values())
    for k in ("frozen_66", "out_of_sample"):
        assert C[k]["unexplained"] == [] and C[k]["abstain_to_4"] == []
    assert all(C["synonyms_markers_untouched"].values()) and len(C["lexicon_rows"]["kind_changed"]) == 12 and len(C["lexicon_rows"]["added"]) == 21
    lex = {r["term"]: r for r in csv.DictReader((RES / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}
    assert set(C["after_build_proof"]) <= set(lex)
    for t in ("chickpeas", "lentils", "split green peas"):
        assert t not in lex                                                       # the 5 already-covered terms created no duplicate row
    syn = {r["from"] for r in csv.DictReader((RES / "synonyms.csv").open(encoding="utf-8-sig", newline=""))}
    cand = list(csv.DictReader((OUT / "synonym_candidates.csv").open(encoding="utf-8", newline="")))
    later = {r["from"] for r in csv.DictReader((ROOT / "evaluation" / "synonyms_2" / "synonym_rows.csv").open(encoding="utf-8", newline=""))}      # UPDATED: 'moth bean' and 'mat bean' were applied later by the separately gated synonyms-2 batch (FDC Common Name evidence); Batch 1 itself did not touch synonyms.csv
    # scoped-powder-5: NALT16207 independently supports these food names.
    # The historical batch gate is unchanged; only these later aliases leave its queue.
    later |= {"garbanzo bean", "garbanzo beans"}
    # nalt-names-7: only exact current Product16208/16211 naming admissions, not the old candidate queue.
    current = json.loads((ROOT / "evaluation" / "nalt_names_7" / "admission.json").read_text())
    later |= {x["name"] for x in current["aliases"] if x["concept_id"] in {16208,16211}}
    assert cand and not (({r["from"] for r in cand} & syn) - later) and "black turtle beans" not in syn


def test_synthetic_controls_in_the_applied_gate_never_take_group_1_via_the_new_rows():
    C = json.loads((OUT / "applied_gate" / "applied_gate.json").read_text(encoding="utf-8"))
    neg = C["controls"]
    for n in RULE["negative_controls"]:
        v = neg[n]
        assert not any(d == "single recognised unprocessed food" for d in v["drivers_after"]), n
        assert v["group_after"] != 1, n
    for n in ("salted pinto beans", "canned kidney beans", "baked beans"):
        assert neg[n]["group_after"] != 1
    for n in RULE["positive_controls"]:
        assert neg[n]["row_after"] is not None or neg[n]["group_after"] is not None, n
