"""millets-24: FSSAI 2.4.6 millets/pulses list (full PDF). Heads: teff, amaranth grain, kodo millet, little millet, barnyard millet (FAO grains class-instance; FDC 169747/170682 for teff and amaranth grain, FSSAI naming for the millets). proso millet is RECOGNITION-ONLY (the generic millet grain). Aliases: mandua, kangni, kakun, kutki, kodo, sanwa, jhangora, cheena, kuttu, kabuli chana, arhar. Bare 'amaranth' abstains (leaf vs grain)."""
import csv
from pathlib import Path
import pytest
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
PAIRS = [(r["from"], r["to"]) for r in csv.DictReader((ROOT / "evaluation" / "millets_24" / "aliases.csv").open(newline=""))]
FORMS = ["{}", "{}, Salt", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "Dried {}", "Roasted {}", "{} (Sugar)", "{} 100%", "{} powder", "{} flour", "{} flakes", "Puffed {}", "{} puffs", "Cooked {}", "Sprouted {}", "Malted {}", "{} (Salt)", "Hydrogenated {}", "Instant {}", "{} extract", "{} protein", "Polished {}", "{} semolina"]


def grp(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


@pytest.mark.parametrize("pair", PAIRS)
@pytest.mark.parametrize("form", FORMS)
def test_alias_matches_target(pair, form):
    a, b = pair
    assert grp(form.format(a.title())) == grp(form.format(b.title())), (a, b, form)


@pytest.mark.parametrize("t", ["Teff", "Amaranth grain", "Kodo millet", "Little millet", "Barnyard millet", "Proso millet", "Arhar", "Mandua", "Kuttu"])
def test_sole_plain_grain_group_1(t):
    assert grp(t) == 1


def test_guards():
    assert grp("Amaranth") is None
    assert grp("Arhar dal") == 1 and grp("Arhar dal, Salt") == 3
    for t in ["Kodo millet flour", "Teff flour", "Puffed teff"]:
        assert grp(t) is None
