"""Existing real pasted evidence plus synthetic boundary/false-positive controls."""
from pathlib import Path
import pytest
from foodscan.pipeline import analyse_text
from foodscan.parser import suspect_adjacent_class_items

ROOT=Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('text',[
 'Mixed Spices (Clove, Cinnamon, Chilli) Preservative (INS 211)',
 'Rice (Rice) Colour (INS 102)',
 'Spices [Clove, Cinnamon] preservative (INS 211)',
])
def test_adjacent_food_and_class_brackets_are_uncertain_without_inventing_split(text):
 a=analyse_text('Ingredients: '+text+'.',source='text')
 assert a.completeness['status']=='uncertain'
 assert any('ingredient-item boundaries are uncertain' in r for r in a.completeness['reasons'])
 assert a.ingredients==[text]
 assert a.completeness['words']['unaccounted']==0
 assert any('original item is kept unchanged' in w for w in a.warnings)

@pytest.mark.parametrize('text',[
 'Rice (Rice), Preservative (INS 211)',
 'Spices (Pepper Preservative (INS 211))',
 'Stabilizer (INS 414) Preservative (INS 211)',
 'Stabiliser (INS 414) Preservative (INS 211)',
 'Emulsifying Agent (INS 322) Preservative (INS 211)',
 'Rice (Rice) (100%)',
 'Rice (Rice) as colouring',
 'Mixed Spices (Clove, Cinnamon, Chilli)',
 'Rice (Rice) with salt (1%)',
 'Rice (Rice) and Preservative (INS 211)',
 'Rice (Rice) Preservative free (claim)',
 'Rice (Rice) Natural Flavour (vanilla)',
])
def test_nested_or_explicitly_separated_or_role_wording_not_flagged(text):
 assert not suspect_adjacent_class_items([text])


def test_real_m12_words_and_original_merged_item_are_preserved():
 text=(ROOT/'evaluation/fresh_batch_2/inputs/M12.txt').read_text()
 a=analyse_text(text,source='text')
 assert a.group==4
 assert 'MIXED SPICES (CLOVE, CINNAMON, CHILLI) PRESERVATIVE (INS 211)' in a.ingredients
 assert a.completeness['status']=='uncertain' and a.completeness['words']['unaccounted']==0
 assert any('ingredient boundary may be missing' in w for w in a.warnings)


def test_boundary_signal_does_not_change_classifier_outcome():
 a=analyse_text('Ingredients: Rice (Rice) Colour (INS 102).',source='text')
 assert a.group==4 and any('colour' in d.detail.lower() for d in a.drivers)
