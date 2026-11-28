"""generic-fish-24: generic cod, halibut, pollock, flounder, crab, lobster behave like their existing species rows in every probed form."""
import pytest
from foodscan.pipeline import analyse_text


def res(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "{}, Sugar", "Dried {}", "{} powder", "Smoked {}", "Canned {}", "Salted {}", "Breaded {}", "Fried {}", "{} (5%), Water", "Rice, {}", "{} flavour", "{} paste", "{} stick", "Hydrogenated {}"]
SPECIES = {"Cod": "Atlantic cod", "Halibut": "Greenland halibut", "Pollock": "Alaska pollock", "Flounder": "Atlantic cod", "Crab": "Dungeness crab", "Lobster": "Northern lobster"}


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", list(SPECIES))
def test_matches_species_row(form, name):
    assert res(form.format(name)) == res(form.format(SPECIES[name]))


# shrimp-24 lifted shrimp (tests/test_shrimp_24.py).
def test_held_generics_stay_unrecognised():
    for n in ["Salmon", "Tuna", "Roe", "Herring", "Mackerel", "Anchovy"]:
        assert res(n) is None

# audit-24m: fifteen rows that were the same food as an existing row, demoted to RECOGNITION-ONLY (species-identity audit).
AUDIT_24M = ["jicama", "waterchestnuts", "sapote", "redcurrants", "mungobeans", "winter squashes", "cress", "chrysanthemum leaves", "bajra", "jowar", "maize", "groundnut oil", "chillies", "rajma", "moong"]


def test_generic_labels_are_excluded_from_the_head_count():
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
    import count_heads
    c = count_heads.counts()
    # smoked-fish-24 adds five explicit smoked-fish names (recognition-only coverage). yoghurt-24: "plain yoghurt" is recognition-only (variant of the existing dahi head per the FSSAI clubbing list), so it joins the six generic fish labels
    # millets-24: proso millet joins (the generic millet grain's species name).
    # flour-24: pearl millet flour and ragi flour join the recognition-only list (species flours of the millet flour row).
    assert sorted(c["recognition_only"]) == sorted(AUDIT_24M + ["cod", "crab", "flounder", "halibut", "kippered herring", "lobster", "plain yoghurt", "pearl millet flour", "proso millet", "pollock", "ragi flour", "smoked haddock", "smoked salmon", "smoked sturgeon", "smoked whitefish"])
    assert c["placed_rows"] - c["canonical_placed"] >= 6
