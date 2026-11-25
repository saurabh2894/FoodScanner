"""indian-alias-24d: moongphali = groundnut kernel (FSSAI 2.3.47(1)); behaves exactly like Peanut and Groundnuts in every form. Naming only; counted separately."""
import pytest
from foodscan.pipeline import analyse_text

FORMS = ["{}", "{}, Salt", "{} powder", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "{}, Sunflower oil, Salt", "Dried {}", "Roasted {}", "Salted {}", "{} oil", "{} butter", "{} flour", "Oil Roasted {}", "Sugared {}", "{} (Salt)", "{} (Sugar)", "Chutney ({}, Chilli)", "{} 100%", "100% {} powder", "{} protein isolate", "Hydrogenated {} oil"]


def grp(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


@pytest.mark.parametrize("form", FORMS)
def test_moongphali_matches_peanut_and_groundnuts(form):
    assert grp(form.format("Moongphali")) == grp(form.format("Peanuts")) == grp(form.format("Groundnuts"))


def test_groundnut_kernel_phrase_not_encoded():
    assert grp("Groundnut kernel") is None
