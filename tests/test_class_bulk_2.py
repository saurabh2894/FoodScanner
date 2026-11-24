"""class-bulk-2 / Batch 2 Vegetables (PROPOSAL on a branch; merge held behind the legume guard). SYNTHETIC unit cases for the vegetable rule and the vegetable kind guard (both directions)."""
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

RULE = json.loads((ROOT / "data" / "ingest" / "class_vegetables_1.json").read_text(encoding="utf-8"))
OUT = ROOT / "evaluation" / "class_bulk_2" / "vegetables"
RES = ROOT / "src" / "foodscan" / "resources"
LEX = {r["term"]: r for r in csv.DictReader((RES / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}


def dec(desc, attrs=None, cat="Vegetables and Vegetable Products"):
    return cb.decide({"description": desc, "food_category": cat}, attrs or {"portions": [], "foodon": ""}, RULE)


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return (a.group if a.answered else None), a


def test_synthetic_plain_raw_and_frozen_unprepared_forms_are_accepted_with_a_derived_term():
    assert dec("Kale, raw")["term"] == "kale"
    assert dec("Carrots, frozen, unprepared (Includes foods for USDA's Food Distribution Program)")["decision"] == "ACCEPT"
    assert dec("Squash, winter, butternut, raw")["term"] == "butternut winter squash"
    assert dec("Spinach, mature", {"portions": [], "foodon": "spinach leaf (raw)"})["decision"] == "ACCEPT"      # plain form from the Foundation FoodOn attribute


def test_synthetic_cooked_canned_salted_product_and_mixture_forms_never_accept():
    for d in ("Spinach, cooked, boiled, drained, without salt", "Tomatoes, red, ripe, canned, packed in tomato juice", "Potatoes, french fried, frozen", "Carrots, canned, regular pack, drained solids",
              "Cabbage, red, pickled", "Tomato sauce, canned", "Potatoes, mashed, home-prepared", "Vegetables, mixed, frozen, unprepared", "Potato flour", "Peppers, sweet, red, sauteed",
              "Edamame, frozen, prepared", "Mushrooms, portabella, exposed to ultraviolet light, grilled", "Potatoes, o'brien, frozen, unprepared"):
        assert dec(d)["decision"] == "REJECT", d


def test_synthetic_overlaps_unstated_forms_and_conditional_cases_are_queued_not_accepted():
    for d in ("Corn, sweet, yellow, raw", "Peas, green, raw", "Alfalfa seeds, sprouted, raw", "Seaweed, kelp, raw", "Tomatoes, sun-dried", "Ginger root, raw", "Turnip greens and turnips, frozen, unprepared", "Hearts of palm, raw"):
        assert dec(d)["decision"] == "QUEUE", d
    assert dec("Mushroom, enoki", {"portions": [], "foodon": "enoki mushroom"})["decision"] == "QUEUE"             # plain form not stated by name or attribute
    assert dec("Beets, raw")["decision"] == "QUEUE" or RULE["canonical"]["beets"]["to"] is None


def test_synthetic_the_committed_rows_repeat_the_route_clause_and_the_name_collision_terms_stay_out():
    S = list(csv.DictReader((OUT / "staged_rows.csv").open(encoding="utf-8", newline="")))
    texts = [RULE["clause"]["text"]] + [c["text"] for c in RULE["clauses_alt"]]
    assert S and all(r["kind"] == "vegetable" and r["source"].startswith("PROVISIONAL") and any(t in r["source"] for t in texts) for r in S)
    terms = {r["term"] for r in S}
    for t in ("beets", "celery", "arrowroot"):
        assert t not in terms and (t not in LEX or t=='celery')                                   # name-collision terms queued for an owner decision (descriptor handling)
    assert any("potatoes, sweet potatoes and cassava" in r["source"] for r in S if r["term"] == "cassava")
    assert any("fresh or dried mushrooms" in r["source"] for r in S if r["term"] == "shiitake mushrooms")


def test_synthetic_the_applied_state_gate_is_clean_and_every_row_is_in_the_lexicon_of_this_branch():
    C = json.loads((OUT / "applied_gate" / "applied_gate.json").read_text(encoding="utf-8"))
    assert C["verdict"] == "READY_FOR_REVIEW" and not C["blockers"] and C["drift"]["differences"] == {}
    assert len(C["after_build_proof"]) == 114 and all(v["recognised_after"] and not v["recognised_before"] for v in C["after_build_proof"].values())
    for k in ("frozen_66", "out_of_sample"):
        assert C[k]["unexplained"] == [] and C[k]["abstain_to_4"] == []
    ps = C["powder_surface"]
    assert ps["group1_after_forms_not_stated"] == [] and ps["newly_group4_or_other"] == {}
    assert C["drift"]["expected_owner_ruled"] == {"banana powder": [1, None], "strawberry powder": [1, None], "beetroot powder": [1, None]}
    assert all(C["synonyms_markers_untouched"].values()) and set(C["lexicon_rows"]["kind_changed"]) == {"cucumber", "tomato", "potato", "onion", "carrot", "cabbage"}
    assert {t for t, r in LEX.items() if r["kind"] == "vegetable"} == set(C["lexicon_rows"]["added"]) | set(C["lexicon_rows"]["kind_changed"]) | {"mushroom", "lettuce", "sweetcorn"} | {'winter squashes', 'buckwheat sprouts', 'bean sprouts', 'grain sprouts', 'sweet potato greens', 'microgreens', 'japanese bunching onions', 'sorrel', 'root vegetables', 'leafy vegetables', 'inflorescence vegetables', 'hot peppers', 'celery', 'green onions', 'spring onions', 'celery leaves', 'celery stalks'} | {'kelp', 'laver', 'wakame', 'spirulina', 'jicama', 'waterchestnuts', 'cloud ears', 'hearts of palm', 'fiddlehead ferns'}  # produce-gaps-24 and algae-24: algae named in the Group 1 definition; nalt-names-6/8/9/10/11: separately sourced plain-food heads; historical gate unchanged


@pytest.mark.parametrize("t", ["Salted Potatoes", "Potatoes (in brine)", "Carrots (sweetened)", "Salted Kale", "Carrots (Carrots, Salt)", "Tomato (with sugar)"])
def test_synthetic_negative_a_vegetable_item_whose_own_name_or_bracket_adds_salt_sugar_or_brine_never_takes_group_1(t):
    group, a = g(t)
    assert group == 3 and not any(d.detail == "single recognised unprocessed food" for d in a.drivers), (t, group)


@pytest.mark.parametrize("t", ["Cucumber (pickled)", "Onions (pickled)", "Tomatoes (canned)", "Spinach (tinned)", "Cabbage (preserved)", "Rice, Tomatoes (canned)"])
def test_synthetic_negative_canned_bottled_or_pickled_vegetable_without_salt_sugar_or_brine_abstains(t):
    group, a = g(t)
    assert group is None and "canned, bottled or preserved" in (a.reason or ""), t


@pytest.mark.parametrize("t", ["Spinach", "Kale", "Potato", "Unsalted Carrots", "Carrots (no added salt)", "Carrots (salt free)", "Carrots (frozen)", "Boiled Potatoes", "Spinach (cooked)", "Shiitake Mushrooms", "Sweet Potatoes"])
def test_synthetic_plain_negated_frozen_and_cooked_forms_keep_group_1(t):
    assert g(t)[0] == 1, t                                                       # roasting/boiling/cooking are NOT part of the guard (FAO Group 1 definition names them)


@pytest.mark.parametrize("t", ["Canned Tomatoes", "Tomato Sauce", "Potato Chips", "French Fries", "Mashed Potatoes", "Sauerkraut", "Kimchi", "Vegetable Juice", "Mushrooms in Brine"])
def test_synthetic_negative_forms_outside_the_vocabulary_never_get_group_1(t):
    group, a = g(t)
    assert group is None and t.lower() in " ".join(u.lower() for u in a.unassessed), t


def test_synthetic_plain_vegetable_inside_a_salted_list_keeps_its_item_placement():
    group, a = g("Rice, Salt, Carrots")
    assert group == 3 and any(d.ingredient == "Carrots" and d.detail == "recognised whole food" for d in a.drivers)
    assert g("Rice, Carrots")[0] is None
