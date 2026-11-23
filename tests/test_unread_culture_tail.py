"""Actual N08 OCR punctuation cannot silently exempt the unread cultures."""
from pathlib import Path
import pytest
from foodscan.pipeline import analyse_text, analyse_image
D=Path(__file__).parent/'fixtures/native_n08_readings'


def test_actual_native_second_reading_remains_visible_and_blocks_low_group():
    t=(D/'second.txt').read_text()
    a=analyse_text(t,source='ocr')
    assert not a.answered
    assert 'not read' in a.reason
    assert a.completeness['status']=='uncertain'
    assert any('Probiotic Culture' in x for x in a.ignored)
    assert a.ingredients==['Pasteurised Toned Milk']
    assert a.extracted_text==t


def test_default_actual_native_readings_still_abstain_without_selection_change():
    class Frozen:
        def extract_text(self,p):return (D/'first.txt').read_text()
        def extract_text_alt(self,p):return (D/'second.txt').read_text()
    a=analyse_image('unused',Frozen())
    assert not a.answered
    assert a.extracted_text==(D/'first.txt').read_text()


@pytest.mark.parametrize('tail',['Probiotic Culture.','Active Lactic Culture and Probiotic Culture.','Cultures (UnknownSpecies).'])
def test_unknown_culture_tail_not_classified_or_discarded(tail):
    a=analyse_text('Ingredients: Milk. '+tail,source='text')
    assert not a.answered and a.ignored==[tail]
    assert not any('starter' in d.detail for d in a.drivers)


@pytest.mark.parametrize('tail',['*Culture information.','Directions: add culture.','Serving suggestion: culture.'])
def test_explicit_noningredient_tail_exclusions_preserved(tail):
    a=analyse_text('Ingredients: Milk. '+tail,source='text')
    assert a.group==1


def test_group4_marker_stands_with_unread_tail_warning():
    a=analyse_text('Ingredients: Milk, flavour. Probiotic culture.',source='text')
    assert a.group==4
    assert a.completeness['status']=='uncertain'
    assert any('not read' in w for w in a.warnings)
