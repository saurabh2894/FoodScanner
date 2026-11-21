"""Tests for Task 16: Bounded multigrain parser repair.

Covers:
1. Footnote handling:
   - Trailing marks (#, ##, *, **, dagger, double dagger, observed OCR closing quote U+201D).
   - Adjacent to spaces, commas, percentages, and brackets.
   - Quoted phrases ('"Natural Flavour"', '“Natural Flavour”') preserved without false footnote inference.
   - Raw ingredient text preserved for audit while normalized name resolves cleanly.
2. Bracketed pair connectors:
   - Support 'and' in addition to '&' in _split_amp_pair.
   - Culinary blend guards: 'Corn and Canola Oil' in and outside brackets, and with shared percentage.
   - Positive counterpart: 'Rice and Sunflower Oil' splits.
   - Unknown second terms stay whole.
   - Non-recognized shared modifiers stay whole.
   - More than two sides stay whole.
   - Shared additive code lists stay whole.
   - Negations stay whole.
   - Non-percentage bracket details stay whole.
   - Connector fidelity in notes ('and' vs '&').
3. Multi-path acceptance:
   - Original literal, browser OCR text, and normalized variant agree on recognized ingredients.
   - Group abstains honestly (group is None).
   - Vitamins and minerals remain unplaced.
   - Sprouted grains remain unplaced.
   - Parent compound is metadata in unassessed, not unknown ingredient blocker.
"""
from __future__ import annotations

import pytest

from foodscan.normalise import normalise_ingredient, strip_footnotes
from foodscan.pipeline import _split_amp_pair, analyse_text

LITERAL_LABEL = (
    "Ingredients: Multigrain Flour Blend (45.7%) [Sprouted Ragi & Jowar (23.4%), Rice & Oat (22.3%)], "
    "Whole Milk Powder (29.5%), Date Powder (9%), Banana Powder, Strawberry Powder (5%), "
    "Skimmed Milk Powder, Vitamins# and Minerals##, Beetroot Powder, Antioxidant (Natural Tocopherol)."
)

OCR_LABEL = (
    "INGREDIENTS\n\n"
    "Multigrain Flour Blend (45.7%) [Sprouted Ragi &\n"
    "Jowar (23.4%), Rice & Oat (22.3%)], Whole Milk\n"
    "Powder (29.5%), Date Powder (9%), Banana\n"
    "Powder, Strawberry Powder (5%), Skimmed Milk\n"
    "Powder, Vitamins” and Minerals** , Beetroot\n"
    "Powder, Antioxidant (Natural Tocopherol).\n\n"
    "THIS PRODUCT CONTAINS 23% MILLETS\n"
    "Contains Milk & Oats. Made in a facility that\n"
    "also processes Soy, Wheat & Nuts. May contain\n"
    "trace elements.\n"
)

NORMALIZED_LABEL = (
    "Ingredients: Multigrain Flour Blend (45.7%) [Sprouted Ragi & Jowar (23.4%), Rice & Oat (22.3%)], "
    "Whole Milk Powder (29.5%), Date Powder (9%), Banana Powder, Strawberry Powder (5%), "
    "Skimmed Milk Powder, Vitamins and Minerals, Beetroot Powder, Antioxidant (Natural Tocopherol)."
)


# =============================================================================
# 1. Footnote handling unit tests
# =============================================================================

@pytest.mark.parametrize(
    "raw,expected_clean",
    [
        ("Vitamins#", "Vitamins"),
        ("Minerals##", "Minerals"),
        ("Salt*", "Salt"),
        ("Sugar**", "Sugar"),
        ("Iron†", "Iron"),
        ("Zinc‡", "Zinc"),
        ("Vitamins”", "Vitamins"),
        ("Minerals”", "Minerals"),
        ("Vitamins #", "Vitamins"),
        ("Minerals ##", "Minerals"),
        ("Salt *", "Salt"),
        ("Sugar **", "Sugar"),
        ("Iron †", "Iron"),
        ("Zinc ‡", "Zinc"),
        ("Vitamins ”", "Vitamins"),
    ],
)
def test_strip_footnotes_individual_marks(raw: str, expected_clean: str):
    assert strip_footnotes(raw) == expected_clean


