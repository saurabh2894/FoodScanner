"""Current-source synthetic controls, not photo OCR or label-accuracy evidence."""
from pathlib import Path
import json
import pytest
from foodscan.pipeline import analyse_text
from foodscan.normalise import normalise_ingredient
from foodscan.classify import lookup
ROOT=Path(__file__).resolve().parent.parent
M=json.loads((ROOT/'evaluation/nalt_names_10/admission.json').read_text())
ALIASES=[(a['name'],a['target']) for a in M['aliases']]
NAMES=[r['term'] for r in M['new_foods']]
FORMS=['{t}','Raw {t}','Fresh {t}','Frozen {t}','Dried {t}','Roasted {t}','Salted {t}','Sugared {t}','{t} (Salt)','{t} (Sugar)','{t} (Brine)','{t} (XQ9)','{t} powder','100% {t} powder','Whole {t} powder','{t} powder (100% Rice)','{t} powder (Sugar)','{t} butter','{t} flour','{t} oil','{t} extract','{t} juice','{t} solids','{t} protein isolate','Mango ({t} Powder)','Mango (100% {t} Powder)','Cashew Nuts ({t} Powder)','Cashew Nuts (100% {t} Powder)','{t} (Milk Powder)','{t} (Banana Powder)','{t} (100% Rice, Banana Powder)','Hydrogenated {t}','Interesterified {t}','{t} (Rice)','{t} (Palm, Salt)']
def result(t):
 a=analyse_text('Ingredients: '+t+'.',source='text')
 return a.group if a.answered else None

@pytest.mark.parametrize('alias,target',ALIASES)
@pytest.mark.parametrize('form',FORMS)
def test_name_does_not_invent_processing_or_composition_permission(alias,target,form):
 row=lookup(normalise_ingredient(alias).name)
 assert row and row['term']==target
 assert result(form.format(t=alias))==result(form.format(t=target))

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
 assert result(form.format(t=name))==(None if name in ['edible fungi','wild edible mushrooms'] else 1)

@pytest.mark.parametrize('name',NAMES)
def test_existing_protein_isolate_marker_remains_a_separate_marker(name):
 assert result(name+' protein isolate')==4

@pytest.mark.parametrize('name',[n for n in M['held'] if n not in ['dried vegetables','dehydrated vegetables']])
def test_no_other_prior_hold_is_lifted(name):
 if name in ['celery', 'scallions', 'spring onions']:
  assert result(name)==1  # Independently sourced slice14 lift; older manifest retained.
  return
 if name in ['greengram', 'blackgram', 'mungo beans', 'mungobeans', 'catjang peas', 'haricot beans', 'mungbeans', 'urd beans']:
  assert result(name)==1  # Source-backed slice13 lift; historical manifest retained.
  return
 assert result(name) is None

@pytest.mark.parametrize('name',['swiss chard','groundnut oil','flaxseed oil','coconut oil','sunflower oil','soybean oil','corn oil','portabella mushrooms','crimini mushrooms','lettuce','tomato'])
def test_existing_supported_names_keep_their_normalisation_and_group(name):
 assert normalise_ingredient(name).name==name
 assert result(name)==(2 if name.endswith('oil') else 1)

def test_source_record_separates_food_identity_from_placement():
 assert len(M['new_foods'])==4 and len(M['aliases'])==5
 for r in M['new_foods']:
  assert r['inference_level'].startswith('class-instance')
  assert 'not named' in r['source'] and 'not NOVA' in r['source'] and 'Not a strong marker' in r['source']


@pytest.mark.parametrize('name',[n for n in NAMES if True])
def test_stated_same_food_powder_plus_sugar_uses_source_backed_group_three(name):
 assert result(name+' Powder (Sugar)')==(None if name in ['edible fungi','wild edible mushrooms'] else 3)

def test_new_names_do_not_force_held_cashew_compounds_or_confections():
 assert result('Cashew Fruit') is None
 assert result('Cashew Apple') is None
 assert result('Truffles') is None
 assert normalise_ingredient('Cashew Fruit').name == 'cashew nuts fruit'

@pytest.mark.parametrize('name',NAMES)
def test_canonical_food_names_are_not_rewritten_by_shorter_aliases(name):
 assert normalise_ingredient(name).name == name
 assert result(name)==1

@pytest.mark.parametrize('name',['Green Leafy Vegetables','Leafy Greens','Leafy Green Vegetables','Fresh Greens','Salad Greens'])
def test_current_source_names_keep_plain_food_only_scope(name):
 assert result(name)==1
 assert result(name+' Extract') is None
 assert result(name+' powder') is None
