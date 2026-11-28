"""herb_spice_bulk_1 as merged: SYNTHETIC unit cases only. They are hand-written probes of recognition behaviour (positive disambiguation, negatives, near-miss aliases,
hint words). They are not labels, not external evidence and never counted as coverage; real-label evidence lives in evaluation/out_of_sample_herb_spice_1/."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from foodscan.classify import is_recognised
from foodscan.normalise import normalise_ingredient
from foodscan.pipeline import analyse_text

RES = Path(__file__).resolve().parent.parent / "src" / "foodscan" / "resources"


def rec(term: str) -> bool:
    return bool(is_recognised(normalise_ingredient(term).name))


def lex() -> dict[str, dict]:
    with (RES / "lexicon.csv").open(encoding="utf-8-sig", newline="") as fh:
        return {r["term"]: r for r in csv.DictReader(fh)}


NEW_ROWS = ["allspice", "basil", "celery seed", "chervil", "coriander leaf", "coriander seed", "dill seed", "dill weed", "marjoram", "oregano", "paprika", "parsley", "peppermint",
            "rosemary", "saffron", "sage", "savory", "spearmint", "tarragon", "thyme"]
SYNONYMS = {"anise seed": "aniseed", "caraway seed": "caraway", "cumin seed": "cumin", "fenugreek seed": "fenugreek"}


@pytest.mark.parametrize("t", NEW_ROWS)
def test_synthetic_positive_each_new_row_is_a_herb_spice_row_with_a_provisional_verbatim_source(t):
    r = lex()[t]
    assert r["kind"] == "herb_spice" and r["source"].startswith("PROVISIONAL: FAO 2019") and "herbs and spices used in culinary preparations" in r["source"]
    assert rec(t) and rec(f"Dried {t}") and rec(t.upper())


def test_synthetic_named_status_in_provenance():
    for t in ("oregano", "thyme"):
        assert "exact term IS named by the clause" in lex()[t]["source"]
    for t in set(NEW_ROWS) - {"oregano", "thyme"}:
        assert "exact term not named by the clause" in lex()[t]["source"] and "IS named" not in lex()[t]["source"]


@pytest.mark.parametrize("variant, base", SYNONYMS.items())
def test_synthetic_same_part_variants_are_synonyms_not_new_rows(variant, base):
    assert variant not in lex() and base in lex()
    assert normalise_ingredient(variant).name == base and rec(variant)


def test_synthetic_different_parts_stay_distinct_and_bare_base_rows_are_not_widened():
    assert normalise_ingredient("coriander leaf").name == "coriander leaf" and normalise_ingredient("coriander seed").name == "coriander seed"
    assert normalise_ingredient("dill weed").name == "dill weed" and normalise_ingredient("dill seed").name == "dill seed"
    assert lex()["coriander"]["source"].startswith("PROVISIONAL (source-repair-26e") and lex()["dill"]["source"] == "research/02 synthetic example 3"          # untouched
    assert "coriander" not in {r["from"] for r in csv.DictReader((RES / "synonyms.csv").open(encoding="utf-8-sig"))}
    assert rec("peppermint") and rec("spearmint") and rec("mint") and "peppermint" not in SYNONYMS


@pytest.mark.parametrize("t", ["poppy seed", "curry powder", "prepared mustard", "seasoning mix", "poultry seasoning", "pumpkin pie spice", "vanilla extract", "canned capers"])
def test_synthetic_negative_parked_or_rejected_forms_are_not_recognised(t):
    assert not rec(t) and t not in lex()


@pytest.mark.parametrize("t", ["garlic powder", "onion powder"])  # chilli powder reversed by general-25e: FAO Group 1 names spices "whole or powdered" and FSSAI 2.9.3(2) defines chilli powder; this batch only asserted it was not touched
def test_synthetic_negative_no_new_row_or_synonym_was_added_for_the_parked_powders(t):
    assert t not in lex() and t not in {r["from"] for r in csv.DictReader((RES / "synonyms.csv").open(encoding="utf-8-sig"))}        # whatever they do today is unchanged by this batch


@pytest.mark.parametrize("t", ["oregano extract", "paprika extract", "paprika oleoresin", "rosemary extract", "basil flavour", "thyme flavouring", "saffron colour", "peppermint oil",
                               "sage tea", "basil pesto", "parsley sauce", "mixed herbs", "italian seasoning"])
def test_synthetic_negative_hint_words_and_processed_forms_do_not_pass_as_the_plain_herb(t):
    assert not rec(t)


@pytest.mark.parametrize("t", ["cuminseed", "oreganoo", "thymee", "basill", "aniseeds x", "dill-weedy", "corianderleaf", "sagee"])
def test_synthetic_negative_near_miss_aliases_do_not_match(t):
    assert not rec(t)


@pytest.mark.parametrize("t", ["cumin seeds", "caraway seeds", "fenugreek seeds", "anise seeds", "coriander leaves", "oregano leaves"])
def test_synthetic_formerly_known_gap_plural_and_part_forms_now_recognised(t):
    """These six were strict xfails (a documented gap measured on the out-of-sample set); plural-policy-1 fixed them, so the marker was removed exactly as the xfail reason said it must be."""
    assert rec(t)


def test_synthetic_new_rows_are_recognised_in_a_list_and_do_not_by_themselves_make_a_group_4_driver():
    a = analyse_text("Ingredients: Wheat flour, salt, thyme, oregano, cumin seed, paprika", source="text")
    assert not any(x in a.unassessed for x in ("thyme", "oregano", "cumin seed", "paprika"))
    assert not any("marker" in d.detail.lower() and any(w in d.detail.lower() for w in ("thyme", "oregano", "paprika")) for d in a.drivers)


def test_merged_rows_are_byte_for_byte_the_gate_candidates():
    gate = Path(__file__).resolve().parent.parent / "evaluation" / "herb_spice_bulk_1" / "gate"
    cand = list(csv.DictReader((gate / "lexicon_candidate_rows.csv").open(encoding="utf-8", newline="")))
    syn_c = list(csv.DictReader((gate / "synonyms_candidate_rows.csv").open(encoding="utf-8", newline="")))
    L = lex()
    assert len(cand) == 20 and len(syn_c) == 4 and "poppy seed" not in L
    for r in cand:
        assert L[r["term"]]["kind"] == r["kind"] and L[r["term"]]["source"] == r["source"]
    S = {r["from"]: r for r in csv.DictReader((RES / "synonyms.csv").open(encoding="utf-8-sig", newline=""))}
    for r in syn_c:
        assert S[r["from"]]["to"] == r["to"] and S[r["from"]]["source"] == r["source"]
