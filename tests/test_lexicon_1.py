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
    "almonds": "whole_food",
    "pumpkin seeds": "whole_food",
    "flax seeds": "whole_food",
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
    # Package E (plain juices)
    "apple juice": "whole_food",
    "grape juice": "whole_food",
    "orange juice": "whole_food",
    "pineapple juice": "whole_food",
}


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
    for starch in ["tapioca starch", "starch", "corn starch", "potato starch"]:
        assert starch not in rows, f"starch {starch} should not be in lexicon.csv"

    # Milk and derivative terms held for decision
    for milk in ["whey", "whey powder", "vitamins & minerals", "vitamins and minerals"]:
        assert milk not in rows, f"milk/mineral term {milk} should not be in lexicon.csv"

    # OCR / label typos
    for typo in ["tumeric", "com meal", "refined palmolien oil", "maltodectrin"]:
        assert typo not in rows, f"typo {typo} should not be in lexicon.csv"

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
    for item in processed_forms:
        assert item not in rows, f"{item} should not have a lexicon row"
        r = analyse_text(f"Ingredients: {item}.", source="text")
        assert item in r.unassessed, f"{item} should stay unassessed"


def test_normalise_ingredient_maps_new_terms_to_kind():
    # Test that normalise_ingredient together with lookup maps new terms to their kind
    for term, expected_kind in [("Almonds", "whole_food"), ("Ajwain", "herb_spice"), ("Black Raisin", "whole_food")]:
        norm = normalise_ingredient(term)
        assert norm.name == term.lower()
        info = lookup(norm.name)
        assert info is not None
        assert info["kind"] == expected_kind
