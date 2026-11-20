"""_peel_label guard (bounded repair): a candidate section label that holds a descriptor or form word is an ingredient NAME, never a label.
Every case here is SYNTHETIC (written for these tests; not a label, not evidence). The S19 case reproduces only the SHAPE of a real out-of-sample segment."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from foodscan.parser import _FORM_WORDS_EXTRA, _peel_label, parse_ingredient_list
from foodscan.pipeline import analyse_text

RES = Path(__file__).resolve().parent.parent / "src" / "foodscan" / "resources"
DESCRIPTORS = [r["word"].lower() for r in csv.DictReader((RES / "descriptors.csv").open(encoding="utf-8-sig", newline=""))]

S19_SHAPE = "Ingredients: Rice flour, salt, Paprika Powder Flake(0.6%): Roasted Sesame, Roasted Seaweed."


def test_synthetic_s19_shape_stays_whole_with_no_phantom_section_and_stays_flagged():
    p = parse_ingredient_list(S19_SHAPE)
    assert "Paprika Powder Flake(0.6%): Roasted Sesame" in p.items            # one whole item, as before the new paprika row
    assert [s.label for s in p.sections] == [None]                              # no "Powder Flake 0.6%" section
    a = analyse_text(S19_SHAPE, source="text")
    assert any("section label may not have been split" in w for w in a.warnings)
    assert a.completeness["status"] == "uncertain"
    assert "a section label may not have been split from an ingredient" in a.completeness["reasons"]


@pytest.mark.parametrize("item", [
    "PAPRIKA POWDER FLAKE(0.6%): ROASTED SESAME", "Paprika Powder Flake (0.6%): Roasted Sesame", "Paprika Flakes: Roasted Sesame",
    "Rice Bran Oil Seasoning Powder : Onion", "Rice Bran Oil Dried Flakes (5%): Onion", "Rice Bran Oil Powder Seasoning : Onion"])
def test_synthetic_no_candidate_label_with_a_form_word_is_accepted_whichever_candidate_the_loop_tries_first(item):
    assert _peel_label(item) is None


@pytest.mark.parametrize("word", DESCRIPTORS + ["flake", "flakes"])
def test_synthetic_every_descriptor_and_flake_word_blocks_the_peel(word):
    assert _peel_label(f"Rice Bran Oil {word.capitalize()} : Onion") is None
    assert _peel_label(f"Rice Bran Oil Seasoning {word} : Onion") is None


@pytest.mark.parametrize("item, expected", [
    ("Rice Bran Oil Seasoning : Onion", ("Rice Bran Oil", "Seasoning", "Onion")),
    ("Rice Bran Oil Seasoning (12%): Onion", ("Rice Bran Oil", "Seasoning 12%", "Onion"))])
def test_synthetic_positive_control_a_real_section_pattern_still_peels(item, expected):
    assert _peel_label(item) == expected


def test_synthetic_positive_control_end_to_end_same_line_section_still_splits():
    p = parse_ingredient_list("Ingredients: Rice, Rice Bran Oil Seasoning : Onion, salt, flavour.")
    assert [s.label for s in p.sections] == [None, "Seasoning"] and not any(":" in i for i in p.items)


# ---- sweep: the batch's new known prefixes x label-like suffixes (SYNTHETIC; scripts/peel_sweep.py is the exploratory version) ----
NEW_PREFIXES = ["allspice", "basil", "celery seed", "chervil", "coriander leaf", "coriander seed", "dill seed", "dill weed", "marjoram", "oregano", "paprika", "parsley", "peppermint",
                "rosemary", "saffron", "sage", "savory", "spearmint", "tarragon", "thyme", "aniseed", "caraway", "cumin", "fenugreek"]      # 20 rows + the 4 rows the synonyms point to
NAME_SUFFIXES = ["POWDER FLAKE (0.6%)", "POWDER FLAKE", "FLAKE", "FLAKES (2%)", "POWDER (3%)", "DRIED", "EXTRACT (5%)", "EXTRACT", "MIX (10%)", "MIX", "BLEND", "BLEND (2%)", "PASTE"]
GENUINE_SUFFIXES = [("SEASONING", "SEASONING"), ("SEASONING (12%)", "SEASONING 12%"), ("SOUP (22.7%)", "SOUP 22.7%"), ("SAUCE", "SAUCE")]


@pytest.mark.parametrize("prefix", NEW_PREFIXES)
def test_synthetic_sweep_no_new_prefix_peels_a_phantom_label_from_a_name_or_form_suffix(prefix):
    for suf in NAME_SUFFIXES:
        assert _peel_label(f"{prefix.upper()} {suf}: Roasted Sesame") is None, (prefix, suf)


@pytest.mark.parametrize("prefix", NEW_PREFIXES)
def test_synthetic_sweep_positive_controls_genuine_headers_still_peel_after_every_new_prefix(prefix):
    for suf, label in GENUINE_SUFFIXES:
        got = _peel_label(f"{prefix.upper()} {suf}: Roasted Sesame")
        assert got == (prefix.upper(), label, "Roasted Sesame"), (prefix, suf, got)


def test_guard_word_set_is_exactly_descriptors_plus_flake_plus_the_named_rule_file_form_words():
    rule = json.loads((Path(__file__).resolve().parent.parent / "data" / "ingest" / "clause_tier1_herbs_spices.json").read_text(encoding="utf-8"))
    processed = set(rule["processed_words"]["words"])
    excluded_on_purpose = {"seasoning", "sauce", "imitation", "flavor", "flavour"}
    from_rule = {"extract", "paste", "mix", "blend", "syrup", "cooked", "canned", "pickled", "prepared"}
    assert from_rule == processed - excluded_on_purpose, "the rule file's processed words changed: re-decide the guard set explicitly"
    assert {"flake", "flakes"} | from_rule | {w + "s" for w in ("extract", "paste", "blend")} | {"mixes"} == set(_FORM_WORDS_EXTRA)
    assert not (excluded_on_purpose & set(_FORM_WORDS_EXTRA)) and not (excluded_on_purpose & set(DESCRIPTORS))
