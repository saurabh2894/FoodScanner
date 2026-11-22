"""Narrow nested-vocabulary and intrinsic-food-name regression controls."""
import pytest
from foodscan.pipeline import analyse_text
from foodscan.classify import lookup


def a(text):
    return analyse_text('Ingredients: ' + text + '.', source='text')


def group(text):
    result = a(text)
    return result.group if result.answered else None


@pytest.mark.parametrize('head', ['Semolina', 'Suji', 'Rawa', 'Chickpea', 'Cashew Nuts',
    'Pistachio Nuts', 'Sugar Apples', 'Milk', 'Cilantro', 'Baking Powder', 'Corn Oil'])
@pytest.mark.parametrize('child', ['Sprouted Ragi', 'Sprouted Jowar'])
def test_recognition_only_grain_does_not_disappear_in_a_bracket(head, child):
    assert lookup(child.lower())['kind'] == 'unplaced'
    result = a(f'{head} ({child})')
    assert not result.answered
    assert any(child.lower() in item for item in result.unplaced)
    assert result.completeness['assessed']['not_assessed'] == 1


@pytest.mark.parametrize('head', ['Semolina', 'Suji', 'Cashew Nuts', 'Sugar Apples'])
@pytest.mark.parametrize('child', ['Sprouted Ragi', 'Sprouted Jowar'])
def test_strong_marker_still_decides_and_keeps_unplaced_visible(head, child):
    result = a(f'{head} ({child}), Maltodextrin')
    assert result.answered and result.group == 4
    assert any(child.lower() in item for item in result.unplaced)


@pytest.mark.parametrize('form', ['Sugar Apples', 'Sugar Apple', 'Raw Sugar Apples',
    'Sugar-apples (Rice)', 'Sugar-apples (Milk)', 'Sugar-apples (Cashew Nuts)',
    'Sugar-apples (Suji)', '100% Sugar-apples powder'])
def test_intrinsic_sugar_in_the_fruit_name_is_not_added_sugar(form):
    assert group(form) == 1


@pytest.mark.parametrize('form', ['Salted Sugar Apples', 'Sugar-apples (salt)',
    'Sugar-apples (sugar)', 'Sugar-apples (corn oil)',
    'Sugar-apples (no added salt, sugar)', 'Sugar-apples (salt free, sugar)',
    'Sugar-apples (sugar apples, sugar)'])
def test_actual_added_substances_on_the_fruit_are_not_exempted(form):
    assert group(form) == 3


@pytest.mark.parametrize('form', ['Sugar-apples powder', 'Sugar-apples (canned)',
    'Sugar-apples (XQ9)', 'Sugar Applesauce', 'Sugar Apple Juice'])
def test_other_fruit_forms_do_not_borrow_plain_fruit_placement(form):
    assert group(form) is None


@pytest.mark.parametrize('head', ['Cashew Nuts', 'Chickpea', 'Sugar Apples'])
@pytest.mark.parametrize('child', ['Rice', 'Milk', 'Cashew Nuts', 'Vitamins', 'Minerals',
    'Vitamins and Minerals'])
def test_source_supported_raw_mixtures_and_fortification_are_preserved(head, child):
    assert group(f'{head} ({child})') == 1


def test_existing_milk_and_starter_culture_route_is_preserved():
    assert group('Milk (Starter Culture)') == 1
