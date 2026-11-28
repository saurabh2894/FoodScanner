"""tea-coffee-rows-1 (SYNTHETIC): two whole_food rows, `tea` and `coffee` (FAO Table 1 Group 1 example "tea, coffee, and drinking water", exact-named ingredient terms; no purity claim).
Held and unrecognised: instant, decaf, extract, leaves/beans, black/oolong tea, espresso, herbal infusions, ready-to-drink, aliases, coffee substitutes. Conditioned and nested forms ('Tea (sugar)', 'Tea (milk)', 'Salted Tea', 'Tea (egg)')
abstain through the whole-food guard (merged in main 342e662); before it, a recognised whole_food row answered Group 1 for them (a widened hole measured and reported in the evaluation README)."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from foodscan.pipeline import analyse_text

ROWS = ["tea", "coffee"]


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return (a.group if a.answered else None), a


@pytest.mark.parametrize("t", ["Tea", "Coffee", "Roasted Coffee", "Unsalted Tea", "Tea (no added salt)", "100% Coffee Powder"])
def test_synthetic_plain_tea_and_coffee_are_group_1(t):
    assert g(t)[0] == 1, t


@pytest.mark.parametrize("t", ROWS)
def test_synthetic_sugar_salt_and_flavour_lists_follow_the_existing_rules(t):
    assert g(f"{t}, Sugar")[0] == 3 and g(f"Sugar, {t}")[0] == 3 and g(f"{t}, Salt")[0] == 3
    assert g(f"{t}, Flavour")[0] == 4 and g(f"{t}, Natural Flavour")[0] == 4 and g(f"{t}, Maltodextrin")[0] == 4 and g(f"{t}, Colour (INS 150d)")[0] == 4


@pytest.mark.parametrize("t", ["Coffee, Milk", "Coffee (Chicory)", "Tea (XQ9)", "Tea (Arabica)", "Coffee (Camellia Sinensis)", "Tea Powder", "Coffee Powder", "Tea, Coffee", "Water, Tea", "Rice, Tea"])
def test_synthetic_milk_unknown_brackets_and_bare_powders_abstain(t):
    assert g(t)[0] is None, t


@pytest.mark.parametrize("t", ["Instant Coffee", "Decaffeinated Tea", "Decaf Coffee", "Instant Tea", "Tea Extract", "Coffee Extract", "Tea Leaves", "Coffee Beans", "Espresso", "Hibiscus Tea", "Chamomile Tea",
                               "Coffee Substitute", "Chicory", "Ready To Drink Tea", "Iced Tea", "Bottled Water", "Drinking Water"])
def test_synthetic_held_forms_aliases_and_other_beverages_stay_unrecognised(t):
    assert g(t)[0] is None, t


@pytest.mark.parametrize("t", ["Tea (sugar)", "Tea (milk)", "Coffee (milk)", "Tea (egg)", "Tea (rice)", "Salted Tea", "Tea (salted)", "Tea (canned)", "Tea (brine)", "Tea (sunflower oil)", "Coffee (sugar)"])
def test_synthetic_conditioned_and_nested_forms_abstain_through_the_whole_food_guard(t):
    assert g(t)[0] is None, t


def test_synthetic_green_tea_resolves_through_the_global_descriptor_green():
    # reported, not designed: 'green' is a global descriptor, so 'Green Tea' resolves to the row `tea`; 'Black Tea' does not (aliases stay held)
    # tea-24: black tea and oolong tea are now aliases of tea (FSSAI 2.10.1(1)); see tests/test_tea_24.py
    assert g("Green Tea")[0] == 1 and g("Black Tea")[0] == 1


def test_synthetic_row_provenance_has_the_verified_clause_and_no_spliced_definition_or_purity_claim():
    root = Path(__file__).resolve().parent.parent
    rows = {r["term"]: r["source"] for r in csv.DictReader((root / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}
    for t in ROWS:
        s = rows[t]
        assert s.startswith("PROVISIONAL (tea-coffee-rows-1)") and 'example "tea, coffee, and drinking water"' in s and "exact-named" in s and "FDC id" in s, t
        assert "nothing is claimed about purity" in s and "Unprocessed (or natural)" not in s and "algae and water" not in s and "pure" not in s.replace("purity", ""), t
        assert "instant or decaffeinated" in s and "never placement" in s
    assert rows["water"] and "neutral" in {r["kind"] for r in csv.DictReader((root / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline="")) if r["term"] == "water"}
