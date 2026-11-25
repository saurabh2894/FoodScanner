"""cured-meat-g3-1: sole plain bacon, ham and pastrami are Group 3 (FAO Group 3 prose names ham, bacon, pastrami; identity USDA FDC SR Legacy); every other form abstains."""
import csv
from pathlib import Path
import pytest
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
STAGED = [r["term"] for r in csv.DictReader((ROOT / "evaluation" / "cured_meat_24" / "staged_rows.csv").open(newline=""))]


def run(t):
    return analyse_text(f"Ingredients: {t}.", source="text")


def test_staged():
    assert STAGED == ["bacon", "ham", "pastrami"]


@pytest.mark.parametrize("t", STAGED)
def test_sole_plain_is_group3(t):
    a = run(t.capitalize())
    assert a.answered and a.group == 3


FORMS = ["{}, Salt", "Smoked {}", "{} powder", "Raw {}", "{} bits", "Meatless {}", "Turkey {}", "Vegan {}", "{} (Pork)", "{}, Cheese", "{} salad", "Dried {}", "Canned {}", "Sliced {}", "{} flavour"]


@pytest.mark.parametrize("t", STAGED)
@pytest.mark.parametrize("f", FORMS)
def test_other_forms_never_group3(t, f):
    a = run(f.format(t.capitalize()))
    assert not (a.answered and a.group == 3)


def test_neighbours_unchanged():
    for n in ["Salami", "Jerky", "Sausage", "Gammon", "Prosciutto"]:
        a = run(n)
        assert not a.answered or a.group is None
