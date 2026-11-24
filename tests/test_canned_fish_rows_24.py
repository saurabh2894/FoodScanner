"""canned-fish-g3-1: the canned or tinned names of tuna and sardine are Group 3 (Brazil and PAHO 'canned sardine and tuna'); bare names stay unrecognised; other content abstains."""
import csv
from pathlib import Path
import pytest
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
STAGED = [r["term"] for r in csv.DictReader((ROOT / "evaluation" / "canned_fish_rows_24" / "staged_rows.csv").open(newline=""))]


def run(t):
    return analyse_text(f"Ingredients: {t}.", source="text")


def test_staged_count():
    assert len(STAGED) == 6 and len(set(STAGED)) == 6


@pytest.mark.parametrize("t", STAGED)
@pytest.mark.parametrize("shape", ["{t}", "{t}, Water, Salt", "{t}, Sunflower Oil", "{t} (in Oil)", "{t} (Water, Salt)", "{t}, Olive Oil, Salt"])
def test_canned_is_group3(t, shape):
    a = run(shape.format(t=t))
    assert a.answered and a.group == 3


@pytest.mark.parametrize("t", STAGED)
@pytest.mark.parametrize("shape", ["{t}, Tomato Sauce", "{t}, Soy Protein", "{t} powder", "{t}, {t}", "{t} (Tuna, Salt)", "{t}, Wheat Flour", "Smoked {t}", "{t}, Milk"])
def test_other_forms_abstain(t, shape):
    a = run(shape.format(t=t))
    assert not a.answered or a.group is None


@pytest.mark.parametrize("t", ["Tuna", "Sardine", "Sardines", "Tuna (Canned)", "Tuna in Oil"])
def test_bare_names_stay_unrecognised(t):
    a = run(t)
    assert not a.answered or a.group is None
