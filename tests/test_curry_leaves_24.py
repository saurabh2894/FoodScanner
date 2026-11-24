"""curry-leaves-24: curry leaves is a recognised herb row, behaving exactly like the existing herb rows (e.g. mint)."""
import csv
from pathlib import Path
import pytest
from foodscan.classify import lookup
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
STAGED = [r["term"] for r in csv.DictReader((ROOT / "evaluation" / "curry_leaves_24" / "staged_rows.csv").open(newline=""))]


def test_staged():
    assert STAGED == ["curry leaves"]
    assert lookup("curry leaves")["kind"] == "herb_spice"


@pytest.mark.parametrize("shape", ["{}", "{}, Salt", "Dried {}", "{} powder", "{} (Colour)"])
def test_same_outcome_as_mint(shape):
    a = analyse_text("Ingredients: " + shape.format("Curry leaves") + ".", source="text")
    b = analyse_text("Ingredients: " + shape.format("Mint") + ".", source="text")
    assert (a.answered, a.group) == (b.answered, b.group)


def test_marker_still_wins():
    a = analyse_text("Ingredients: Curry leaves, Maltodextrin.", source="text")
    assert a.answered and a.group == 4


def test_no_unverified_alias():
    assert lookup("kadi patta") is None
