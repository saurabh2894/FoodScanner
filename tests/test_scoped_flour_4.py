"""Synthetic controls for the scoped flour condition correction.

Plain and minimally processed flour, the existing salted-grain positives and
raw Group 1 mixtures are retained. No new Group 3 placement is introduced.
"""
import pytest
from foodscan.classify import lexicon, _SCOPED_TERMS
from foodscan.pipeline import analyse_text

FLOURS = [r['term'] for r in lexicon().values() if r['kind'] == 'flour']
SALTED = [t for t in FLOURS if t in _SCOPED_TERMS['toasted']]
UNSCOPED_SALT = [t for t in FLOURS if t not in SALTED]


def result(text):
    return analyse_text('Ingredients: ' + text + '.', source='text')


def group(text):
    a = result(text)
    return a.group if a.answered else None


@pytest.mark.parametrize('term', FLOURS)
@pytest.mark.parametrize('form', ['{t} (sugar)', '{t} (sunflower oil)', '{t} (Mango, Sugar)',
    '{t} (canned)', '{t} (preserved)', '{t} (honey)', '{t} (brine)'])
def test_added_or_unresolved_preserved_form_cannot_borrow_plain_flour_group1(term, form):
    a = result(form.format(t=term))
    assert not a.answered and 'added or preserving condition' in a.reason


@pytest.mark.parametrize('term', UNSCOPED_SALT)
@pytest.mark.parametrize('form', ['Salted {t}', '{t} (salt)', '{t} (Sea Salt)'])
def test_salt_outside_existing_bounded_positive_scope_does_not_borrow_plain_group1(term, form):
    assert group(form.format(t=term)) is None


@pytest.mark.parametrize('term', FLOURS)
@pytest.mark.parametrize('form', ['{t}', 'Unsalted {t}', '{t} (no added salt)',
    '{t} (no added sugar)', '{t} (Rice)', '{t} (Mango)', '{t} (Milk)',
    '{t} (Sugar Apples)', '{t} (Vitamins, Minerals)'])
def test_plain_source_supported_routes_and_raw_food_mixtures_stay_group1(term, form):
    assert group(form.format(t=term)) == 1


@pytest.mark.parametrize('term', [t for t in FLOURS if t != 'split pulse urad flour'])
@pytest.mark.parametrize('form', ['{t} powder', '100% {t} powder'])
def test_previously_recognised_flour_powder_names_are_unchanged(term, form):
    assert group(form.format(t=term)) == 1


@pytest.mark.parametrize('text', ['split pulse urad flour powder', '100% split pulse urad flour powder'])
def test_existing_unrecognised_compound_flour_powder_names_are_not_forced_positive(text):
    assert group(text) is None


@pytest.mark.parametrize('term', SALTED)
@pytest.mark.parametrize('form', ['Salted {t}', '{t} (salt)', '{t} (Sea Salt)',
    '{t} (Rice, Salt)', '{t} (Salt, Sugar)', '{t} (Rice, Salt, Sugar)'])
def test_existing_source_supported_group3_routes_are_not_regressions(term, form):
    assert group(form.format(t=term)) == 3


@pytest.mark.parametrize('term', FLOURS)
@pytest.mark.parametrize('form', ['{t} (XQ9)', '{t} (Sugar, XQ9)', '{t} (Sprouted Ragi)',
    '{t} (Corn Starch)', '{t} (Salt, Corn Starch)', '{t}, Salt', '{t}, Sugar'])
def test_existing_uncertain_forms_remain_uncertain(term, form):
    assert group(form.format(t=term)) is None


@pytest.mark.parametrize('term', FLOURS)
@pytest.mark.parametrize('form', ['{t} (sugar), Maltodextrin', '{t} (canned), Maltodextrin'])
def test_strong_marker_keeps_priority(term, form):
    assert group(form.format(t=term)) == 4


def test_no_pending_alias_is_accidentally_released():
    assert group('Maida') is None
    assert group('Cashew') is None
    assert group('Pistachio') is None
    assert group('Garbanzo Bean') is None
