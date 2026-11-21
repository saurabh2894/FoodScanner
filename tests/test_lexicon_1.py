"""Tests for Task 3: Lexicon 1 - Sourced ingredient vocabulary."""
from pathlib import Path
import pytest

from foodscan.tables import load_table
from foodscan.classify import lookup
from foodscan.normalise import normalise_ingredient
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent

ADDED_TERMS = {
    # Package A (nuts and seeds)
    "almonds": "nut_seed",     # provenance-fixes-1: conditioned nut/seed kind (item-level salt/sugar condition)
    "pumpkin seeds": "nut_seed",     # provenance-fixes-1: conditioned nut/seed kind (item-level salt/sugar condition)
    "flax seeds": "nut_seed",     # provenance-fixes-1: conditioned nut/seed kind (item-level salt/sugar condition)
    # Package B (herbs and spices)
    "ajwain": "herb_spice",
    "bishop's seed": "herb_spice",
    "aniseed": "herb_spice",
    "caraway": "herb_spice",
    "bay leaf": "herb_spice",
    "capsicum powder": "herb_spice",
    "fennel": "herb_spice",
    "fennel seeds": "herb_spice",
    "fenugreek": "herb_spice",
    "nutmeg": "herb_spice",
    "mace": "herb_spice",
    "mint": "herb_spice",
    "mustard": "herb_spice",
    "pepper": "herb_spice",
    "long pepper": "herb_spice",
    "white pepper": "herb_spice",
    "black pepper bits": "herb_spice",
    "red chili": "herb_spice",
    "chillies": "herb_spice",
    "chilli flakes": "herb_spice",
    "schezwan pepper": "herb_spice",
    "dried curry leaves": "herb_spice",
    # Package D (dried fruit)
    "black raisin": "whole_food",
}
# Package E (plain juices: apple, grape, orange, pineapple juice) is HELD, not added: see test_juice_rows_are_held below and evaluation/lexicon_1_flip_check/README.md.


def test_added_lexicon_rows_exist_with_kind_and_provisional_source():
    rows = {r["term"]: r for r in load_table("lexicon.csv")}
    for term, expected_kind in ADDED_TERMS.items():
        assert term in rows, f"missing lexicon row for {term}"
        row = rows[term]
        assert row["kind"] == expected_kind, f"wrong kind for {term}: {row['kind']} != {expected_kind}"
        assert row["source"].startswith("PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11"), f"invalid source for {term}: {row['source']}"
        assert "exact label term seen on" in row["source"], f"source for {term} missing evidence citation: {row['source']}"


def test_explicit_exclusions_and_blocked_items_did_not_get_rows():
    rows = {r["term"]: r for r in load_table("lexicon.csv")}

    # Pulps and purees
    for pulp in ["mango pulp", "papaya pulp", "pear pulp", "banana pulp", "tomato puree", "tomato paste", "raw mango pulp"]:
        assert pulp not in rows, f"pulp {pulp} should not be in lexicon.csv"

    # Juice concentrates
    for conc in ["apple juice concentrate", "lemon juice concentrate", "orange juice concentrate", "fruit juice concentrate"]:
        assert conc not in rows, f"concentrate {conc} should not be in lexicon.csv"

    # Starches
    # owner decision (2026-11-21, pmc-decisions-1): the hold is LIFTED for plain starch and tapioca starch ONLY (kind culinary, FAO Group 2 clause + PMC10127522 corroboration); the rest stay out
    for starch in ["corn starch", "potato starch", "modified starch", "maize starch"]:
        assert starch not in rows, f"starch {starch} should not be in lexicon.csv"
    for starch in ["tapioca starch", "starch"]:
        assert starch not in rows or (rows[starch]["kind"] == "culinary" and "PMC10127522" in rows[starch]["source"]), f"{starch} may only be the owner-lifted culinary row"

    # Milk and derivative terms held for decision
    for milk in ["whey", "whey powder"]:
        assert milk not in rows, f"milk/mineral term {milk} should not be in lexicon.csv"
    # owner decision (held-sources gate, 2026-11-21): the vitamins/minerals terms may exist ONLY as kind "unplaced" (recognised by name, never placed, any list holding one abstains)
    for vit in ["vitamins & minerals", "vitamins and minerals"]:
        assert vit not in rows or rows[vit]["kind"] == "unplaced", f"{vit} may only be an unplaced-kind row"

    # OCR / label typos
    for typo in ["tumeric", "com meal", "refined palmolien oil", "maltodectrin"]:
        assert typo not in rows, f"typo {typo} should not be in lexicon.csv"

    # Plain juices held (senior review): the bare term does not establish fresh/pasteurized versus reconstituted from concentrate
    for juice in ["apple juice", "grape juice", "orange juice", "pineapple juice"]:
        assert juice not in rows, f"{juice} is held (cranberry precedent), no row"

    # Condition-blocked candidate items
    assert "roasted peanuts" not in rows, "roasted peanuts on b1/N15 has added sugar/salt, must be blocked"
    assert "corn flakes" not in rows, "corn flakes on dev/F10 does not establish plain status, must be blocked"
    assert "cranberry" not in rows, "cranberry on b1/N14 does not establish plain dried status, must be blocked"


def test_condition_handling_processed_forms_stay_unassessed():
    # Processed/sweetened forms of added terms must get NO row and remain unassessed
    processed_forms = [
        "apple juice concentrate",
        "salted roasted peanuts",
        "orange juice concentrate",
        "grape juice concentrate",
        "pineapple juice concentrate",
    ]
    rows = {r["term"]: r for r in load_table("lexicon.csv")}
    approved_markers = {"apple juice concentrate"}      # marker-rows-1 (owner-approved, FAO section 3 'fruit juice concentrates', class-level): still NO lexicon row, but no longer unassessed
    for item in processed_forms:
        assert item not in rows, f"{item} should not have a lexicon row"
        r = analyse_text(f"Ingredients: {item}.", source="text")
        if item in approved_markers:
            assert r.answered and r.group == 4 and item not in r.unassessed, f"{item} is an approved strong marker"
        else:
            assert item in r.unassessed, f"{item} should stay unassessed"


def test_normalise_ingredient_maps_new_terms_to_kind():
    # Test that normalise_ingredient together with lookup maps new terms to their kind
    for term, expected_kind in [("Almonds", "nut_seed"), ("Ajwain", "herb_spice"), ("Black Raisin", "whole_food")]:
        norm = normalise_ingredient(term)
        assert norm.name == term.lower()
        info = lookup(norm.name)
        assert info is not None
        assert info["kind"] == expected_kind


def test_juice_rows_are_held():
    """FAO 2019 Table 1 Group 1 lists 'fresh or pasteurized fruit or vegetable juices (with no added sugar, sweeteners or flavours)'; pp. 9-10 list 'fruit juice concentrate'
    among the substances of ultra-processed foods. A bare 'apple juice' does not say which, and the unknown crosses the Group 1 / Group 4 boundary, so the four juice rows
    are held (same discipline as cranberry). They stay unassessed; nothing else changes."""
    for juice in ["apple juice", "grape juice", "orange juice", "pineapple juice"]:
        r = analyse_text(f"Ingredients: {juice}.", source="text")
        assert not r.answered and juice in r.unassessed, juice
