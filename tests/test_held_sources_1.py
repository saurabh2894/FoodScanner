"""held-sources-1 as merged: fruit/vegetable powders recognised as single powdered natural foods; vitamins/minerals and sprouted forms stay UNPLACED and the list abstains.
SYNTHETIC cases plus the owner's own acceptance label text (a real photographed label, transcribed and verified by the owner; not Open Food Facts)."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from foodscan.classify import is_recognised
from foodscan.normalise import normalise_ingredient
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
DEC = json.loads((ROOT / "data" / "ingest" / "held_decisions_1.json").read_text(encoding="utf-8"))["decisions"]
LEX = {r["term"]: r for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}
LABEL = ("Ingredients: Multigrain Flour Blend (45.7%) [Sprouted Ragi & Jowar (23.4%), Rice & Oat (22.3%)], Whole Milk Powder (29.5%), Date Powder (9%), Banana Powder, Strawberry Powder (5%), "
         "Skimmed Milk Powder, Vitamins and Minerals, Beetroot Powder, Antioxidant (Natural Tocopherol).")


def rec(t: str) -> bool:
    return bool(is_recognised(normalise_ingredient(t).name))


def grp(text: str):
    a = analyse_text(text, source="text")
    return (a.group if a.answered else None), a


@pytest.mark.parametrize("d", [d for d in DEC if d["disposition"] == "ACCEPT_ROW"], ids=lambda d: d["term"])
def test_synthetic_powder_rows_are_conditioned_food_powder_provisional_with_the_verbatim_definition(d):
    r = LEX[d["term"]]
    assert r["kind"] == "food_powder" and "CONDITIONED" in r["source"] and "carriers or anti-caking agents" in r["source"] and r["source"].startswith("PROVISIONAL: FAO 2019") and d["clause"] in r["source"] and "held-decisions-1" in r["source"] and rec(d["term"])


def test_synthetic_a_powder_is_group_1_only_as_the_sole_item_and_otherwise_abstains_naming_the_composition_uncertainty():
    g, a = grp("Ingredients: Banana powder")
    assert g == 1 and "nothing else listed" in a.drivers[0].detail
    for text in ("Ingredients: Rice, banana powder, salt.", "Ingredients: Banana powder, strawberry powder.", "Ingredients: Milk, banana powder."):
        g, a = grp(text)
        assert g is None and "named without its composition" in a.reason and "carriers or anti-caking agents" in a.reason, text      # never answered from the term alone
    assert grp("Ingredients: Banana powder, maltodextrin.")[0] == 4          # an existing strong marker keeps priority over the powder abstention
    assert grp("Ingredients: Banana powder, salt.")[0] is None               # a Group 2 item does not turn the unresolved powder into Group 3


def test_synthetic_a_powder_never_counts_as_a_whole_food_in_a_group_3_combination():
    g, a = grp("Ingredients: Rice, banana powder, salt.")
    assert g is None                                                           # rice + salt alone would be Group 3; the powder blocks the answer instead of joining it
    assert grp("Ingredients: Rice, salt.")[0] == 3


@pytest.mark.parametrize("t", ["sprouted ragi & jowar", "rice & oat", "fortified wheat flour"])
def test_synthetic_negative_pairs_and_fortified_forms_are_not_recognised(t):
    assert not rec(t)                                                             # the '&' pair split and fortified products stay unresolved vocabulary


def test_synthetic_vitamins_and_minerals_and_sprouted_forms_are_recognised_only_as_unplaced_never_classified():
    for t in ("vitamins and minerals", "vitamins", "minerals", "sprouted ragi", "sprouted jowar"):
        assert rec(t) and LEX[t]["kind"] == "unplaced"                           # recognised by name only (workstream: unplaced kind)


def test_synthetic_a_list_with_vitamins_and_minerals_abstains_never_forced():
    g, a = grp("Ingredients: Rice, banana powder, vitamins and minerals.")
    assert g is None and [u.lower() for u in a.unplaced] == ["vitamins", "minerals"] and not any("vitamins" in u.lower() or "minerals" in u.lower() for u in a.unassessed)         # the 'and' pair splits into two recognised items


def test_owner_acceptance_label_newly_recognised_forms_and_an_honest_abstention():
    g, a = grp(LABEL)
    assert g is None and not a.answered                                          # (b) no group: weak marker only, unplaced items remain
    un = " | ".join(a.unassessed).lower()
    for t in ("banana powder", "strawberry powder", "beetroot powder", "vitamins", "minerals", "sprouted ragi", "rice & oat"):    # (a) recognised now (the '&' pairs split)
        assert t not in un, t
    assert [u.lower() for u in a.unplaced] == ["sprouted ragi", "sprouted jowar", "vitamins", "minerals"]        # shown apart, as unplaced
    assert a.unassessed == ["Multigrain Flour Blend (45.7%) (group name; its contents were assessed separately)"]  # only the blend's group name is left
    assert "antioxidant" in a.reason.lower()
