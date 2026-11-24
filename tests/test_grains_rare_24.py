"""grains-rare-24: rare grains behave exactly like the existing sorghum grain row."""
import csv
from pathlib import Path
import pytest
from foodscan.classify import lookup
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
STAGED = [r["term"] for r in csv.DictReader((ROOT / "evaluation" / "grains_rare_24" / "staged_rows.csv").open(newline=""))]


def test_staged():
    assert STAGED == ["einkorn", "fonio", "khorasan", "farro", "bulgur"]
    assert all(lookup(t)["kind"] == "whole_food" for t in STAGED)


@pytest.mark.parametrize("term", STAGED)
@pytest.mark.parametrize("shape", ["{}", "{}, Salt", "{} (Colour)", "{}, Maltodextrin", "Wheat semolina (75%), {}, Mustard"])
def test_same_outcome_as_sorghum(term, shape):
    a = analyse_text("Ingredients: " + shape.format(term.capitalize()) + ".", source="text")
    b = analyse_text("Ingredients: " + shape.format("Sorghum") + ".", source="text")
    assert (a.answered, a.group) == (b.answered, b.group)


def test_marker_still_wins():
    assert analyse_text("Ingredients: Bulgur, Maltodextrin.", source="text").group == 4


def test_no_unverified_alias():
    assert lookup("kamut") is None and lookup("emmer") is None


@pytest.mark.parametrize("term", STAGED)
def test_flour_forms_stay_unresolved(term):
    a = analyse_text("Ingredients: " + term.capitalize() + " flour.", source="text")
    assert not a.answered
