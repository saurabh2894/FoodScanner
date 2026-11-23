"""Synthetic exact-source/form controls, not fresh label or OCR accuracy."""
import pytest
from foodscan.pipeline import analyse_text
from foodscan.classify import lookup
from foodscan.normalise import normalise_ingredient

FORMS = ['{t}', 'Plain {t}', 'Salted {t}', 'Sugared {t}', 'Sweetened {t}', 'Flavoured {t}', 'Flavored {t}', 'Powdered {t}', 'Dried {t}', 'Refined {t}', 'Fresh {t}', '100% {t}', '{t} (100%)', '{t} (Water)', '{t} (Sugar)', '{t} (Rice)', '{t}, Sugar', '{t}, Water', '{t}, Rice', '{t}, Flavour', '{t}, Maltodextrin', '{t}, INS 999', '{t}, Preservative (INS 211)', 'Milk ({t})', 'Mango ({t})', 'Rice ({t})', 'Rice (Milk ({t}))', 'Sugar ({t})', '{t} concentrate', '{t} powder']

def result(text):
    return analyse_text('Ingredients: '+text+'.', source='text')

@pytest.mark.parametrize('form',FORMS)
def test_water_exact_source_scope(form):
    a=result(form.format(t='Carbonated Water'))
    expected = 1 if form in ('{t}','Plain {t}') else 4 if form in ('{t}, Flavour','{t}, Maltodextrin') else None
    assert a.group == expected
    if expected == 1:
        assert not a.unplaced and a.completeness['assessed']['not_assessed']==0
        assert 'Khandpur' in a.drivers[0].source

@pytest.mark.parametrize('text',['Carbonated Water, Flavour','Carbonated Water, Maltodextrin'])
def test_existing_marker_priority_does_not_erase_water_scope_limit(text):
    a=result(text)
    assert a.group == 4 and 'Carbonated Water' in a.unplaced
    assert a.completeness['assessed']['not_assessed'] == 1

def test_weak_headline_names_water_scope():
    a=result('Carbonated Water, Preservative (INS 211)')
    assert not a.answered and 'named water' in a.reason and a.unplaced

def test_no_category_membership_expansion():
    for term in ['sparkling water','seltzer water','soda water','tonic water','carbonated drink','carbonating agent']:
        assert lookup(normalise_ingredient(term).name) is None
    assert lookup('carbonated water')['kind']=='named_water'
