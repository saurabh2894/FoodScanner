"""Milk powder exception to the powder standard (owner post-merge refinement 2026-11-21; SYNTHETIC, both directions).
FAO Table 1 Group 1 (p.11) names the powdered form by name: 'frozen eggs; fresh, powdered or pasteurized milk'. Only '<optional fat-grade word> milk powder' (milk, toned milk, buffalo milk; grade words
whole/skimmed/skim) takes that exact-named clause. Everything else stays under the powder standard (tests/test_powder_standard_1.py): non-milk powders, 'milk solids powder' (a solids fraction is not the
named form), fortified/instant/blend/vitamin-added forms and any milk powder with extra words."""
from __future__ import annotations

import pytest

from foodscan.pipeline import analyse_text


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return (a.group if a.answered else None), a


@pytest.mark.parametrize("t", ["Milk Powder", "Whole Milk Powder", "Skimmed Milk Powder", "Toned Milk Powder", "Buffalo Milk Powder", "Whole Buffalo Milk Powder", "Milk Powder (45%)", "Skimmed Milk Powder (Milk)"])
def test_synthetic_the_enumerated_fat_grade_milk_powder_forms_take_group_1_via_the_exact_named_clause(t):
    group, a = g(t)
    assert group == 1 and "fresh, powdered or pasteurized milk" in a.drivers[0].detail, (t, group)


@pytest.mark.parametrize("t", ["Fortified Milk Powder", "Instant Milk Powder", "Milk Powder Blend", "Milk Powder (Vitamins Added)", "Skimmed Milk Powder (Soy Lecithin)", "Milk Powder (Vitamin D)", "Whole Milk Powder (Fortified)"])
def test_synthetic_negative_modified_fortified_or_blended_milk_powders_never_slip_through_the_exception(t):
    group, a = g(t)
    assert group != 1 and not any("powdered milk" in d.detail for d in a.drivers), (t, group)


@pytest.mark.parametrize("t", ["Milk Solids Powder", "Whole Milk Solids Powder", "Rice, Milk Solids Powder", "Milk Solids Powder, Rice", "Blend (Milk Solids Powder, Salt)", "Rice, Salt, Milk Solids Powder"])
def test_synthetic_negative_milk_solids_powder_abstains_in_every_position(t):
    group, a = g(t)
    assert group is None and not any("powdered milk" in d.detail for d in a.drivers), (t, group)


def test_synthetic_milk_solids_alone_is_unchanged_and_non_milk_powders_still_abstain():
    # UPDATED (milk-24e): generic milk solids abstains outside a fermented milk (milk plus culture rule still gives 1); FSSAI 2.1 uses the words only as a composition measure, 2.7 defines them for chocolate only, and the term can name a fraction or concentrate.
    assert g("Milk Solids")[0] is None
    for t in ("Spinach Powder", "Banana Powder", "Egg Powder", "Carrot Powder", "Rice Powder"):
        group, a = g(t)
        assert group is None and "named without its composition" in (a.reason or ""), t
    assert g("100% Spinach Powder")[0] == 1


def test_synthetic_milk_powder_in_lists_follows_the_plain_row_behaviour_again():
    assert g("Rice, Salt, Milk Powder")[0] == 3
    assert g("Rice, Milk Powder")[0] is None


def test_synthetic_the_committed_gate_shows_exactly_the_six_milk_powder_forms_moving_abstain_to_group_1():
    import json
    from pathlib import Path
    C = json.loads((Path(__file__).resolve().parent.parent / "evaluation" / "milk_powder_1" / "applied_gate" / "applied_gate.json").read_text(encoding="utf-8"))
    assert C["verdict"] == "READY_FOR_REVIEW" and not C["blockers"]
    assert C["powder_surface"]["changed"] == {f: [None, 1] for f in ("milk powder", "whole milk powder", "toned milk powder", "whole toned milk powder", "buffalo milk powder", "whole buffalo milk powder")}
    assert C["powder_surface"]["group1_after_forms_not_stated"] == [] and C["powder_surface"]["newly_group4_or_other"] == {}
    for k in ("frozen_66", "out_of_sample"):
        assert C[k]["unexplained"] == [] and C[k]["abstain_to_4"] == [] and C[k]["changed"] == []
    assert C["drift"]["differences"] == {}
