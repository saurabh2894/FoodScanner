"""tomato-24b: tomato paste and tomato puree are FSSAI 2.3.14 / Codex CXS 57 designations of tomato concentrate. Every probed form must equal the concentrate row's behaviour (Group 3 only with stated salt or sugar and nothing else; every other form abstains)."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


SHAPES = ["{t}", "{t}, Salt", "{t}, Sugar", "{t}, Sugar, Salt", "{t} (Salt)", "{t} (Tomato, Salt)", "{t} (28\u00b0B)", "{t}, Salt, Water",
          "{t}, Salt, Citric Acid", "{t} powder", "Dried {t}", "{t}, {t}, Salt", "{t} (Tomato)", "{t}, Salt, Wheat Flour", "Wheat flour, Salt, {t}",
          "Rice, {t}", "Sugar, {t}", "{t} 100%", "Canned {t}", "Organic {t}, Salt"]


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("alias", ["Tomato paste", "Tomato puree"])
def test_alias_equals_concentrate(alias, shape):
    assert g(shape.format(t=alias)) == g(shape.format(t="Tomato concentrate")), (alias, shape)


@pytest.mark.parametrize("alias", ["Tomato paste", "Tomato puree"])
def test_group3_only_with_stated_salt_or_sugar(alias):
    assert g(alias) is None
    assert g(alias + ", Salt") == 3
    assert g(alias + ", Sugar, Salt") == 3
    assert g(alias + ", Salt, Water") is None


@pytest.mark.parametrize("alias", ["Tomato paste", "Tomato puree"])
def test_never_group_4_as_a_named_neighbour(alias):
    assert g("Wheat flour, Salt, " + alias) != 4
