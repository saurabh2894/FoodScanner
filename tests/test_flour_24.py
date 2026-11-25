"""flour-24: cassava flour (head), pearl millet flour and ragi flour (RECOGNITION-ONLY species flours), plus FSSAI 2.4 aliases jowar flour = sorghum flour, bajra flour = pearl millet flour, tapioca flour = cassava flour. Naming/placement from FSSAI Chapter 2.4 (full PDF) and the FAO flour clause. Salted forms abstain for the new rows (conservative; wheat flour and millet flour have an older salted rule)."""
import pytest
from foodscan.pipeline import analyse_text

FORMS = ["{}", "{}, Salt", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "{}, Sunflower oil, Salt", "Dried {}", "Roasted {}", "{} (Sugar)", "Chutney ({}, Chilli)", "{} 100%", "{} powder", "{} starch", "Hydrogenated {}", "Fermented {}", "Sweetened {}", "{} protein isolate", "Bleached {}", "{} (Bleached)", "{} (Maida)"]
FAMS = [("Cassava flour", "Tapioca flour", "Wheat flour"), ("Pearl millet flour", "Bajra flour", "Millet flour"), ("Jowar flour", "Sorghum flour", "Millet flour")]


def grp(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("fam", FAMS)
def test_family_behaves_alike(fam, form):
    assert len({grp(form.format(x)) for x in fam}) == 1, (fam, form)


@pytest.mark.parametrize("t", ["Cassava flour", "Tapioca flour", "Pearl millet flour", "Bajra flour", "Ragi flour", "Jowar flour"])
def test_sole_flour_group_1(t):
    assert grp(t) == 1


def test_salted_and_other_unproved_forms_abstain():
    for t in ["Salted Cassava flour", "Cassava flour (Salt)", "Cassava flour, Salt"]:
        assert grp(t) in (None, 3)
    assert grp("Tapioca starch") == 2
    assert grp("Cassava") is None or grp("Cassava") == 1
