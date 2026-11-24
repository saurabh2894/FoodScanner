"""group2-named-24: molasses and maple syrup, named in the FAO Group 2 examples, behave like the existing honey row."""
import csv
from pathlib import Path
import pytest
from foodscan.classify import lookup
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
STAGED = [r["term"] for r in csv.DictReader((ROOT / "evaluation" / "group2_named_24" / "staged_rows.csv").open(newline=""))]


def test_staged():
    assert STAGED == ["molasses", "maple syrup"] and all(lookup(t)["kind"] == "culinary" for t in STAGED)


@pytest.mark.parametrize("term", STAGED)
@pytest.mark.parametrize("shape", ["{}", "{}, Salt", "{} (Colour)", "{}, Maltodextrin", "Wheat flour, {}, Mustard", "Dried {}", "{} powder", "{}, Flavour"])
def test_same_outcome_as_honey(term, shape):
    a = analyse_text("Ingredients: " + shape.format(term.capitalize()) + ".", source="text")
    b = analyse_text("Ingredients: " + shape.format("Honey") + ".", source="text")
    assert (a.answered, a.group) == (b.answered, b.group)


def test_flavoured_and_bare_maple_stay_unrecognised():
    assert lookup("maple") is None and lookup("maple flavoured syrup") is None and lookup("pancake syrup") is None
