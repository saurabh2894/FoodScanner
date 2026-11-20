"""Directions 1 and 3 of the batch-2 follow-up: sourced everyday dairy terms with the provenance line, and negation scoped to its exact span."""
import json
from pathlib import Path

import pytest

from foodscan.classify import is_recognised
from foodscan.parser import parse_ingredient_list
from foodscan.pipeline import analyse_text
from foodscan.tables import load_table

ROOT = Path(__file__).resolve().parent.parent


def t(x):
    return analyse_text(x, source="text")


def decl(r):
    return [d["text"] for d in r.declared]


def driver_details(r):
    return " | ".join(d.detail for d in r.drivers)


# ============================ 1. dairy vocabulary and the provenance line ====================================================
def test_milk_solids_and_starter_culture_rows_follow_the_citation_rule():
    rows = {r["term"]: r["source"] for r in load_table("lexicon.csv")}
    assert rows["milk solids"].startswith("PROVISIONAL, exact ingredient term not defined in a source") and "2.1.13 item 2(a)(ii)" in rows["milk solids"]
    assert rows["starter culture"].startswith("Identity:") and "2.1.13 item 2(b)(i)" in rows["starter culture"] and "NOVA method only" in rows["starter culture"]


@pytest.mark.parametrize("text", [
    "Ingredients: Milk, starter culture.",
    "Ingredients: Pasteurised toned milk, milk solids, active lactic cultures.",
    "Ingredients: Pasteurised double toned milk, Milk Solids, Active Lactic Cultures (L.bacillus delbrueckii subsp. bulgaricus, S.thermophilus).",
])
def test_milk_solids_and_starter_culture_now_feed_the_milk_plus_culture_rule(text):
    r = t(text)
    assert r.answered and r.group == 1, text


def test_the_provenance_line_is_milk_context_not_a_blocking_item():
    r = t("Pasteurised Toned Milk & Active Lactic Cultures, Made from Toned Milk Allergen Information: Contains Milk")
    assert r.answered and r.group == 1 and r.ingredients == ["Pasteurised Toned Milk", "Active Lactic Cultures"]
    assert r.completeness["status"] == "complete" and r.completeness["words"]["unaccounted"] == 0 and r.completeness["words"]["excluded"] >= 4    # set aside, not lost
    r2 = t("Ingredients: Pasteurised Toned Milk & Active Lactic Cultures. Made from Toned Milk.")
    assert r2.group == 1


def test_dairy_controls_the_rule_is_not_a_general_dairy_matcher():
    assert t("Ingredients: Milk solids and Sugar.").group == 3                          # milk + sugar is still group 3, not 1
    assert not t("Ingredients: Milk, active culture, xyzgum.").answered                 # one unknown item
    assert t("Ingredients: Milk, active culture, sweetener (INS 950).").group == 4
    assert not t("Ingredients: Milk, probiotic culture.").answered                      # probiotic culture is still not a starter culture
    assert not t("Ingredients: Paneer, active culture.").answered                       # no new dairy terms beyond the evidenced ones
    assert not t("Ingredients: Rice, salt, made from rice.").answered                   # only a MILK provenance line is set aside
    assert "made from rice" in t("Ingredients: Rice, salt, made from rice.").ingredients


# ============================ 3. negation scoped to its exact span ==========================================================
NEG = "Contains no added flavours, added colour or preservatives."


def test_negated_contains_line_declares_nothing_and_cannot_cause_a_false_group_4():
    r = t("Ingredients: Milk, salt. " + NEG)                       # no code decides the group: a false Group 4 would be visible here
    assert r.answered and r.group == 3 and decl(r) == [] and "Contains" not in driver_details(r)
    r = t("Ingredients: Rice, salt. " + NEG)
    assert r.group != 4 and decl(r) == [] and not any(d.detail.startswith("declared") for d in r.drivers)


@pytest.mark.parametrize("neg", ["Contains no added flavours.", "CONTAINS NO ADDED FLAVOURS,\nADDED COLOUR OR PRESERVATIVES.", "Contains nil added colour.",
                                 "Does not contain added flavour.", "Contains without added sweeteners.", "No added flavours or colours."])
def test_negation_wordings_are_not_declarations(neg):
    r = t("Ingredients: Milk, salt. " + neg)
    assert r.group == 3 and decl(r) == [], neg


def test_the_same_line_without_negation_is_a_declaration_and_decides():
    r = t("Ingredients: Milk, salt. Contains added flavours.")
    assert r.group == 4 and decl(r) and any(d.detail.startswith('declared in "Contains"') for d in r.drivers)
    assert t("Ingredients: Milk, salt. Contains permitted natural colour.").group == 4


def test_mixed_line_registers_only_the_positive_span():
    r = t("Ingredients: Milk, salt. No added colours, contains added flavour.")
    assert r.group == 4 and decl(r) == ["added flavour"] and "colour" not in " ".join(decl(r)).lower()
    r = t("Ingredients: Milk, salt. Contains added flavour, no added colours.")
    assert r.group == 4 and decl(r) == ["added flavour"]
    r = t("Ingredients: Milk, salt. No added colours, contains preservative (INS 211).")
    assert decl(r) == ["preservative (INS 211)"] and r.group != 4                 # preservative alone decides nothing; the negated colour is not read
    r = t("Ingredients: Milk, salt. Contains permitted colour, no added flavours.")
    assert r.group == 4 and decl(r) == ["permitted colour"] and "flavour" not in " ".join(decl(r)).lower()


def test_allergen_statements_are_never_drivers_in_either_direction():
    for line in ("Free from nuts.", "Contains soy, milk.", "Free from nuts. Contains soy, milk. May contain traces of sesame."):
        r = t("Ingredients: Rice, salt. " + line)
        assert r.group != 4 and not any(d.detail.startswith("declared") for d in r.drivers), line
    assert decl(t("Ingredients: Rice, salt. May contain traces of added colour.")) == []             # "may contain" is never read


def test_negation_claim_opening_a_sentence_after_the_list_is_not_an_ingredient():
    r = t("Ingredients: Milk, salt. No added colours, contains added flavour.")
    assert r.ingredients == ["Milk", "salt"] and not r.ignored and r.completeness["status"] == "complete"


def test_the_observed_photo_reading_of_the_negated_line(tmp_path):
    p = ROOT / "evaluation/fresh_batch_2/frozen_results_2eb5f39/photo_results.json"
    ocr = [x for x in json.load(p.open()) if x["id"] == "M07"][0]["ocr_readings"][0]
    r = analyse_text(ocr, source="ocr")
    assert r.group == 4 and decl(r) == [] and "declared" not in driver_details(r) and "firming" in driver_details(r)     # decided by the real marker only
