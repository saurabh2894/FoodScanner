"""per-form-1 (SYNTHETIC; owner evidence rulings). (1) roasted/toasted plain grains and flours: Group 1, basis FAO 2019 p.6 methods clause ('roasting' exact-named; 'toasted' is an inference). (2) The unknown-bracket abstention
now covers whole_food items ('Rice (XQ9)' Group 1 -> abstain). The parked forms stay unresolved."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from foodscan.classify import _scoped_descriptors, lookup
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return (a.group if a.answered else None), a


def test_synthetic_the_toasted_descriptor_is_kind_scoped_and_cites_the_fao_methods_clause_verbatim():
    assert _scoped_descriptors() == {"toasted": frozenset({"whole_food", "flour"})}
    row = next(r for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "descriptors.csv").open(encoding="utf-8-sig", newline="")) if r["word"] == "toasted")
    assert "drying, crushing, grinding, powdering, fractioning, filtering, roasting, boiling, non-alcoholic fermentation, pasteurization, chilling, freezing, placing in containers, and vacuum packaging" in row["source"]
    assert "INFERENCE" in row["source"] and row["kinds"] == "whole_food;flour"
    fao = " ".join((ROOT / "evaluation" / "per_form_1" / "fao_p6_quote.txt").read_text(encoding="utf-8").split())
    assert fao in row["source"]


@pytest.mark.parametrize("t", ["Roasted Buckwheat", "Roasted Oat Flour", "Toasted Oat Flour", "Toasted Buckwheat", "Toasted Rice", "Toasted Unsalted Oat Flour"])
def test_synthetic_plain_roasted_and_toasted_grains_and_flours_are_group_1(t):
    assert g(t)[0] == 1, t


@pytest.mark.parametrize("t", ["Toasted Almonds", "Toasted Soybeans", "Toasted Lychee", "Toasted Carrot", "Toasted Milk", "Toasted Egg", "Toasted Oats", "Toasted Rolled Oats", "Toasted Wheat", "Toasted Salted Oat Flour", "Toasted Sweetened Oat Flour",
                               "Toasted Honey Oat Flour", "Toasted Flavoured Oat Flour", "Toasted Spiced Oat Flour", "Toasted Oat Flour, Salt", "Toasted Oat Flour, Sugar", "Rice, Toasted Oat Flour"])
def test_synthetic_negative_toasted_is_scoped_to_grains_and_flours_and_never_overrides_a_guard_or_a_list_rule(t):
    assert g(t)[0] is None, t
    assert lookup("toasted almonds") is None and lookup("toasted lychee") is None and lookup("toasted oat flour")["kind"] == "flour"


@pytest.mark.parametrize("t", ["Rice (XQ9)", "Wheat (XQ9)", "Milk (XQ9)", "Egg (XQ9)", "Roasted Buckwheat (XQ9)", "Toasted Oat Flour (XQ9)", "Oat Flour (XQ9)"])
def test_synthetic_negative_an_unknown_bracket_on_a_whole_food_or_flour_item_abstains(t):
    group, a = g(t)
    assert group is None and "names content the vocabulary does not recognise" in (a.reason or ""), t


@pytest.mark.parametrize("t", ["Rice (Basmati)", "Rice (Parboiled)", "Milk (Skimmed)", "Rice", "Wheat Flour (Organic)", "Whole Wheat Flour (Atta)"])
def test_synthetic_recognised_and_descriptor_brackets_keep_group_1(t):
    assert g(t)[0] == 1, t


@pytest.mark.parametrize("t", ["Enriched Wheat Flour", "Fortified Wheat Flour", "Enriched Flour", "Fortified Rice", "Sprouted Ragi", "Sprouted Jowar", "Pearled Barley", "Vitamins and Minerals", "Rice, Vitamins and Minerals"])
def test_synthetic_parked_forms_stay_unresolved_and_abstain(t):
    group, a = g(t)
    assert group is None, t
    assert not any(d.detail.startswith("single recognised") for d in a.drivers)


def test_synthetic_the_powder_standard_is_unchanged():
    assert g("Mango Powder")[0] is None and g("100% Mango Powder")[0] == 1 and g("Milk Powder")[0] == 1 and g("Milk Solids Powder")[0] is None


# SPECIES-OF-ORIGIN PROVENANCE (owner decision, round 2): cow/buffalo/goat is benign ONLY in a bracket that holds 'milk' AND only when the head item is itself a milk item (whole_food, term in milk/toned milk/double toned
# milk/buffalo milk/milk solids). Resolved in the bracket check: no lexicon row, no synonym, no globally recognised word.
@pytest.mark.parametrize("t", ["Milk (Pasteurized Cow Milk)", "Milk (Buffalo Milk)", "Milk (Goat Milk)", "Toned Milk (Cow Milk)"])
def test_synthetic_species_of_origin_in_a_milk_bracket_on_a_milk_item_is_benign_provenance(t):
    assert g(t)[0] == 1, t


@pytest.mark.parametrize("t", ["Milk (Cow)", "Rice (Cow)", "Rice (Cow Milk)", "Egg (Cow Milk)", "Milk (Cow Cheese)", "Milk (Cow Milk, XQ9)", "Goat Milk (Pasteurized)", "Cow Milk", "Milk solids (Pasteurized skimmed cow milk)", "Milk Solids (Cow Milk)"])
def test_synthetic_negative_a_species_word_anywhere_else_stays_unrecognised_and_the_abstention_stands(t):
    group, a = g(t)
    assert group is None, t


def test_synthetic_the_species_word_is_not_a_recognised_word_and_the_frozen_q10_label_stays_abstained_on_its_own_evidence():
    from foodscan.classify import is_recognised
    assert not is_recognised("cow milk") and not is_recognised("goat milk") and not is_recognised("cow")
    a = analyse_text((ROOT / "evaluation" / "fresh_batch_3" / "inputs" / "Q10.txt").read_text(encoding="utf-8"), source="text")
    # b3/Q10 'Milk solids (Pasteurized skimmed cow milk)': 'milk solids' is not established as identical to milk (owner ruling) and no quoted source places this exact form (FAO names 'fresh, powdered or pasteurized
    # milk', not milk solids), so it stays abstained, attributed to the unknown-bracket rule. Group 1 for it would be an unjustified placement.
    assert not a.answered and "names content the vocabulary does not recognise" in (a.reason or "")
    assert analyse_text("Ingredients: Milk solids.", source="text").group == 1                    # the bare existing row is untouched


def test_synthetic_the_toasted_term_set_is_exactly_the_23_terms_batch_4_placed():
    import csv as _csv
    from foodscan.classify import _SCOPED_TERMS
    staged = {r["term"] for r in _csv.DictReader((ROOT / "evaluation" / "class_bulk_4" / "grains" / "staged_rows.csv").open(encoding="utf-8", newline=""))}
    assert _SCOPED_TERMS["toasted"] == frozenset(staged) and len(staged) == 23
    from foodscan.classify import lookup as _lookup
    kinds = {t: _lookup(t)["kind"] for t in staged}                  # 'red rice' and 'parboiled rice' resolve to the row 'rice' through the global descriptors
    assert sum(1 for t in staged if kinds[t] == "whole_food") == 9 and sum(1 for t in staged if kinds[t] == "flour") == 14


def test_synthetic_roasted_is_unchanged_by_this_branch():
    assert g("Roasted Milk")[0] == 1 and g("Roasted Buckwheat")[0] == 1                  # the pre-existing broad global descriptor: not widened, not narrowed
