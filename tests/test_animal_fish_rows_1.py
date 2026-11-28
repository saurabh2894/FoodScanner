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
    # 68 rows of animal-fish-rows-1 plus 38 genus rows of fish-rows-2-24
    assert len(ROWS) == 106 and "queen crab" in ROWS and "snow crab" not in ROWS and "spot" in ROWS and "spot croaker" not in ROWS and "pumpkin seed sunfish" in ROWS and "pumpkinseed sunfish" not in ROWS and "squid" in ROWS and "tilapia" not in ROWS
    assert all(t in LEX for t in ("beef", "lamb", "pork", "chicken", "veal", "turkey", "duck", "goose"))


NOT_FISH = {"alaska king crab", "blue crab", "blue swimming crab", "dungeness crab", "queen crab", "northern lobster", "blue mussel", "eastern oyster", "pacific oyster", "common octopus", "patagonian bay scallop", "sea scallop"}
# fish-rows-2-24 (2026-11-24): 38 genus rows stacked on the same guard; the eleven shellfish extend the dried-scope-none set
NOT_FISH_2 = {"abalone", "clam", "crayfish", "cuttlefish", "mussel", "octopus", "oyster", "scallop", "spiny lobster", "squid", "whelk"}
NOT_FISH = NOT_FISH | NOT_FISH_2


@pytest.mark.parametrize("t", ROWS)
def test_synthetic_plain_and_minimal_process_forms_are_group_1(t):
    assert g(t)[0] == 1 and g(f"ground {t}")[0] == 1 and g(f"roasted {t}")[0] == 1 and g(f"boiled {t}")[0] == 1 and g(f"steamed {t}")[0] == 1, t


@pytest.mark.parametrize("t", [x for x in ROWS if x not in NOT_FISH])
def test_synthetic_dried_fish_is_group_3_with_the_fao_example(t):
    group, a = g(f"dried {t}")
    assert group == 3 and "salted, dried, cured, or smoked meats and fish" in a.drivers[0].detail and "DRIED-G3-SCOPE: finfish" in LEX[t], t


@pytest.mark.parametrize("t", sorted(NOT_FISH))
def test_synthetic_dried_crustaceans_and_molluscs_abstain_and_never_fall_back_to_group_1(t):
    # owner review of animal-guard-1: the FAO Group 3 example names dried 'meats and fish', not seafood; the Group 1 example grouping is not extended to it
    assert "DRIED-G3-SCOPE: none" in LEX[t] and t in ROWS
    for f in ("dried {x}", "dehydrated {x}", "dried {x}, salt", "dried {x} powder"):
        group, a = g(f.format(x=t))
        assert group is None, f.format(x=t)
    group, a = g(f"dried {t}")
    assert a.reason.startswith("a dried form of an animal food is named (") and "dried meats and fish only" in a.reason and "does not make it Group 1" in a.reason


def test_synthetic_the_scope_split_is_twelve_seafood_and_fifty_six_fish_rows():
    # animal-fish-rows-1 split 12 seafood / 56 fish; fish-rows-2-24 adds 11 seafood (scope none) and 27 finfish
    assert len(NOT_FISH) == 23 and len(ROWS) - len(NOT_FISH) == 83 and NOT_FISH <= set(ROWS)


@pytest.mark.parametrize("t", ROWS)
def test_synthetic_powders_and_conditioned_forms_abstain(t):
    # smoked-fish-24: "smoked haddock", "smoked sturgeon" and "smoked whitefish" are now explicit rows placed Group 3 (FAO Group 3 prose "smoked fish"; FDC SR Legacy identity), so the bare "smoked {x}" pin is skipped for them
    smoked_rows = {"haddock", "sturgeon", "whitefish"}
    for f in ("{x} powder", "100% {x} powder", "whole {x} powder", "salted {x}", "smoked {x}", "cured {x}", "canned {x}", "breaded {x}", "battered {x}", "fried {x}", "minced {x}", "formed {x}", "cooked {x}", "chilled {x}",
              "{x} (XQ9)", "{x} (rice)", "{x} (milk)", "{x} (brine)", "{x} (sunflower oil)", "{x}, water"):
        if f == "smoked {x}" and t in smoked_rows:
            assert g(f.format(x=t))[0] == 3, f.format(x=t)
            continue
        assert g(f.format(x=t))[0] is None, f.format(x=t)
    assert g(f"{t}, salt")[0] == 3 and g(f"hydrogenated {t}")[0] == 4


# shrimp-24 lifted the shrimp and prawn holds additively (tests/test_shrimp_24.py).
# generic-fish-24 re-examined and staged cod, halibut, pollock, crab, lobster (tests/test_generic_fish_24.py); the rest stay held.
@pytest.mark.parametrize("t", ["Salmon", "Tuna", "Fish", "Snow Crab", "Spot Croaker", "Pumpkinseed Sunfish"])  # fssai-fish-26b: Catfish and Tilapia left this hold list; FSSAI 2.6.2 names them (tests/test_fssai_fish_26b.py)
def test_synthetic_generic_names_and_aliases_stay_unrecognised(t):
    assert g(t)[0] is None, t


def test_synthetic_row_provenance_is_class_instance_with_the_verified_example_only():
    for t in ROWS:
        s = LEX[t]
        assert '"meat, poultry, fish and seafood, whole or in the form of steaks, fillets and other cuts"' in s and "never NAMED" in s and "no taxonomic resolution" in s and "no alias" in s and "FDC id" in s and "Unprocessed (or natural)" not in s, t
