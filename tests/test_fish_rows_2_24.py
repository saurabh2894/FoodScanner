"""fish-rows-2-24 (SYNTHETIC): 38 low-processed-form-dominance fish and shellfish genus rows stacked on animal-guard-1
(same reviewed pattern as animal-fish-rows-1: class-instance of the FAO Group 1 'meat, poultry, fish and seafood' example,
FDC CC0 naming support only, never placement). Held out: canned/smoked-dominant generics (tuna, salmon, sardine, herring,
mackerel, anchovy, cod, pollock, halibut, shrimp, crab, lobster, bass) stay unrecognised - bare label words would misread
dominant processed forms as raw; conch and sardine have no raw FDC record; roe stays on review; snail is terrestrial
(outside the 'fish and seafood' example scope). Guard probes: compounds, smoked/canned/fried forms and powders abstain;
dried finfish -> Group 3; dried shellfish abstains (scope none)."""
from __future__ import annotations

import csv
from pathlib import Path

from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
STAGED = [r["term"] for r in csv.DictReader((ROOT / "evaluation" / "fish_rows_2_24" / "staged_rows.csv").open(newline=""))]


def g(t):
    a = analyse_text(f"Ingredients: {t}.", source="text")
    return (a.group if a.answered else None), a


def test_synthetic_thirty_eight_rows_staged():
    assert len(STAGED) == 38 and "squid" in STAGED and "octopus" in STAGED and "spiny lobster" in STAGED


def test_synthetic_all_rows_are_group_1():
    for t in STAGED:
        assert g(t)[0] == 1, t
        assert g(f"{t.title()} (5%)")[0] == 1, t


def test_synthetic_processed_form_words_abstain():
    for t in ["Smoked Trout", "Canned Clam", "Fried Squid", "Breaded Oyster", "Oyster Sauce", "Squid Ink", "Clam Chowder", "Squid Powder"]:
        assert g(t)[0] is None, t


def test_synthetic_dried_scope_rules():
    assert g("Dried Carp")[0] == 3
    assert g("Dried Squid")[0] is None


def test_synthetic_held_generics_stay_unrecognised():
    for t in ["Tuna", "Salmon", "Shrimp", "Herring", "Sardine", "Mackerel", "Anchovy", "Prawns", "Catfish", "Tilapia", "Cod Liver Oil"]:
        assert g(t)[0] is None, t
