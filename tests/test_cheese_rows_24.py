"""cheese-g3-1: sole plain cheese rows are Group 3 (Brazil 'cheeses', FAO 'simple cheeses to which salt is added'); every other form abstains."""
import csv
from pathlib import Path
import pytest
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
STAGED = [r["term"] for r in csv.DictReader((ROOT / "evaluation" / "cheese_rows_24" / "staged_rows.csv").open(newline=""))]


def run(t):
    return analyse_text(f"Ingredients: {t}.", source="text")


def test_staged_count():
    assert len(STAGED) == 13 and len(set(STAGED)) == 13


@pytest.mark.parametrize("t", STAGED)
def test_sole_plain_is_group3(t):
    a = run(t)
    assert a.answered and a.group == 3


@pytest.mark.parametrize("t", ["Cheese powder", "Cheese (Cheddar)", "Cheddar, Salt", "Cheese, Wheat Flour", "Milk, Cheese", "Processed cheese", "Grated Mozzarella", "Cheddar powder", "Smoked Cheddar", "Cheese spread"])
def test_other_forms_abstain(t):
    a = run(t)
    assert not a.answered or a.group is None
