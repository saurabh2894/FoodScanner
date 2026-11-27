"""general-24v: three new heads (cornelian cherry, orache, scorzonera) plus two name aliases (lamb's lettuce to cornsalad, black salsify to scorzonera). Plain forms behave like existing plain fruit/vegetable rows; processed forms abstain."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


@pytest.mark.parametrize("t,ref", [("Cornelian cherry", "Medlar"), ("Cornelian cherries", "Medlar"), ("Orache", "Watercress"), ("Scorzonera", "Salsify"), ("Black salsify", "Salsify"), ("Lamb's lettuce", "Cornsalad")])
def test_plain_equals_reference_row(t, ref):
    assert g(t) == g(ref) == 1


@pytest.mark.parametrize("t,ref", [("{}, Salt", "Watercress"), ("Sugar, {}", "Watercress")])
@pytest.mark.parametrize("name", ["Cornelian cherry", "Orache", "Scorzonera", "Black salsify", "Lamb's lettuce"])
def test_added_salt_or_sugar_matches_reference(t, ref, name):
    assert g(t.format(name)) == g(t.format(ref)) == 3


@pytest.mark.parametrize("t", ["Orache powder", "Cornelian cherry jam", "Canned scorzonera", "Scorzonera extract"])
def test_processed_forms_abstain(t):
    assert g(t) is None


def test_scorzonera_is_not_salsify_row():
    from foodscan.tables import load_table
    syn = {r["from"].lower(): r["to"].lower() for r in load_table("synonyms.csv")}
    assert "scorzonera" not in syn and syn["black salsify"] == "scorzonera"
