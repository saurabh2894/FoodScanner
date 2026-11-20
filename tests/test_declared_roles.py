"""Declared role of an additive code (roles.py): read from the SCANNED label's own wording for the entry, never from the code.
Role-scoped wording cites the NOVA method text that was read (FAO 2019, Monteiro et al.). Display only: no classification depends on it."""
import pytest

from foodscan import roles
from foodscan.pipeline import analyse_text


def a(t):
    return analyse_text(t, source="text")


def use(text, code):
    return next(u for u in a(text).ins_mappings if u.code == code)


def test_declared_class_is_shown_per_label_wording():
    u = use("Ingredients: Water, Sugar, Acidity Regulator (INS 330), Antioxidant (INS 392).", "330")
    assert u.declared == "Acidity Regulator" and u.declared_roles == ("acidity regulator",)
    assert u.role_notes[0] == 'Declared on the label as: "Acidity Regulator".'
    assert use("Ingredients: Water, Sugar, Acidity Regulator (INS 330), Antioxidant (INS 392).", "392").declared_roles == ("antioxidant",)


def test_same_code_two_labels_two_declared_classes():
    t1 = use("Ingredients: Rice, salt, Thickeners (INS 508).", "508")
    t2 = use("Ingredients: Rice, salt, Salt substitute (INS 508).", "508")
    t3 = use("Ingredients: Rice, salt, Acidity Regulator (INS 508).", "508")
    assert t1.declared_roles == ("thickener",) and t2.declared_roles == ("salt substitute",) and t3.declared_roles == ("acidity regulator",)
    assert t1.role_notes != t2.role_notes != t3.role_notes


def test_codes_whose_label_declares_no_class_stay_bare():
    u = use("Ingredients: Rice, salt, Potassium chloride (INS 508).", "508")
    assert u.declared is None and u.declared_roles == () and u.role_notes == [] and u.role_label is None
    assert u.ref_name == "Potassium chloride"          # name from the JECFA page, effect unknown


def test_preservative_and_antioxidant_get_the_role_scoped_no_marker_wording_with_source():
    for text, role in [("Ingredients: Water, Preservative (INS 211).", "preservative"), ("Ingredients: Water, Antioxidant (INS 300).", "antioxidant")]:
        u = a(text).ins_mappings[0]
        note = u.role_notes[-1]
        assert note.startswith(f"Declared as {role}: no Group 4 marker detected for this role per Monteiro et al. 2019, FAO")
        assert "does not by itself separate the groups" in note       # the source mentions these additives in Group 3 and in the Group 4 definition
        assert "never" not in note.lower()


def test_unsupported_classes_never_get_the_no_marker_wording():
    for cls in ["Acidity Regulator", "Stabilizer", "Anticaking Agent", "Raising Agent", "Salt substitute"]:
        u = a(f"Ingredients: Water, {cls} (INS 330).").ins_mappings[0]
        assert u.declared_roles, cls
        assert not any("no Group 4 marker detected" in n for n in u.role_notes), cls
        assert any("not named in the NOVA source read" in n for n in u.role_notes), cls


def test_classes_the_source_lists_for_group_4_say_so_and_state_what_this_tool_does():
    t = use("Ingredients: Rice, Thickeners (INS 508).", "508")
    assert "lists thickeners among the additive classes of ultra-processed foods" in t.role_notes[-1]
    assert "does not count this class as a marker yet" in t.role_notes[-1]       # honest about the gap: classification unchanged
    c = use("Ingredients: Rice, Colour (INS 150d).", "150d")
    assert "lists colours among the additive classes" in c.role_notes[-1] and "counts that class on the label as a Group 4 marker" in c.role_notes[-1]


def test_shared_entry_does_not_claim_a_role_per_code():
    us = a("Ingredients: Milk, Emulsifier & Stabilizers [INS 471, INS 407, INS 412].").ins_mappings
    assert {u.code for u in us} == {"471", "407", "412"}
    for u in us:
        assert u.declared_roles == ("emulsifier", "stabiliser")
        assert any("share this entry" in n for n in u.role_notes)


def test_filler_words_around_the_class_do_not_hide_it():
    assert a("Ingredients: Water, Food Colour (INS 150d).").ins_mappings[0].declared_roles == ("colour",)
    assert a("Ingredients: Water, Class II Preservative (INS 211).").ins_mappings[0].declared_roles == ("preservative",)
    assert a("Ingredients: Water, Natural and Synthetic Food Colours (INS 150d, INS 122).").ins_mappings[0].declared_roles == ("colour",)


@pytest.mark.parametrize("text", [
    "Ingredients: Water, Sugar, Acidity Regulator (INS 330), Preservative (INS 211).",
    "Ingredients: Rice, salt, Thickeners (INS 508).",
    "Ingredients: Rice, salt, Salt substitute (INS 508).",
    "Ingredients: Milk, Emulsifier & Stabilizers [INS 471, INS 407, INS 412].",
    "Ingredients: Potato, oil, salt, Antioxidant (INS 392), Acidity Regulator (INS 330).",
    "Ingredients: Water, Sugar, Colour (INS 150d), Flavour.",
    "Ingredients: Refined wheat flour, Raising agents [INS 500(ii), INS 503(ii)], Stabilizer (INS 440).",
    "Ingredients: Water, Sugar, Class II Preservative (INS 211). Contains Permitted Natural Colour (INS 150d).",
])
def test_declared_roles_change_no_classification(text, monkeypatch):
    before = a(text)
    monkeypatch.setattr(roles, "declared_roles", lambda name: ())
    from foodscan import normalise
    monkeypatch.setattr(normalise, "_declared_roles", lambda name: ())
    after = a(text)
    assert (before.answered, before.group, before.reason) == (after.answered, after.group, after.reason)
    assert [(d.ingredient, d.detail) for d in before.drivers] == [(d.ingredient, d.detail) for d in after.drivers]
