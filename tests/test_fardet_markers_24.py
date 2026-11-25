"""fardet-markers-24: glucose syrup, malt extract and liquid glucose are Group 4 markers; free-from and unnamed neighbours do not move."""
import pytest
from foodscan.pipeline import analyse_text


def run(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.answered, a.group


@pytest.mark.parametrize("t", ["Wheat flour, Salt, {}", "Water, {}", "Wheat flour, {} (Stabiliser)"])
@pytest.mark.parametrize("name", ["Glucose syrup", "Liquid glucose", "Malt extract", "Barley malt extract", "Dried glucose syrup", "Glucose syrup solids"])
def test_named_substance_is_group_4(t, name):
    assert run(t.format(name)) == (True, 4)


@pytest.mark.parametrize("name", ["Glucose", "Sugar syrup", "Malted barley", "Malt", "Barley malt", "Glucose free", "Free from glucose syrup", "Without malt extract", "No added glucose syrup", "Glucose syrup-free"])
def test_unnamed_neighbours_and_negations_do_not_trigger(name):
    assert run("Wheat flour, Salt, " + name) != (True, 4)
