"""beetroot-24: label 'beetroot' is a vegetable; the beet red colour wording abstains; bare beet/beets stay out."""
import pytest
from foodscan.pipeline import analyse_text


def run(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


@pytest.mark.parametrize("t,g", [("Beetroot", 1), ("Beetroot, Salt", 3), ("Dried beetroot", 1), ("Roasted beetroot", 1), ("Beetroot, Sugar", 3), ("Beetroot flavour", 4), ("Beetroot colour", 4)])
def test_beetroot_forms(t, g):
    assert run(t) == g


@pytest.mark.parametrize("t", ["Beetroot red", "Beet red", "Beet red powder", "Beetroot red powder", "Wheat flour, Beetroot red", "Beetroot (5%), Water", "Beetroot juice", "Pickled beetroot", "Beetroot extract", "Beetroot fibre", "Beet", "Beets"])
def test_collisions_and_unknown_forms_abstain(t):
    assert run(t) is None
