"""animal-fish-rows-1 (SYNTHETIC): 68 fish and seafood rows as source-stated food labels, class-instance of the FAO Group 1 example 'meat, poultry, fish and seafood, whole or in the form of steaks, fillets and other cuts' (never NAMED, no
aliases, no taxonomy). They sit on the animal guard of animal-guard-1: dried -> Group 3, any powder abstains, salted/smoked/cured/canned/breaded/battered/fried/minced/formed forms abstain. Labels follow the source spelling (queen crab,
spot, pumpkin seed sunfish); generic names (salmon, tuna, fish, shrimp, crab, lobster) and aliases (snow crab, spot croaker, pumpkinseed sunfish) stay unrecognised."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
LEX = {r["term"]: r["source"] for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}
MEAT = {"beef", "lamb", "pork", "chicken", "veal", "turkey", "duck", "goose"}
ROWS = sorted(t for t, s in LEX.items() if s.startswith("PROVISIONAL (animal-guard-1)") and t not in MEAT)


def g(t):
    a = analyse_text(f"Ingredients: {t}.", source="text")
    return (a.group if a.answered else None), a


def test_synthetic_sixty_eight_fish_rows_and_the_eight_meat_rows_are_present():
    assert len(ROWS) == 68 and "queen crab" in ROWS and "snow crab" not in ROWS and "spot" in ROWS and "spot croaker" not in ROWS and "pumpkin seed sunfish" in ROWS and "pumpkinseed sunfish" not in ROWS
    assert all(t in LEX for t in ("beef", "lamb", "pork", "chicken", "veal", "turkey", "duck", "goose"))


@pytest.mark.parametrize("t", ROWS)
def test_synthetic_plain_and_minimal_process_forms_are_group_1_and_dried_is_group_3(t):
    assert g(t)[0] == 1 and g(f"ground {t}")[0] == 1 and g(f"roasted {t}")[0] == 1 and g(f"boiled {t}")[0] == 1 and g(f"steamed {t}")[0] == 1, t
    group, a = g(f"dried {t}")
    assert group == 3 and "salted, dried, cured, or smoked meats and fish" in a.drivers[0].detail, t


@pytest.mark.parametrize("t", ROWS)
def test_synthetic_powders_and_conditioned_forms_abstain(t):
    for f in ("{x} powder", "100% {x} powder", "whole {x} powder", "salted {x}", "smoked {x}", "cured {x}", "canned {x}", "breaded {x}", "battered {x}", "fried {x}", "minced {x}", "formed {x}", "cooked {x}", "chilled {x}",
              "{x} (XQ9)", "{x} (rice)", "{x} (milk)", "{x} (brine)", "{x} (sunflower oil)", "{x}, water"):
        assert g(f.format(x=t))[0] is None, f.format(x=t)
    assert g(f"{t}, salt")[0] == 3 and g(f"hydrogenated {t}")[0] == 4


@pytest.mark.parametrize("t", ["Salmon", "Tuna", "Fish", "Shrimp", "Prawn", "Crab", "Lobster", "Snow Crab", "Spot Croaker", "Pumpkinseed Sunfish", "Catfish", "Cod", "Pollock", "Halibut", "Tilapia"])
def test_synthetic_generic_names_and_aliases_stay_unrecognised(t):
    assert g(t)[0] is None, t


def test_synthetic_row_provenance_is_class_instance_with_the_verified_example_only():
    for t in ROWS:
        s = LEX[t]
        assert '"meat, poultry, fish and seafood, whole or in the form of steaks, fillets and other cuts"' in s and "never NAMED" in s and "no taxonomic resolution" in s and "no alias" in s and "FDC id" in s and "Unprocessed (or natural)" not in s, t
