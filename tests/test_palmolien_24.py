"""palmolien-24: Indian trade spelling "palmolien" aliases palmolein (spelling only). Pure typos such as maltodectrin stay unrecognised."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return (a.group if a.answered else None), a.unassessed


SHAPES = ["{t}", "{t}, Salt", "{t}, Maltodextrin", "{t}, Sugar", "Refined {t}", "{t} (Palm)", "Wheat flour, {t}", "{t}, Emulsifier (471)", "{t}, Spices & Condiments"]


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("alias", ["Palmolien", "Palmolien oil", "Refined Palmolien Oil"])
def test_alias_equals_palmolein(alias, shape):
    assert g(shape.format(t=alias)) == g(shape.format(t="Palmolein")), (alias, shape)


def test_maltodectrin_stays_unrecognised():
    assert g("Maltodectrin")[0] is None
