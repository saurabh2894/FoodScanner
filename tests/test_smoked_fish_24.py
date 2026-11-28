"""smoked-fish-g3-1 (recognition-only coverage): an explicitly named smoked fish alone is Group 3 (FAO Group 3 prose 'smoked fish'; identity FDC SR Legacy); every other form abstains."""
import csv
from pathlib import Path
import pytest
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
STAGED = [r["term"] for r in csv.DictReader((ROOT / "evaluation" / "smoked_fish_24" / "staged_rows.csv").open(newline=""))]


def run(t):
    return analyse_text(f"Ingredients: {t}.", source="text")


def test_staged():
    assert STAGED == ["smoked haddock", "smoked salmon", "smoked whitefish", "smoked sturgeon", "kippered herring"]


@pytest.mark.parametrize("t", STAGED)
def test_sole_plain_is_group3(t):
    a = run(t.capitalize())
    assert a.answered and a.group == 3


FORMS = ["{}, Salt", "{} (Atlantic)", "{} powder", "Canned {}", "Salted {}", "{} pate", "{} spread", "Raw {}", "Milk, {}", "{}, Dill", "{} fillets", "{} flavour", "Dried {}"]


@pytest.mark.parametrize("t", STAGED)
@pytest.mark.parametrize("f", FORMS)
def test_other_forms_never_group3(t, f):
    a = run(f.format(t.capitalize()))
    assert not (a.answered and a.group == 3)


def test_neighbours_unchanged():
    assert run("Haddock").group == 1 and run("Dried haddock").group == 3
    for n in ["Salmon", "Herring", "Smoked trout", "Smoked chicken", "Smoked paprika"]:
        a = run(n)
        assert not a.answered or a.group is None
