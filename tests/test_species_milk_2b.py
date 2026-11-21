"""per-form-2b (SYNTHETIC): species-head milk recognition. 'cow milk' and 'goat milk' are lexicon rows (kind whole_food, provenance in the row source: FAO Group 1 milk without species restriction; Lancet 2025 names
minimally processed cow's milk); 'buffalo milk' was already a row. The species words alone stay unrecognised; the species-bracket rule stays scoped to plain milk heads; milk solids stay excluded."""
from __future__ import annotations

import pytest

from foodscan.classify import is_recognised, lookup
from foodscan.normalise import normalise_ingredient
from foodscan.pipeline import analyse_text


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return (a.group if a.answered else None), a


@pytest.mark.parametrize("t", ["Cow Milk", "Goat Milk", "Goat Milk (Pasteurized)", "Pasteurised Cow Milk", "Toned Cow Milk", "Milk (Cow Milk)", "Milk (Goat Milk)", "Buffalo Milk"])
def test_synthetic_species_qualified_milk_head_names_are_group_1(t):
    assert g(t)[0] == 1, t


def test_synthetic_cow_milk_has_drivers_identical_to_milk():
    _, a = g("Cow Milk"); _, b = g("Milk")
    assert [d.detail for d in a.drivers] == [d.detail for d in b.drivers] and lookup("cow milk")["kind"] == "whole_food"


def test_synthetic_the_row_provenance_quotes_the_sources_and_states_the_inference_level():
    import csv
    from pathlib import Path
    rows = {r["term"]: r["source"] for r in csv.DictReader((Path(__file__).resolve().parent.parent / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}
    for t in ("cow milk", "goat milk"):
        assert rows[t].startswith("PROVISIONAL") and "or of or from animals (muscle, fat, offal, eggs, milk)" in rows[t] and "fresh, powdered or pasteurized milk" in rows[t] and "Inference level" in rows[t]
    assert "minimally processed cow" in rows["cow milk"] and "class-instance" in rows["goat milk"]


@pytest.mark.parametrize("t", ["Cow Milk Powder", "Skimmed Cow Milk Powder", "Goat Milk Powder", "Whole Cow Milk Powder"])
def test_synthetic_species_milk_powder_follows_the_milk_powder_outcome(t):
    group, a = g(t)
    assert group == 1 and "fresh, powdered or pasteurized milk" in a.drivers[0].detail, t


@pytest.mark.parametrize("t", ["Fortified Cow Milk Powder", "Cow Milk Solids Powder", "Cow Milk Powder (Vitamins Added)"])
def test_synthetic_negative_modified_species_milk_powders_still_abstain(t):
    assert g(t)[0] is None, t


@pytest.mark.parametrize("t", ["Cow", "Goat", "Sheep Milk", "Human Milk", "Cow Cheese", "Cow Milk Solids", "Cow's Milk"])
def test_synthetic_negative_the_species_words_alone_and_other_forms_stay_unrecognised(t):
    group, a = g(t)
    assert group is None and t.lower() in " ".join(u.lower() for u in a.unassessed), t
    assert not is_recognised("cow") and not is_recognised("goat")


@pytest.mark.parametrize("t", ["Milk Solids (Pasteurized Skimmed Cow Milk)", "Milk Solids (Cow Milk)", "Rice (Cow Milk)", "Rice (Buffalo Milk)", "Rice (Goat Milk)", "Milk (Cow)", "Egg (Cow Milk)"])
def test_synthetic_negative_milk_solids_exclusion_and_the_head_scoped_species_bracket_rule_stand(t):
    assert g(t)[0] is None, t


def test_synthetic_cow_milk_with_a_culture_follows_the_milk_plus_culture_rule_and_salted_is_the_milk_behaviour():
    assert g("Cow Milk, Starter Culture")[0] == 1
    assert g("Salted Cow Milk")[0] == g("Salted Milk")[0]                                  # outside the 23-term salted-grain scope: identical to 'Salted Milk' (measured, parked)
