"""Source-grounded N09 composition metadata, no dairy vocabulary admission."""
from pathlib import Path
import pytest
from foodscan.pipeline import analyse_text
from foodscan.parser import parse_ingredient_list

ROOT = Path(__file__).resolve().parents[1]
N09 = (ROOT / 'evaluation/fresh_batch_1/inputs/N09.txt').read_text()


def test_n09_actual_record_keeps_composition_visible_without_inventing_an_ingredient():
    a = analyse_text(N09, source='text')
    assert a.group == 1
    assert a.ingredients == ['Pasteurized Buffalo Milk']
    assert any('Fat 6.00% Min., SNF 9.00% Min.' in w and 'composition declaration' in w for w in a.warnings)
    assert any('PROVISIONAL' in d.source for d in a.drivers)
    assert a.completeness['words']['unaccounted'] == 0
    assert a.completeness['words']['composition'] == 8
    assert a.completeness['words']['excluded'] == 0
    assert any('may be PROVISIONAL' in w for w in a.warnings)
    assert a.extracted_text == N09


def test_pack_line_break_does_not_have_to_be_fabricated_to_fix_n09():
    t = 'Ingredients:\nPasteurized Buffalo Milk\nFat6.00%Min., SNF9.00%Min.\nAllergen Information: Contains Milk'
    a = analyse_text(t, source='text')
    assert a.group == 1
    assert any('Fat6.00%Min., SNF9.00%Min.' in w for w in a.warnings)


@pytest.mark.parametrize('body', [
    'Pasteurized Buffalo Milk Fat 6.00% Min.',
    'Pasteurized Buffalo Milk SNF 9.00% Min.',
    'Pasteurized Buffalo Milk, Milk Fat 6.00% Min., SNF 9.00% Min.',
    'Pasteurized Buffalo Milk Fat 6.00% Min., SNF 9.00% Min., Vitamin A',
    'Pasteurized Buffalo Milk Fat 6.00% Min., SNF 9.00% Min. Vitamin A',
    'Pasteurized Buffalo Milk Fat 6.00% Min., SNF 9.00% Min., Milk Solids',
    'Rice Fat 6.00% Min., SNF 9.00% Min.',
    'Pasteurized Buffalo Milk (Fat 6.00% Min., SNF 9.00% Min.)',
    'Milk Fat 6%, SNF 9%',
])
def test_not_a_generic_fat_nutrient_or_ingredient_cutoff(body):
    p = parse_ingredient_list('Ingredients: ' + body)
    assert p.composition == []
    assert not analyse_text('Ingredients: ' + body, source='text').answered


def test_marker_after_pair_not_lost():
    a = analyse_text('Ingredients: Pasteurized Buffalo Milk Fat 6.00% Min., SNF 9.00% Min. Contains added flavour.', source='text')
    assert a.group == 4 and any('flavour' in d.ingredient.lower() for d in a.drivers)


def test_n08_actual_record_stays_unresolved_not_starter_synonym():
    a = analyse_text((ROOT / 'evaluation/fresh_batch_1/inputs/N08.txt').read_text(), source='text')
    assert a.group is None
    assert any('Probiotic Culture' in u for u in a.unassessed)


def test_native_template_metadata_role_and_item_count():
    from foodscan.web.app import create_app
    from flask import render_template
    with create_app().app_context():
        h = render_template('index.html', result=analyse_text(N09, source='text'), error=None)
    assert '8 identified as milk-composition metadata' in h
    assert '0 of 1 items' in h
    assert 'built-in method' not in h
