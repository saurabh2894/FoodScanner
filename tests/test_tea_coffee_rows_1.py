"""tea-coffee-rows-1 (SYNTHETIC): two whole_food rows, `tea` and `coffee` (FAO Table 1 Group 1 example "tea, coffee, and drinking water", exact-named ingredient terms; no purity claim).
Held and unrecognised: instant, decaf, extract, leaves/beans, black/oolong tea, espresso, herbal infusions, ready-to-drink, aliases, coffee substitutes. Forms that need the separate whole-food-guard-1 proposal to abstain are
marked xfail (non-strict): without that guard a recognised whole_food row answers Group 1 for 'Tea (sugar)', 'Tea (milk)', 'Salted Tea' and similar (a widened hole, reported in the evaluation README)."""
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


@pytest.mark.parametrize("t", ["Instant Coffee", "Decaffeinated Tea", "Decaf Coffee", "Instant Tea", "Tea Extract", "Coffee Extract", "Tea Leaves", "Coffee Beans", "Black Tea", "Oolong Tea", "Espresso", "Hibiscus Tea", "Chamomile Tea",
                               "Herbal Tea", "Coffee Substitute", "Chicory", "Ready To Drink Tea", "Iced Tea", "Bottled Water", "Drinking Water"])
def test_synthetic_held_forms_aliases_and_other_beverages_stay_unrecognised(t):
    assert g(t)[0] is None, t


@pytest.mark.xfail(strict=False, reason="widened hole until whole-food-guard-1 merges: a recognised whole_food row answers Group 1 for an added condition or a distinct food in its own bracket")
@pytest.mark.parametrize("t", ["Tea (sugar)", "Tea (milk)", "Coffee (milk)", "Tea (egg)", "Tea (rice)", "Salted Tea", "Tea (salted)", "Tea (canned)", "Tea (brine)", "Tea (sunflower oil)", "Coffee (sugar)"])
def test_synthetic_conditioned_and_nested_forms_abstain_once_the_whole_food_guard_is_in(t):
    assert g(t)[0] is None, t


def test_synthetic_green_tea_resolves_through_the_global_descriptor_green():
    # reported, not designed: 'green' is a global descriptor, so 'Green Tea' resolves to the row `tea`; 'Black Tea' does not (aliases stay held)
    assert g("Green Tea")[0] == 1 and g("Black Tea")[0] is None


def test_synthetic_row_provenance_has_the_verified_clause_and_no_spliced_definition_or_purity_claim():
    root = Path(__file__).resolve().parent.parent
    rows = {r["term"]: r["source"] for r in csv.DictReader((root / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}
    for t in ROWS:
        s = rows[t]
        assert s.startswith("PROVISIONAL (tea-coffee-rows-1)") and 'example "tea, coffee, and drinking water"' in s and "exact-named" in s and "FDC id" in s, t
        assert "nothing is claimed about purity" in s and "Unprocessed (or natural)" not in s and "algae and water" not in s and "pure" not in s.replace("purity", ""), t
        assert "instant or decaffeinated" in s and "never placement" in s
    assert rows["water"] and "neutral" in {r["kind"] for r in csv.DictReader((root / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline="")) if r["term"] == "water"}
