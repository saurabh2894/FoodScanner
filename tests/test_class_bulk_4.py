"""class-bulk-4 / Batch 4 Grains (PROPOSAL on a branch; merge stops with the owner). SYNTHETIC unit cases for the grains rule and the flour-kind unknown-bracket abstention."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import class_batch as cb  # noqa: E402

from foodscan.pipeline import analyse_text  # noqa: E402

RULE = json.loads((ROOT / "data" / "ingest" / "class_grains_1.json").read_text(encoding="utf-8"))
OUT = ROOT / "evaluation" / "class_bulk_4" / "grains"
RES = ROOT / "src" / "foodscan" / "resources"
LEX = {r["term"]: r for r in csv.DictReader((RES / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}


def dec(desc, attrs=None, cat="Cereal Grains and Pasta"):
    return cb.decide({"description": desc, "food_category": cat}, attrs or {"portions": [], "foodon": ""}, RULE)


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return (a.group if a.answered else None), a


def test_synthetic_plain_grains_and_plain_flours_are_accepted_with_a_derived_term():
    assert dec("Wild rice, dry, raw")["term"] == "wild rice"
    assert dec("Flour, rye")["term"] == "rye flour"
    assert dec("Buckwheat, whole grain")["decision"] == "ACCEPT"
    assert dec("Rice, brown, long-grain, raw (Includes foods for USDA's Food Distribution Program)")["decision"] == "ACCEPT"


def test_synthetic_enriched_bleached_pregelatinized_cooked_pasta_starch_gluten_and_branded_forms_never_accept():
    for d in ("Wheat flour, white, all-purpose, enriched, bleached", "Rice, white, long-grain, regular, enriched, cooked", "Oat flour, pre-gelatinized", "Spaghetti, dry, enriched", "Noodles, egg, cooked",
              "Vital wheat gluten", "Hominy, canned, white", "Rice, brown, parboiled, dry, UNCLE BEN'S", "Tapioca, pearl, dry", "Corn flour, masa harina, white or yellow, dry, raw", "Rice bran, crude", "Flour, wheat, self-rising"):
        assert dec(d)["decision"] in ("REJECT", "QUEUE"), d
    assert dec("Vital wheat gluten")["decision"] in ("REJECT", "QUEUE") and dec("Hominy, canned, white")["decision"] == "REJECT"


def test_synthetic_sprouted_pearled_roasted_malt_and_corn_forms_are_queued_for_owner_decisions():
    for d in ("Wheat, sprouted", "Barley, pearled, raw", "Buckwheat groats, roasted, dry", "Barley malt flour", "Corn grain, yellow", "Bulgur, dry", "Couscous, dry", "Einkorn, grain, dry, raw"):
        assert dec(d)["decision"] in ("QUEUE", "REJECT"), d
    assert dec("Wheat, sprouted")["decision"] == "QUEUE" and dec("Bulgur, dry")["decision"] == "QUEUE" and dec("Corn grain, yellow")["decision"] == "QUEUE"


def test_synthetic_the_committed_rows_repeat_the_route_clause_and_kinds_follow_the_word_flour():
    S = list(csv.DictReader((OUT / "staged_rows.csv").open(encoding="utf-8", newline="")))
    texts = [RULE["clause"]["text"]] + [c["text"] for c in RULE["clauses_alt"]]
    assert S and all(r["source"].startswith("PROVISIONAL") and any(t in r["source"] for t in texts) for r in S)
    for r in S:
        assert r["kind"] == ("flour" if any(w in r["term"] for w in ("flour", "meal", "semolina")) else "whole_food"), r["term"]


def test_synthetic_the_applied_state_gate_is_clean_and_the_14_rows_are_in_the_lexicon():
    C = json.loads((OUT / "applied_gate" / "applied_gate.json").read_text(encoding="utf-8"))
    assert C["verdict"] == "READY_FOR_REVIEW" and not C["blockers"] and C["drift"]["differences"] == {}
    assert len(C["after_build_proof"]) == 14 and all(v["recognised_after"] and not v["recognised_before"] for v in C["after_build_proof"].values())
    for k in ("frozen_66", "out_of_sample"):
        assert C[k]["unexplained"] == [] and C[k]["abstain_to_4"] == [] and C[k]["abstain_to_1"] == []
    assert C["powder_surface"]["group1_after_forms_not_stated"] == [] and all(C["synonyms_markers_untouched"].values())
    assert set(C["lexicon_rows"]["added"]) <= set(LEX)


@pytest.mark.parametrize("t", ["Rye Flour", "Oat Flour", "Buckwheat", "Wild Rice", "Cornmeal", "Semolina", "Whole Wheat Flour (Atta)", "Wheat Flour (Organic)"])
def test_synthetic_plain_forms_keep_group_1_as_the_sole_item(t):
    assert g(t)[0] == 1, t


@pytest.mark.parametrize("t", ["Oat Flour (XQ9)", "Rye Flour (XQ9)", "Wheat Flour (XQ9)"])
def test_synthetic_negative_unknown_additions_on_a_flour_item_are_never_laundered(t):
    group, a = g(t)
    assert group is None and "names content the vocabulary does not recognise" in (a.reason or ""), t


@pytest.mark.parametrize("t", ["Rice, Oat Flour", "Oat Flour, Salt", "Oat Flour, Sugar", "Oat Flour, XQ9"])
def test_synthetic_a_flour_in_a_list_still_abstains_and_unknowns_stay_unassessed(t):
    group, a = g(t)
    assert group is None, t


@pytest.mark.parametrize("t", ["Enriched Wheat Flour", "Bleached Wheat Flour", "Fortified Wheat Flour", "Pre-gelatinized Oat Flour", "Arrowroot Flour", "Semolina Pasta", "Masa Harina", "Rice Noodles"])
def test_synthetic_negative_forms_outside_the_vocabulary_stay_unassessed(t):
    group, a = g(t)
    assert group is None and t.lower() in " ".join(u.lower() for u in a.unassessed), t
