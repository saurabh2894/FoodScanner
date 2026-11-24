"""fao-named-substances-24: FAO 2019 p.10 names casein, whey protein, mechanically separated meat and fruit juice concentrate as UPF-identifying substances."""
import pytest
from foodscan.pipeline import analyse_text


def run(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.answered, a.group


@pytest.mark.parametrize("t", ["Wheat flour, Salt, {}", "Water, {}", "Wheat flour, {} (Stabiliser)"])
@pytest.mark.parametrize("name", ["Casein", "Lactose", "Gluten", "Whey protein concentrate", "Whey protein isolate", "Mechanically separated meat", "Fruit juice concentrate", "Lemon juice concentrate"])
def test_named_substance_is_group_4(t, name):
    assert run(t.format(name)) == (True, 4)


@pytest.mark.parametrize("name", ["Tomato paste", "Orange juice from concentrate", "Whey", "Milk protein", "Lactase enzyme"])
def test_unnamed_neighbours_do_not_move(name):
    assert run("Wheat flour, Salt, " + name) != (True, 4)


@pytest.mark.parametrize("name", ["Lactose free milk", "Milk (lactose free)", "Gluten free oats", "Gluten-free wheat flour", "Casein free", "Without gluten", "Free from gluten", "Non gluten flour", "No added lactose", "Lactose-free milk powder", "Whey protein-free"])
def test_free_from_and_negated_forms_are_not_markers(name):
    assert run("Wheat flour, Salt, " + name) != (True, 4)


def test_held_terms_stay_unstaged():
    import csv
    from pathlib import Path
    terms = {r["term"] for r in csv.DictReader((Path(__file__).resolve().parent.parent / "src/foodscan/resources/markers.csv").open(newline=""))}
    assert not ({"hydrolysed protein", "corn syrup"} & terms)
