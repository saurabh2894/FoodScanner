"""Failure-1 fix (corrective release). Scope of the declared-colour marker, research/04.

1. A whole spice or whole food carrying a colour FUNCTION NOTE is never read as a declared added colour.
2. An explicitly declared added colour still counts as the marker.
3. Butter plus a declared colour returns the documented provisional result (Group 4 on the declared colour).
Provisional: nothing here claims annatto is unsafe or that the product's health effects are established.
"""
import pytest

from foodscan.pipeline import analyse_text


def a(t):
    return analyse_text(t, source="text")


def colour_driver(r):
    return any('"colour"' in d.detail or 'statement: "colour"' in d.detail for d in r.drivers)


# ---- 1. function note on a whole food: not a marker ------------------------------------------------------------------
@pytest.mark.parametrize("text", [
    "Ingredients: Rice flakes, roasted gram, ground spices & condiments (iodised salt, red chilli, turmeric (colouring & spices), cumin).",
    "Ingredients: Rice, salt, turmeric (colour).",
    "Ingredients: Rice, salt, turmeric (colouring & spices).",
    "Ingredients: Rice, salt, beetroot powder (for natural colours).",
    "Ingredients: Milk fat, salt, annatto (colour).",
    "Ingredients: Rice, salt, paprika (natural colour).",
    # wording variants on a named whole food or spice
    "Ingredients: Rice, salt, turmeric (as colourant).",
    "Ingredients: Rice, salt, turmeric (as colouring).",
    "Ingredients: Rice, salt, turmeric (for colour).",
    "Ingredients: Rice, salt, turmeric (colour & spices).",
    "Ingredients: Rice, salt, turmeric (natural colour).",
    "Ingredients: Rice, salt, turmeric (colouring agent).",
    "Ingredients: Rice, salt, turmeric (used as a colourant).",
    "Ingredients: Rice, salt, paprika (as colorant).",
    "Ingredients: Rice, salt, turmeric (as coloring).",
])
def test_colour_function_note_on_a_whole_food_is_not_a_declared_colour(text):
    r = a(text)
    assert not colour_driver(r), text
    assert r.group != 4, text                      # never a confident Group 4 from the note alone
    assert not r.answered, text                    # conservative: uncertain unless an independent marker decides (Group 3 from the foods alone is not given)
    assert "colour note" in r.reason, text
    assert any("not counted as an added colour" in w for w in r.warnings), text      # and the note is shown, not silently dropped


@pytest.mark.parametrize("note", ["as colourant", "as colouring", "for colour", "colour & spices", "natural colour", "colouring agent"])
def test_note_variants_do_not_cancel_or_replace_independent_decisions(note):
    # an independent strong marker still gives Group 4, and the note is still reported
    r = a(f"Ingredients: Rice, salt, turmeric ({note}), added flavour.")
    assert r.group == 4 and not colour_driver(r) and any('"flavour"' in d.detail for d in r.drivers)
    assert any("not counted as an added colour" in w for w in r.warnings)
    # a separately declared colour elsewhere still counts
    r = a(f"Ingredients: Rice, salt, turmeric ({note}), colour (INS 150d).")
    assert r.group == 4 and colour_driver(r)
    # a weak marker is not independent evidence: the result stays uncertain
    r = a(f"Ingredients: Rice, salt, turmeric ({note}), raising agent (INS 500(ii)).")
    assert not r.answered


def test_turmeric_note_plus_colour_on_a_contains_line_still_counts_the_declaration():
    for note in ("colouring & spices", "as colourant"):
        r = a(f"Ingredients: Rice, salt, turmeric ({note}). Contains permitted natural colour.")
        assert r.group == 4 and colour_driver(r), note
        # the declared colour is not "in the list": the note on turmeric does not count as the ingredient-list colour
        assert any(d["text"].lower().find("colour") >= 0 and not d["in_list"] for d in r.declared), note
        assert any("not counted as an added colour" in w for w in r.warnings), note


def test_annatto_colour_abstains_by_deliberate_choice():
    # Documented choice (research/04), no special case: a function note on a head that is not in the vocabulary stays uncertain
    # and visible under "Not assessed"; it is not promoted to a declared added colour.
    r = a("Ingredients: Milk fat, salt, annatto (colour).")
    assert not r.answered and any("annatto" in u.lower() for u in r.unassessed)
    assert any("not counted as an added colour" in w for w in r.warnings)


def test_the_note_is_reported_not_silently_dropped():
    r = a("Ingredients: Rice, salt, turmeric (colouring & spices).")
    assert any("not counted as an added colour" in w for w in r.warnings)


def test_unknown_head_with_a_colour_note_stays_uncertain_and_visible():
    r = a("Ingredients: Milk fat, salt, annatto (colour).")
    assert not r.answered and any("annatto" in u.lower() for u in r.unassessed)


def test_other_markers_still_decide_when_a_colour_note_is_present():
    r = a("Ingredients: Rice, salt, turmeric (colouring & spices), added flavour.")
    assert r.group == 4 and not colour_driver(r) and any('"flavour"' in d.detail for d in r.drivers)


# ---- 2. an explicitly declared added colour still counts -------------------------------------------------------------
@pytest.mark.parametrize("text", [
    "Ingredients: Sugar, food colour - E122.",
    "Ingredients: Rice, salt, colour (INS 150d).",
    "Ingredients: Rice, salt, natural colour (annatto).",
    "Ingredients: Rice, colours (INS 150a, INS 150d), salt.",
    "Ingredients: Rice, spices & condiments (salt, colour (INS 150d)).",       # colour inside a compound's list
    "Ingredients: Rice, spices (salt, natural colour, cumin).",
    "Ingredients: Rice, salt. Contains permitted natural colour.",             # Contains declaration
])
def test_declared_added_colour_still_counts(text):
    r = a(text)
    assert r.group == 4 and colour_driver(r), text


def test_a_note_on_one_ingredient_does_not_cancel_a_declared_colour_elsewhere():
    r = a("Ingredients: Rice, salt, turmeric (colouring & spices), natural colour (annatto).")
    assert r.group == 4 and colour_driver(r)


# ---- 3. butter + declared colour: the documented provisional result ----------------------------------------------------
def test_butter_with_a_declared_colour_gives_the_documented_provisional_result():
    for t in ("Ingredients: Butter, salt, colour (INS 160b annatto).", "Ingredients: Milk fat, salt, natural colour (annatto)."):
        r = a(t)
        assert r.group == 4 and colour_driver(r), t


def test_plain_and_salted_butter_do_not_trigger_the_marker():
    for t in ("Ingredients: Butter.", "Ingredients: Butter, salt.", "Ingredients: Milk fat, salt."):
        assert not colour_driver(a(t)), t
