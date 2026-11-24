"""clause-named-24: pasta, couscous, polenta (named in the FAO Group 1 definition), rye and hemp seed."""
import csv
from pathlib import Path
import pytest
from foodscan.classify import lookup
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
STAGED = [r["term"] for r in csv.DictReader((ROOT / "evaluation" / "clause_named_24" / "staged_rows.csv").open(newline=""))]
LIKE = {"pasta": "Sorghum", "couscous": "Sorghum", "polenta": "Sorghum", "rye": "Sorghum", "hemp seeds": "Pecans"}


def test_staged():
    assert STAGED == ["pasta", "couscous", "polenta", "rye", "hemp seed", "hemp seeds"]
    assert all(lookup(x) for x in STAGED)


def test_held_terms_stay_held():
    # poppy seed: parked (overlaps the conditioned nuts/seeds clause); lotus seeds: held by the class_bulk_5 review (oily-seed membership unsupported); caraway seed is a synonym of caraway.
    assert lookup("poppy seed") is None and lookup("lotus seeds") is None


@pytest.mark.parametrize("term", sorted(LIKE))
@pytest.mark.parametrize("shape", ["{}", "{}, Salt", "{} (Colour)", "{}, Maltodextrin", "Wheat semolina (75%), {}, Mustard", "{}, Sugar"])
def test_same_outcome_as_reference_row(term, shape):
    a = analyse_text("Ingredients: " + shape.format(term.capitalize()) + ".", source="text")
    b = analyse_text("Ingredients: " + shape.format(LIKE[term]) + ".", source="text")
    assert (a.answered, a.group) == (b.answered, b.group)


def test_composition_conditions_do_not_place_group_1():
    for t in ["Pasta (Egg, Wheat flour)", "Cheese pasta", "Pasta sauce", "Pasta, Maltodextrin", "Pasta (Flavour)"]:
        a = analyse_text("Ingredients: " + t + ".", source="text")
        assert a.group != 1, t


def test_markers_and_salt_still_win():
    assert analyse_text("Ingredients: Couscous, Maltodextrin.", source="text").group == 4
    assert analyse_text("Ingredients: Hemp seeds (Salted).", source="text").group == 3


def test_no_unverified_alias():
    assert lookup("makhana") is None and lookup("fox nuts") is None and lookup("hempseed") is None


@pytest.mark.parametrize("term", ["pasta", "couscous", "polenta", "rye"])
def test_bracketed_salted_form_is_never_group_1(term):
    a = analyse_text("Ingredients: " + term.capitalize() + " (Salted).", source="text")
    assert a.group != 1
