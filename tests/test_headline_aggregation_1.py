"""headline-aggregation-1 (SYNTHETIC). An abstention headed by weak or unlisted markers, a colour note or a sweetener-foods entry also names the other ACTIVE blockers (items not in the vocabulary, recognised-by-name-only
items no source places, the powder of a food or of an oil or fat without a stated composition), without repeating the item the headline already names. No group changes; strong-marker precedence and existing abstentions are untouched.
The UI already lists unplaced and unassessed items below the headline; this only makes the one-line reason complete. Set-aside group names are metadata and are not blockers here."""
from __future__ import annotations

from foodscan.pipeline import analyse_text


def run(t):
    return analyse_text(f"Ingredients: {t}.", source="text")


MULTI = "Multigrain Blend (Sprouted Ragi & Jowar (23.4%), Wheat), Vitamins, Minerals, Antioxidant (INS 320), Edible Vegetable Oil"


def test_synthetic_the_multigrain_headline_names_the_unplaced_items_as_well_as_the_weak_marker():
    a = run(MULTI)
    assert a.group is None and a.reason.startswith("only weak or unlisted markers present (Antioxidant (INS 320)")
    assert "; other open items: recognised by name only, no source read places Sprouted Ragi, Sprouted Jowar, Vitamins, Minerals" in a.reason
    assert "Multigrain Blend" not in a.reason.split("other open items")[1] and "not in the local vocabulary" not in a.reason.split("other open items")[1]


def test_synthetic_nothing_is_appended_when_there_is_no_other_blocker():
    assert run("Wheat, Antioxidant (INS 320)").reason.endswith("not enough to call a group")


def test_synthetic_powders_and_vocabulary_gaps_are_named():
    assert "a powder is named without a stated composition: Spinach Powder" in run("Spinach Powder, Antioxidant (INS 320)").reason
    assert "a powder is named without a stated composition: Sunflower Oil Powder" in run("Sunflower Oil Powder, Antioxidant (INS 320)").reason
    assert "not in the local vocabulary: Xyzzy" in run("Turmeric (Colouring & Spices), Xyzzy").reason


def test_synthetic_the_weak_marker_item_is_not_repeated_as_unrecognised():
    assert "not in the local vocabulary: Antioxidant" not in run("Wheat, Xyzzy, Antioxidant (INS 320)").reason
    assert "not in the local vocabulary: Xyzzy" in run("Wheat, Xyzzy, Antioxidant (INS 320)").reason


def test_synthetic_strong_markers_and_plain_abstentions_keep_their_reasons():
    a = run("Rice, Colour (INS 150d)")
    assert a.group == 4 and a.reason is None
    assert run("Vitamins, Minerals").group is None and "other open items" not in (run("Vitamins, Minerals").reason or "")
