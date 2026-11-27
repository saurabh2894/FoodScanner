"""tomato-24b: tomato paste (25 percent soluble solids or more in FSSAI 2.3.14 and Codex CXS 57) is a tomato concentrate; tomato puree is deliberately NOT aliased (the evidence covers only a confirmed concentrate, not a bare puree). Every probed form must equal the concentrate row's behaviour (Group 3 only with stated salt or sugar and nothing else; every other form abstains)."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


SHAPES = ["{t}", "{t}, Salt", "{t}, Sugar", "{t}, Sugar, Salt", "{t} (Salt)", "{t} (Tomato, Salt)", "{t} (28\u00b0B)", "{t}, Salt, Water",
          "{t}, Salt, Citric Acid", "{t} powder", "Dried {t}", "{t}, {t}, Salt", "{t} (Tomato)", "{t}, Salt, Wheat Flour", "Wheat flour, Salt, {t}",
          "Rice, {t}", "Sugar, {t}", "{t} 100%", "Canned {t}", "Organic {t}, Salt"]


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("alias", ["Tomato paste"])
def test_alias_equals_concentrate(alias, shape):
    assert g(shape.format(t=alias)) == g(shape.format(t="Tomato concentrate")), (alias, shape)


@pytest.mark.parametrize("alias", ["Tomato paste"])
def test_group3_only_with_stated_salt_or_sugar(alias):
    assert g(alias) is None
    assert g(alias + ", Salt") == 3
    assert g(alias + ", Sugar, Salt") == 3
    assert g(alias + ", Salt, Water") is None


@pytest.mark.parametrize("alias", ["Tomato paste"])
def test_never_group_4_as_a_named_neighbour(alias):
    assert g("Wheat flour, Salt, " + alias) != 4


@pytest.mark.parametrize("shape", ["{t}", "{t}, Salt", "{t}, Sugar, Salt", "{t} (Salt)", "Wheat flour, Salt, {t}", "{t} 67%"])
def test_bare_tomato_puree_is_never_placed_even_with_salt(shape):
    # scope gap found by main 07:06: a fresh blended puree plus salt must not become Group 3 through the concentrate rule
    assert g(shape.format(t="Tomato puree")) is None


def test_tomato_puree_is_not_an_alias():
    from foodscan.normalise import normalise_ingredient
    assert normalise_ingredient("tomato puree").name != "tomato concentrate"
