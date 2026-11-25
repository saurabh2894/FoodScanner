"""fibre-marker-24: FAO p.10 names soluble or insoluble fibre; claim wording and unnamed fibres do not trigger."""
import pytest
from foodscan.pipeline import analyse_text


def run(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.answered, a.group


@pytest.mark.parametrize("name", ["soluble fibre", "Insoluble fibre", "Soluble fiber", "insoluble fiber"])
@pytest.mark.parametrize("t", ["Wheat flour, Salt, {}", "Water, {}", "Wheat flour, {} (Stabiliser)"])
def test_named_fibre_is_group_4(t, name):
    assert run(t.format(name)) == (True, 4)


@pytest.mark.parametrize("name", ["Oat fibre", "Dietary fibre", "Soluble fibre-free", "Without soluble fibre"])
def test_unnamed_or_claim_forms_do_not_trigger(name):
    assert run("Wheat flour, Salt, " + name) != (True, 4)


@pytest.mark.parametrize("t", ["Rice, Salt (source of lactose)", "Rice, Sugar (high in fructose)", "Oats (source of soluble fibre)", "Oats (rich in insoluble fibre)", "Wheat flour, Milk solids (source of lactose)"])
def test_claim_wording_alone_abstains(t):
    # A parenthesis can describe a natural content or an added isolated ingredient: neither Group 4 nor a lower group.
    assert run(t) == (False, None)


@pytest.mark.parametrize("t", ["Oats (source of soluble fibre), Maltodextrin", "Oats (source of lactose), Lactose", "Rice, Salt (high in fructose), Wheat gluten"])
def test_independent_group4_driver_is_preserved(t):
    assert run(t) == (True, 4)
