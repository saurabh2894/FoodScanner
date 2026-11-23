"""Current-source synthetic controls, not photo OCR or label-accuracy evidence."""
from pathlib import Path
import json
import pytest
from foodscan.pipeline import analyse_text
from foodscan.normalise import normalise_ingredient
from foodscan.classify import lookup
ROOT=Path(__file__).resolve().parent.parent
M=json.loads((ROOT/'evaluation/nalt_names_13/admission.json').read_text())
ALIASES=[(a['name'],a['target']) for a in M['aliases']]
NAMES=[r['term'] for r in M['new_foods']]
FORMS=['{t}','Raw {t}','Fresh {t}','Frozen {t}','Dried {t}','Roasted {t}','Salted {t}','Sugared {t}','{t} (Salt)','{t} (Sugar)','{t} (Brine)','{t} (XQ9)','{t} powder','100% {t} powder','Whole {t} powder','{t} powder (100% Rice)','{t} powder (Sugar)','{t} butter','{t} flour','{t} oil','{t} extract','{t} juice','{t} solids','{t} protein isolate','Mango ({t} Powder)','Mango (100% {t} Powder)','Cashew Nuts ({t} Powder)','Cashew Nuts (100% {t} Powder)','{t} (Milk Powder)','{t} (Banana Powder)','{t} (100% Rice, Banana Powder)','Hydrogenated {t}','Interesterified {t}','{t} (Rice)','{t} (Palm, Salt)']
def result(t):
 a=analyse_text('Ingredients: '+t+'.',source='text')
 return a.group if a.answered else None

@pytest.mark.parametrize('name',NAMES)
@pytest.mark.parametrize('form',['{t}','Raw {t}','Fresh {t}','Frozen {t}','Dried {t}','Roasted {t}'])
def test_new_plain_food_and_named_minimal_processes(name,form):
 assert result(form.format(t=name))==1

@pytest.mark.parametrize('name',NAMES)
@pytest.mark.parametrize('form',['Salted {t}','{t} (Salt)','{t} (Sugar)','{t} (Brine)','{t}, Salt','{t}, Sugar'])
def test_new_food_item_own_additions_are_group_three_not_plain_food(name,form):
 assert result(form.format(t=name))==3

@pytest.mark.parametrize('name',NAMES)
@pytest.mark.parametrize('form',['Sugared {t}','Brined {t}','Canned {t}','{t} (Canned)','Oil Roasted {t}','{t} powder','{t} powder (100% Rice)','100% {t} (Banana Powder)','{t} extract','{t} oil','{t} butter','{t} flour','{t} juice','{t} (XQ9)'])
def test_unproved_products_and_borrowed_composition_remain_abstentions(name,form):
 assert result(form.format(t=name)) is None

@pytest.mark.parametrize('name',[n for n in NAMES if True])
@pytest.mark.parametrize('form',['100% {t} powder','Whole {t} powder','{t} powder (100% {t})'])
def test_explicit_same_food_only_powder_keeps_named_grinding_scope(name,form):
 assert result(form.format(t=name))==1

@pytest.mark.parametrize('name',NAMES)
def test_existing_protein_isolate_marker_remains_a_separate_marker(name):
 assert result(name+' protein isolate')==4

@pytest.mark.parametrize('name',M['held'])
def test_no_other_prior_hold_is_lifted(name):
 if name in ['celery', 'scallions', 'spring onions']:
  assert result(name)==1  # Independently sourced slice14 lift; older manifest retained.
  return
 assert result(name) is None

@pytest.mark.parametrize('name',['swiss chard','groundnut oil','flaxseed oil','coconut oil','sunflower oil','soybean oil','corn oil','portabella mushrooms','crimini mushrooms','lettuce','tomato'])
def test_existing_supported_names_keep_their_normalisation_and_group(name):
 assert normalise_ingredient(name).name==name
 assert result(name)==(2 if name.endswith('oil') else 1)



@pytest.mark.parametrize('name',NAMES+[a['name'] for a in M['aliases']])
@pytest.mark.parametrize('form',['{t} sprouts','{t} leaves','{t} straw','{t} hulls','{t} forage','{t} hay','{t} silage','100% {t} leaves powder','100% {t} straw powder','100% {t} hulls powder','100% {t} forage powder'])
def test_seed_pod_admission_does_not_admit_unreviewed_plant_parts_or_feed(name,form):
 assert result(form.format(t=name)) is None

@pytest.mark.parametrize('name,target',ALIASES)
@pytest.mark.parametrize('form',FORMS)
def test_exact_name_aliases_keep_canonical_result_and_conditions(name,target,form):
 assert result(form.format(t=name))==result(form.format(t=target))

def test_identity_sources_do_not_silently_assert_whole_pulse_equals_split_dal():
 assert len(M['new_foods'])==6 and len(M['aliases'])==2
 assert all(a['target'] not in ['moong dal','urad dal','pigeon peas','snap beans'] for a in M['aliases'])
 for row in M['new_foods']:
  assert row['inference_level'].startswith('class-instance')
  assert 'not named' in row['source'] and 'Not a strong marker' in row['source']

@pytest.mark.parametrize('name',NAMES)
def test_canonical_spelling_is_not_corrupted(name):
 assert normalise_ingredient(name).name==name
