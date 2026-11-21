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


@pytest.mark.parametrize("t", ["Toasted Almonds", "Toasted Soybeans", "Toasted Lychee", "Toasted Carrot", "Toasted Salted Oat Flour", "Toasted Oat Flour, Salt", "Toasted Oat Flour, Sugar", "Rice, Toasted Oat Flour"])
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
