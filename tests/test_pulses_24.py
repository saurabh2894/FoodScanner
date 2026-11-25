"""pulses-24: FSSAI 2.4.6(2)(VI) horse gram (Kulthi), FAO legumes class-instance, same conditions as mothbeans; alias kulthi."""
import csv
from pathlib import Path
import pytest
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
PAIRS = [(r["from"], r["to"]) for r in csv.DictReader((ROOT / "evaluation" / "pulses_24" / "aliases.csv").open(newline=""))]
FORMS = ["{}", "{}, Salt", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "Dried {}", "Roasted {}", "{} (Sugar)", "{} 100%", "{} powder", "{} flour", "{} flakes", "Puffed {}", "{} puffs", "Cooked {}", "Sprouted {}", "Malted {}", "{} (Salt)", "Hydrogenated {}", "Instant {}", "{} extract", "{} protein", "Polished {}", "{} semolina"]


def grp(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


@pytest.mark.parametrize("pair", PAIRS)
@pytest.mark.parametrize("form", FORMS)
def test_alias_matches_target(pair, form):
    a, b = pair
    assert grp(form.format(a.title())) == grp(form.format(b.title())), (a, b, form)


@pytest.mark.parametrize("t", ["Horse gram", "Kulthi"])
def test_sole_plain_pulse_group_1(t):
    assert grp(t) == 1


def test_guards():
    assert grp("Horse gram, Salt") == grp("Moth bean, Salt") == 3
    for t in ["Horse gram flour", "Puffed horse gram"]:
        assert grp(t) == grp(t.replace("Horse gram", "Moth bean"))