def test_strip_footnotes_adjacent_to_percentages_and_brackets():
    assert strip_footnotes("Date Powder (9%)*") == "Date Powder (9%)"
    assert strip_footnotes("Salt* (1%)") == "Salt (1%)"
    assert strip_footnotes("[Sprouted Ragi* & Jowar** (23.4%)]") == "[Sprouted Ragi & Jowar (23.4%)]"


def test_strip_footnotes_preserves_quoted_phrases():
    # Quoted text representing names or descriptors should not be stripped of quotes
    assert strip_footnotes('"Natural Flavour"') == '"Natural Flavour"'
    assert strip_footnotes('“Natural Flavour”') == '“Natural Flavour”'
    assert strip_footnotes("'Vanilla'") == "'Vanilla'"


def test_normalise_ingredient_preserves_raw_and_strips_footnotes_in_clean():
    ing = normalise_ingredient("Vitamins#")
    assert ing.raw == "Vitamins#"
    assert ing.text == "vitamins"
    assert ing.name == "vitamins"

    ing_ocr = normalise_ingredient("Vitamins”")
    assert ing_ocr.raw == "Vitamins”"
    assert ing_ocr.text == "vitamins"
    assert ing_ocr.name == "vitamins"

    ing_star = normalise_ingredient("Minerals**")
    assert ing_star.raw == "Minerals**"
    assert ing_star.text == "minerals"
    assert ing_star.name == "minerals"


# =============================================================================
# 2. Bracketed pair connectors ('and' & '&') and guard conditions
# =============================================================================

def test_split_amp_pair_with_and_connector():
    items, notes = _split_amp_pair("Rice and Oat (22.3%)")
    assert items == ["Rice", "Oat"]
    assert any("and" in n for n in notes)
    assert not any("&" in n for n in notes)
    assert any("22.3%" in n for n in notes)


def test_split_amp_pair_shared_modifier_with_and():
    items, notes = _split_amp_pair("Sprouted Ragi and Jowar (23.4%)")
    assert items == ["Sprouted Ragi", "Sprouted Jowar"]
    assert any('"Sprouted" was read as shared by both sides of "Sprouted Ragi and Jowar"' in n for n in notes)
    assert any("23.4%" in n for n in notes)


def test_split_amp_pair_connector_fidelity_in_notes():
    _, notes_and = _split_amp_pair("Sprouted Ragi and Jowar (23.4%)")
    assert any('of "Sprouted Ragi and Jowar"' in n for n in notes_and)

    _, notes_amp = _split_amp_pair("Sprouted Ragi & Jowar (23.4%)")
    assert any('of "Sprouted Ragi & Jowar"' in n for n in notes_amp)


def test_culinary_guard_corn_and_canola_oil():
    # Inside brackets without percentage
    items, notes = _split_amp_pair("Corn and Canola Oil")
    assert items == ["Corn and Canola Oil"]
    assert notes == []

    # Inside brackets with shared percentage
    items, notes = _split_amp_pair("Corn and Canola Oil (20%)")
    assert items == ["Corn and Canola Oil (20%)"]
    assert notes == []

    # Inside brackets with ampersand and percentage
    items, notes = _split_amp_pair("Corn & Canola Oil (20%)")
    assert items == ["Corn & Canola Oil (20%)"]
    assert notes == []

    # Outside brackets in analyse_text stays whole and abstains
    a_out = analyse_text("Ingredients: Corn and Canola Oil, Salt.", source="text")
    assert "Corn and Canola Oil" in a_out.unassessed

    # Inside compound bracket in analyse_text stays whole
    a_in = analyse_text("Ingredients: Blend [Corn and Canola Oil (20%), Salt].", source="text")
    assert any("Corn and Canola Oil" in u for u in a_in.unassessed)


