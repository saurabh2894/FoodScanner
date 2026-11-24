"""game-meat-24: antelope, bison, boar, caribou, deer, moose, rabbit as animal meat rows (FDC SR Legacy 'Game meat' raw records; FAO Group 1 meat example), same guards as animal-guard-1."""
import csv
from pathlib import Path
import pytest
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
STAGED = [r["term"] for r in csv.DictReader((ROOT / "evaluation" / "game_meat_24" / "staged_rows.csv").open(newline=""))]


def g(t):
    a = analyse_text(f"Ingredients: {t}, Salt.", source="text")
    return a.group if a.answered else None


def test_seven_rows_staged():
    assert STAGED == ["antelope", "bison", "boar", "caribou", "deer", "moose", "rabbit"]


@pytest.mark.parametrize("t", STAGED)
def test_plain_form_with_salt_is_group_3(t):
    assert g(t) == 3  # salt is a Group 2 ingredient added to a Group 1 food


@pytest.mark.parametrize("t", STAGED)
def test_dried_is_group_3_and_processed_forms_abstain(t):
    assert analyse_text(f"Ingredients: Dried {t}.", source="text").group == 3
    for form in ["Smoked {}", "Canned {}", "{} powder", "{} sausage", "Fried {}", "Breaded {}"]:
        assert not (a := analyse_text("Ingredients: " + form.format(t) + ".", source="text")).answered or a.group in (3, None), form
