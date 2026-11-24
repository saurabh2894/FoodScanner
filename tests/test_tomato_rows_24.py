"""tomato-g3-1: a tomato concentrate is Group 3 only with salt or sugar stated and nothing else listed (Brazil Group 3 'tomato extract or concentrates (with salt and/or sugar)'); every other form abstains."""
import csv
from pathlib import Path
import pytest
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
STAGED = [r["term"] for r in csv.DictReader((ROOT / "evaluation" / "tomato_rows_24" / "staged_rows.csv").open(newline=""))]


def run(t):
    return analyse_text(f"Ingredients: {t}.", source="text")


def test_staged_count():
    assert sorted(STAGED) == ["tomato concentrate", "tomato extract"]


def test_tomato_paste_stays_parked():
    # demand_decisions_1 parks tomato paste until the owner decides; the Brazil clause names concentrates and extract, not paste
    from foodscan.classify import lookup
    assert lookup("tomato paste") is None


@pytest.mark.parametrize("t", STAGED)
@pytest.mark.parametrize("shape", ["{t}, Salt", "{t}, Sugar", "{t}, Sugar, Salt", "{t} (Salt)", "{t} (Tomato, Salt)"])
def test_with_stated_salt_or_sugar_is_group3(t, shape):
    a = run(shape.format(t=t))
    assert a.answered and a.group == 3


@pytest.mark.parametrize("t", STAGED)
@pytest.mark.parametrize("shape", ["{t}", "{t} (28°B)", "{t}, Salt, Water", "{t}, Salt, Citric Acid", "{t} powder", "Dried {t}, Salt", "{t}, {t}, Salt", "{t} (Tomato)", "{t}, Salt, Wheat Flour"])
def test_other_forms_abstain(t, shape):
    a = run(shape.format(t=t))
    assert not a.answered or a.group is None
