"""hydrolysed-protein-24: FAO 2019 p.10 names hydrolysed proteins as a UPF-identifying substance class."""
import pytest
from foodscan.pipeline import analyse_text


def run(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.answered, a.group


@pytest.mark.parametrize("name", ["Hydrolysed protein", "Hydrolysed proteins", "Hydrolyzed protein", "Hydrolyzed vegetable protein", "Hydrolysed soy protein", "Hydrolysed wheat protein", "Hydrolysed milk protein", "Hydrolysed plant protein"])
@pytest.mark.parametrize("t", ["Wheat flour, Salt, {}", "Water, {}"])
def test_hydrolysed_protein_is_group_4(t, name):
    assert run(t.format(name)) == (True, 4)


@pytest.mark.parametrize("name", ["Soy protein", "Wheat protein", "Milk protein", "Hydrolysed starch", "Hydrolysed collagen", "Protein hydrolysate", "Hydrolysed protein free", "Without hydrolysed protein"])
def test_neighbours_and_negations_do_not_move(name):
    assert run("Wheat flour, Salt, " + name) != (True, 4)