def test_rice_and_sunflower_oil_contrast():
    # Rice is not an oil row ('rice oil' does not exist in lexicon)
    # Inside brackets: splits into Rice and Sunflower Oil
    items, notes = _split_amp_pair("Rice and Sunflower Oil")
    assert items == ["Rice", "Sunflower Oil"]

    # In compound bracket
    a = analyse_text("Ingredients: Blend [Rice and Sunflower Oil, Salt].", source="text")
    # Rice and Sunflower Oil are recognised and assessed
    assert "Rice" in a.ingredients or any("rice" in i.lower() for i in a.ingredients)
    assert "Sunflower Oil" in a.ingredients or any("sunflower oil" in i.lower() for i in a.ingredients)


def test_synthetic_guards_stay_whole():
    # Unknown second term
    assert _split_amp_pair("Sprouted Ragi and UnknownGrain (23.4%)") == (["Sprouted Ragi and UnknownGrain (23.4%)"], [])

    # Non-recognized shared modifier
    assert _split_amp_pair("UnknownMod Ragi and Jowar (23.4%)") == (["UnknownMod Ragi and Jowar (23.4%)"], [])

    # More than two sides
    assert _split_amp_pair("Ragi and Jowar and Oat (20%)") == (["Ragi and Jowar and Oat (20%)"], [])
    assert _split_amp_pair("Ragi & Jowar & Oat (20%)") == (["Ragi & Jowar & Oat (20%)"], [])

    # Shared additive code lists
    assert _split_amp_pair("Emulsifiers and Stabilizers [INS 460(i), INS 471]") == (["Emulsifiers and Stabilizers [INS 460(i), INS 471]"], [])

    # Negations
    assert _split_amp_pair("No Added Sugar and Salt") == (["No Added Sugar and Salt"], [])

    # Non-percentage bracket details
    assert _split_amp_pair("Sprouted Ragi and Jowar (organic)") == (["Sprouted Ragi and Jowar (organic)"], [])


# =============================================================================
# 3. Acceptance agreement across literal, OCR, and normalized variants
# =============================================================================

def test_acceptance_literal_ocr_and_normalized_agree_on_recognition():
    res_literal = analyse_text(LITERAL_LABEL, source="text")
    res_ocr = analyse_text(OCR_LABEL, source="ocr")
    res_norm = analyse_text(NORMALIZED_LABEL, source="text")

    # 1. None should force a NOVA group (abstains honestly)
    assert not res_literal.answered and res_literal.group is None
    assert not res_ocr.answered and res_ocr.group is None
    assert not res_norm.answered and res_norm.group is None

    # 2. All should agree on the resolved unplaced vocabulary entries
    for res in (res_literal, res_ocr, res_norm):
        resolved_unplaced = sorted(normalise_ingredient(u).name for u in res.unplaced)
        assert resolved_unplaced == ["minerals", "sprouted jowar", "sprouted ragi", "vitamins"]

    # Raw text preserves original tokens for audit
    assert "Vitamins#" in res_literal.unplaced
    assert "Minerals##" in res_literal.unplaced
    assert "Vitamins”" in res_ocr.unplaced
    assert "Minerals**" in res_ocr.unplaced
    assert "Vitamins" in res_norm.unplaced
    assert "Minerals" in res_norm.unplaced

    # 3. Both shared percentages remain pair context in warnings, never copied onto items
    for res in (res_literal, res_ocr, res_norm):
        pct_notes = [w for w in res.warnings if "applies to the pair" in w]
        assert len(pct_notes) == 2
        assert any("23.4%" in w for w in pct_notes)
        assert any("22.3%" in w for w in pct_notes)
        # Verify percentages are not on unplaced items
        assert not any("%" in u for u in res.unplaced)

    # 4. Expanded parent compound is metadata in unassessed, not unknown blocker
    for res in (res_literal, res_ocr, res_norm):
        assert any("Multigrain Flour Blend (45.7%) (group name" in u for u in res.unassessed)
        # Ensure Vitamins and Minerals are NOT in unassessed
        assert not any("vitamins" in u.lower() for u in res.unassessed)
        assert not any("minerals" in u.lower() for u in res.unassessed)
