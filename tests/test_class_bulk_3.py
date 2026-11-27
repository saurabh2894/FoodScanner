"""class-bulk-3 / Batch 3 Fruits (PROPOSAL on a branch; merge stops with the owner). SYNTHETIC unit cases for the fruit rule and the fruit kind guard (both directions)."""
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

RULE = json.loads((ROOT / "data" / "ingest" / "class_fruits_1.json").read_text(encoding="utf-8"))
OUT = ROOT / "evaluation" / "class_bulk_3" / "fruits"
RES = ROOT / "src" / "foodscan" / "resources"
LEX = {r["term"]: r for r in csv.DictReader((RES / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}


def dec(desc, attrs=None, cat="Fruits and Fruit Juices"):
    return cb.decide({"description": desc, "food_category": cat}, attrs or {"portions": [], "foodon": ""}, RULE)


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return (a.group if a.answered else None), a


def test_synthetic_plain_raw_and_frozen_unsweetened_fruit_are_accepted_with_a_derived_term():
    assert dec("Strawberries, raw")["term"] == "strawberries"
    assert dec("Raspberries, frozen, red, unsweetened")["decision"] == "ACCEPT"
    assert dec("Apples, raw, with skin (Includes foods for USDA's Food Distribution Program)")["term"] == "apples"
    assert dec("Pears, raw, bartlett")["term"] == "bartlett pears"
    # a raw record whose portions are measuring units (slices, sections, cubes) is still plain
    assert dec("Pears, raw", {"portions": ["cup, slices", "cup, cubes"], "foodon": ""})["decision"] == "ACCEPT"


def test_synthetic_juice_syrup_sweetened_canned_dried_heated_and_product_forms_never_accept():
    for d in ("Apple juice, canned or bottled, unsweetened, without added ascorbic acid", "Peaches, canned, heavy syrup pack, solids and liquids", "Strawberries, frozen, sweetened, whole",
              "Applesauce, canned, unsweetened", "Fruit cocktail, canned, juice pack", "Apples, frozen, unsweetened, heated", "Orange juice, raw", "Baobab powder", "Raisins, seedless",
              "Pineapple, canned, water pack", "Blueberries, wild, frozen, sweetened"):
        assert dec(d)["decision"] == "REJECT", d


def test_synthetic_dried_peel_pulp_and_unstated_forms_are_queued_not_accepted():
    for d in ("Apricots, dried, sulfured, uncooked", "Lemon peel, raw", "Orange peel, raw", "Naranjilla (lulo) pulp, frozen, unsweetened", "Tamarinds, raw", "Loganberries, frozen", "Olives, ripe, canned"):
        assert dec(d)["decision"] in ("QUEUE", "REJECT"), d
    assert dec("Tamarinds, raw")["decision"] == "QUEUE" and dec("Loganberries, frozen")["decision"] == "QUEUE"
    assert dec("Lemon peel, raw")["decision"] == "QUEUE"


def test_synthetic_the_committed_rows_repeat_the_clause_and_the_dedupe_collapses_cultivars():
    S = list(csv.DictReader((OUT / "staged_rows.csv").open(encoding="utf-8", newline="")))
    assert S and all(r["kind"] == "fruit" and r["source"].startswith("PROVISIONAL") and RULE["clause"]["text"] in r["source"] for r in S)
    terms = {r["term"] for r in S}
    assert "apples" in terms and not ({"fuji apples", "gala apples", "red delicious apples"} & terms)
    assert RULE["canonical"]["fuji apples"]["to"] == "apples" and RULE["canonical"]["american type grapes"]["to"] is None


def test_synthetic_the_applied_state_gate_is_clean_and_every_row_is_in_this_branchs_lexicon():
    C = json.loads((OUT / "applied_gate" / "applied_gate.json").read_text(encoding="utf-8"))
    assert C["verdict"] == "READY_FOR_REVIEW" and not C["blockers"] and C["drift"]["differences"] == {}
    n = len(C["after_build_proof"])
    assert n == 75 and all(v["recognised_after"] and not v["recognised_before"] for v in C["after_build_proof"].values())
    for k in ("frozen_66", "out_of_sample"):
        assert C[k]["unexplained"] == [] and C[k]["abstain_to_4"] == [] and C[k]["abstain_to_1"] == []
    ps = C["powder_surface"]
    assert ps["group1_after_forms_not_stated"] == [] and ps["newly_group4_or_other"] == {}
    assert all(C["synonyms_markers_untouched"].values()) and set(C["lexicon_rows"]["kind_changed"]) == {"mango", "lemon", "dates", "black raisin"}
    assert {t for t, r in LEX.items() if r["kind"] == "fruit"} == set(C["lexicon_rows"]["added"]) | set(C["lexicon_rows"]["kind_changed"]) | {"tamarind", "mangosteen", "durian", "rambutan", "red mombins", "yellow mombins", "atemoyas", "acai berries", "bilberries"} | {'bergamot oranges', 'sour oranges', 'tangors', 'tangelos', 'satsumas', 'citrus fruits', 'dewberries', 'loganberries', 'currants'} | {'raisins', 'prunes', 'goji berries', 'sapote'} | {'redcurrants', 'whitecurrants', 'damsons', 'greengages'} | {'roselle', 'amla', 'bael', 'karanda', 'phalsa', 'indian jujube'}  # cofid-fish-fruit-24: CoFID-named plain raw fruits, same basis as gooseberries; nalt-names-6/8/9/10/12: separately sourced plain fruits; no cranberry/tamarind/coconut hold lifted ; veg-24 appended additively


@pytest.mark.parametrize("t", ["Salted Plums", "Plums (in syrup)", "Mango (sweetened)", "Strawberries (sweetened)", "Strawberries (with sugar)", "Apples (Apples, Sugar)"])
def test_synthetic_negative_a_fruit_item_whose_own_name_or_bracket_adds_sugar_syrup_or_salt_never_takes_group_1(t):
    group, a = g(t)
    assert group == 3 and not any(d.detail == "single recognised unprocessed food" for d in a.drivers), (t, group)
    assert any("FAO Group 3" in d.detail for d in a.drivers)


@pytest.mark.parametrize("t", ["Mango (preserved)", "Apples (bottled)", "Lemon (pickled)", "Pineapple (canned)", "Rice, Apples (canned)"])
def test_synthetic_negative_canned_bottled_or_preserved_fruit_without_sugar_syrup_or_salt_abstains(t):
    group, a = g(t)
    assert group is None and "canned, bottled or preserved" in (a.reason or ""), t


@pytest.mark.parametrize("t", ["Apples", "Bananas", "Strawberries (frozen)", "Strawberries (no added sugar)", "Strawberries (sugar free)", "Dates", "Black Raisin", "Mango", "Lemon", "Oranges"])
def test_synthetic_plain_negated_and_frozen_forms_keep_group_1(t):
    assert g(t)[0] == 1, t


@pytest.mark.parametrize("t", ["Mango Powder", "Banana Powder", "Strawberry Powder", "Apple Powder", "Spinach & Apple Powder"])
def test_synthetic_the_powder_standard_applies_to_fruit_rows(t):
    group, a = g(t)
    assert group is None and "named without its composition" in (a.reason or ""), t
    assert g("100% Mango Powder")[0] == 1 and g("Whole Banana Powder")[0] == 1


@pytest.mark.parametrize("t", ["Canned Peaches", "Peaches in Syrup", "Applesauce", "Fruit Cocktail", "Strawberry Jam", "Banana Chips", "Raisins in Syrup"])
def test_synthetic_negative_forms_outside_the_vocabulary_never_get_group_1(t):
    group, a = g(t)
    assert group is None and t.lower() in " ".join(u.lower() for u in a.unassessed), t


# DRIED FORMS (owner requirement, class-bulk-3): V1 names 'dried' fruit, so a bare 'dried X' is Group 1 through the existing 'dried' descriptor ONLY when no condition word attaches. Condition words
# (sugar, sweetened, syrup, honey, jaggery, candied, glazed) take the guard to Group 3; a recognised Group 2 substance in the item's own bracket (oil) is an added group 2 ingredient (Group 3 definition);
# unknown additions on the same item are never laundered (the item abstains).
@pytest.mark.parametrize("t", ["Dried Pineapple", "Dried Mango", "Dried Papaya", "Dried Banana", "Dried Blueberries", "Dried Cherries", "Dried Mango (Organic)", "Dried Apricots"])
def test_synthetic_bare_dried_forms_of_the_commonly_sweetened_set_take_group_1_via_v1_dried(t):
    assert g(t)[0] == 1, t


@pytest.mark.parametrize("t", ["Dried Mango (Sugar)", "Dried Banana (Honey)", "Dried Papaya (Jaggery)", "Dried Cherries (Syrup)", "Dried Pineapple (Mango, Sugar)", "Dried Blueberries (Sunflower Oil)"])
def test_synthetic_negative_dried_forms_with_a_stated_condition_never_take_group_1(t):
    group, a = g(t)
    assert group == 3 and not any(d.detail == "single recognised unprocessed food" for d in a.drivers), (t, group)


@pytest.mark.parametrize("t", ["Dried Mango (XQ9)", "Dried Pineapple (Sugar, XQ9)", "Dried Mango (Sulphur Dioxide)", "Mango (XQ9)", "Rice, Dried Mango (XQ9)"])
def test_synthetic_negative_unknown_additions_on_the_same_item_are_never_laundered(t):
    group, a = g(t)
    assert group is None and "names content the vocabulary does not recognise" in (a.reason or ""), (t, group)


@pytest.mark.parametrize("t", ["Sweetened Dried Mango", "Candied Pineapple", "Dried Cranberries (Sugar)", "Dried Cranberries", "Dried Mango Slices (Glazed)"])
def test_synthetic_negative_sweetened_candied_cranberry_and_glazed_forms_stay_unassessed(t):
    group, a = g(t)
    assert group is None and t.lower() in " ".join(u.lower() for u in a.unassessed), t
