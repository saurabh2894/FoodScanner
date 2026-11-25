"""triticale-24: triticale behaves like the rye row in every probed form."""
import pytest
from foodscan.pipeline import analyse_text


def res(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


@pytest.mark.parametrize("form", ["{}", "{}, Salt", "{}, Sugar", "Roasted {}", "{} flakes", "{} flavour", "{} extract", "{} (5%), Water", "Sprouted {}", "{} malt", "{} starch"])
def test_matches_rye(form):
    assert res(form.format("Triticale")) == res(form.format("Rye"))


def test_flour_abstains():
    assert res("Triticale flour") is None
