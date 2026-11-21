"""'&' pairs inside brackets (owner-approved candidate; SYNTHETIC cases + the owner's acceptance label). Both sides must be recognised WITH their shared modifier;
recognised-but-unplaced sides give recognition only (classification stays unresolved); the shared percentage is a note, never copied onto the items."""
from __future__ import annotations

import pytest

from foodscan.pipeline import _split_amp_pair, analyse_text

LABEL = ("Ingredients: Multigrain Flour Blend (45.7%) [Sprouted Ragi & Jowar (23.4%), Rice & Oat (22.3%)], Whole Milk Powder (29.5%), Date Powder (9%), Banana Powder, Strawberry Powder (5%), "
         "Skimmed Milk Powder, Vitamins and Minerals, Beetroot Powder, Antioxidant (Natural Tocopherol).")


def test_synthetic_the_shared_modifier_is_attached_to_both_sides_never_a_bare_second_side():
    items, notes = _split_amp_pair("Sprouted Ragi & Jowar (23.4%)")
    assert items == ["Sprouted Ragi", "Sprouted Jowar"] and "Jowar" not in items
    assert any('"Sprouted" was read as shared' in n for n in notes)


def test_synthetic_the_shared_percentage_is_a_note_not_copied_onto_each_item():
    items, notes = _split_amp_pair("Rice & Oat (22.3%)")
    assert items == ["Rice", "Oat"] and not any("%" in i for i in items)
    assert any("22.3%" in n and "applies to the pair, not to each item separately" in n for n in notes)


@pytest.mark.parametrize("raw", ["Sprouted Ragi & Oat", "Fermented Ragi & Oat", "Spices & Condiments", "Palm & Palmolein", "Rice & Oat (Organic)", "Rice & Oat & Wheat", "Rice and Oat", "Salted Almonds & Cashews"])
def test_synthetic_negative_controls_stay_whole(raw):
    assert _split_amp_pair(raw) == ([raw], [])


def test_synthetic_a_shared_modifier_with_an_unrecognised_modified_form_stays_whole():
    assert _split_amp_pair("Sprouted Ragi & Oat")[0] == ["Sprouted Ragi & Oat"]          # 'sprouted oat' is not in the vocabulary, so the pair is not split
    assert _split_amp_pair("Fermented Ragi & Oat")[0] == ["Fermented Ragi & Oat"]


def test_synthetic_roasted_rice_and_oat_splits_only_because_roasted_oat_IS_recognised_through_the_roasted_descriptor():
    items, _ = _split_amp_pair("Roasted Rice & Oat")
    assert items == ["Roasted Rice", "Roasted Oat"]                                      # recorded: the owner's example assumed 'roasted oat' unrecognised; it is recognised (descriptor), so the split is correct


def test_synthetic_conditioned_forms_keep_their_condition_on_both_sides_after_the_split():
    items, _ = _split_amp_pair("Salted Almonds & Pumpkin Seeds")
    assert items == ["Salted Almonds", "Salted Pumpkin Seeds"]                           # never a bare 'Pumpkin Seeds'


def test_synthetic_a_split_of_unplaced_sides_is_recognition_only_the_list_still_abstains():
    a = analyse_text("Ingredients: Blend [Sprouted Ragi & Jowar (23.4%), Salt].", source="text")
    assert not a.answered and [u.lower() for u in a.unplaced] == ["sprouted ragi", "sprouted jowar"] and "recognised by name only" in a.reason
    assert not any("%" in u for u in a.unplaced)


def test_synthetic_a_split_of_two_placed_foods_classifies_them_as_the_foods_they_are():
    a = analyse_text("Ingredients: Blend [Rice & Oat (22.3%), Salt].", source="text")
    assert a.answered and a.group == 3 and not a.unassessed[1:]


def test_owner_acceptance_label_only_the_blend_group_name_is_left_unassessed_and_it_still_abstains():
    a = analyse_text(LABEL, source="text")
    assert not a.answered and a.unassessed == ["Multigrain Flour Blend (45.7%) (group name; its contents were assessed separately)"]
    assert [u.lower() for u in a.unplaced] == ["sprouted ragi", "sprouted jowar", "vitamins", "minerals"] and "antioxidant" in a.reason.lower()
    assert sum("applies to the pair" in w for w in a.warnings) == 2
