"""fats-rows-1 (SYNTHETIC): twenty `culinary` rows (19 oils and lard) staged from the senior-reviewed FDC 'Fats and Oils' accepts (evaluation/junior_reviews_4/07_fats_oils_review.md).
Placement: FAO Group 2 'Vegetable oils crushed from seeds, nuts or fruit' (class-instance; wheat germ, oat and corn oil under the general Group 2 definition) and 'butter and lard' (lard: exact-named).
Not rows: nutmeg butter, ucuhuba butter (no positive evidence of culinary identity), industrial/brand records, synonyms (shea butter, rapeseed, maize), animal fats other than lard, fish oils."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from foodscan.pipeline import analyse_text

ROWS = ["almond oil", "apricot kernel oil", "avocado oil", "babassu oil", "canola oil", "corn oil", "cupuassu oil", "flaxseed oil", "grapeseed oil", "hazelnut oil", "lard", "oat oil", "palm kernel oil",
        "poppyseed oil", "safflower oil", "sheanut oil", "teaseed oil", "tomatoseed oil", "walnut oil", "wheat germ oil"]


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return (a.group if a.answered else None), a


@pytest.mark.parametrize("t", ROWS)
def test_synthetic_plain_oil_is_group_2_with_the_single_culinary_driver(t):
    group, a = g(t)
    assert group == 2 and a.drivers[0].detail == "single processed culinary ingredient", t


@pytest.mark.parametrize("t", ROWS)
def test_synthetic_hydrogenated_and_interesterified_forms_stay_group_4(t):
    for f in ("Hydrogenated {x}", "Partially Hydrogenated {x}", "Interesterified {x}", "{x} (hydrogenated)"):
        assert g(f.format(x=t))[0] == 4, f.format(x=t)


@pytest.mark.parametrize("t", ROWS)
def test_synthetic_sprays_blends_antioxidant_and_additive_brackets_abstain(t):
    for f in ("{x} spray", "{x} blend", "{x} (antioxidant)", "{x} (INS 319)", "oil, {x}", "cooking {x}"):
        assert g(f.format(x=t))[0] is None, f.format(x=t)


@pytest.mark.parametrize("t", ["Nutmeg Butter", "Ucuhuba Butter", "Rapeseed Oil", "Industrial Canola Oil", "Natreon Canola Oil", "Beef Tallow", "Fish Oil", "Pork Fat", "Animal Fat", "Shortening", "Margarine"])
# Maize Oil now has separate current NALT Product28879 naming evidence in nalt_names_7.
# Every other held fat/synonym remains negative.
def test_synthetic_held_synonym_and_other_fat_terms_stay_unrecognised(t):
    assert g(t)[0] is None, t


def test_synthetic_food_plus_oil_lists_and_nut_oil_brackets_follow_the_existing_rules():
    assert g("Rice, Almond Oil")[0] == 3 and g("Milk, Lard")[0] == 3 and g("Walnuts, Walnut Oil")[0] == 3
    assert g("Walnuts (walnut oil)")[0] == 3 and g("Cashew Nuts (walnut oil)")[0] == 3
    assert g("Lard, Salt")[0] is None and g("Corn Oil, Canola Oil")[0] is None


def test_synthetic_existing_culinary_rows_are_unchanged():
    for t in ("Olive Oil", "Sunflower Oil", "Palm Oil", "Ghee", "Butter", "Cocoa Butter", "Edible Vegetable Oil"):
        assert g(t)[0] == 2, t
    assert g("Hydrogenated Vegetable Oil")[0] == 4
    # UPDATED (culinary-guard-1, merged): an unrecognised bracket on an oil or fat row now abstains (it answered Group 2 when this batch was first staged), for the 20 existing (is_fat_row on main bbc54e3) and the 20 new rows alike
    assert g("Sunflower Oil (XQ9)")[0] is None and g("Corn Oil (XQ9)")[0] is None and g("Corn Oil Powder")[0] is None


def test_synthetic_row_provenance_has_clause_inference_and_no_purity_claim():
    root = Path(__file__).resolve().parent.parent
    rows = {r["term"]: r["source"] for r in csv.DictReader((root / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}
    for t in ROWS:
        s = rows[t]
        assert s.startswith("PROVISIONAL (fats-rows-1)") and "FDC id" in s and "NAMED" not in s and "pure" not in s.replace("purity", "") and "no purity or ingredient-list claim" in s, t
    assert "exact-named" in rows["lard"] and "butter and lard obtained from milk and pork" in rows["lard"]
    for t in ("wheat germ oil", "oat oil", "corn oil"):
        assert "general definition" in rows[t] and "class-instance of the definition" in rows[t], t
    assert "notably olives" in rows["almond oil"] and "class-instance of vegetable oils" in rows["almond oil"]
    assert "nutmeg butter" not in rows and "ucuhuba butter" not in rows
