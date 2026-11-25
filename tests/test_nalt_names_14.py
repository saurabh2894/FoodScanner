"""Current-source synthetic controls, not photo OCR or label-accuracy evidence."""
from pathlib import Path
import json
import pytest
from foodscan.pipeline import analyse_text
from foodscan.normalise import normalise_ingredient
from foodscan.classify import lookup
ROOT=Path(__file__).resolve().parent.parent
M=json.loads((ROOT/'evaluation/nalt_names_14/admission.json').read_text())
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
 if name in ['greengram', 'blackgram', 'mungo beans', 'mungobeans', 'catjang peas', 'haricot beans', 'mungbeans', 'urd beans']:
  assert result(name)==1  # Source-backed slice13 lift; historical manifest retained.
  return
 assert result(name) is None

@pytest.mark.parametrize('name',['swiss chard','groundnut oil','flaxseed oil','coconut oil','sunflower oil','soybean oil','corn oil','portabella mushrooms','crimini mushrooms','lettuce','tomato'])
def test_existing_supported_names_keep_their_normalisation_and_group(name):
 assert normalise_ingredient(name).name==name
 assert result(name)==(2 if name.endswith('oil') else 1)



@pytest.mark.parametrize('name,target',ALIASES)
@pytest.mark.parametrize('form',FORMS)
def test_exact_name_aliases_keep_target_conditions(name,target,form):
 assert result(form.format(t=name))==result(form.format(t=target))

@pytest.mark.parametrize('name',NAMES)
def test_canonical_spelling_is_not_corrupted(name):
 assert normalise_ingredient(name).name==name

@pytest.mark.parametrize('name',['sugar beet','sugar beets','forage beets','celery salt'])
@pytest.mark.parametrize('form',['{t}','100% {t} powder','{t} powder','{t} (Sugar)'])
def test_unreviewed_crop_recipe_and_feed_names_stay_abstentions(name,form):
 assert result(form.format(t=name)) is None

def test_leaf_source_correction_is_a_leafy_vegetable_not_a_starchy_root_claim():
 row=lookup('beet greens')
 assert row['kind']=='vegetable' and 'Source-only correction' in row['source']
 assert result('beet greens')==1
 assert len(M['new_foods'])==5 and len(M['aliases'])==1
 assert not any(a['name']=='spring onions' for a in M['aliases'])

@pytest.mark.parametrize('name',NAMES)
@pytest.mark.parametrize('part',['straw','hay','silage','forage','flowers','roots','seeds'])
def test_independent_food_heads_do_not_grant_unreviewed_plant_parts(name,part):
 assert result(name+' '+part) is None

def test_celery_leaves_are_an_independently_sourced_positive_not_a_generic_part_exception():
 assert result('celery leaves')==1
 assert result('celery stalks')==1
 assert result('celery leaves powder') is None
 assert result('100% celery leaves powder')==1

@pytest.mark.parametrize('text,expected',[
 ('beetroot powder powder',None),('100% beetroot powder powder',1),
 ('Whole beetroot powder powder',1),('beetroot powder powder (Sugar)',3),
 ('beetroot powder powder (100% Rice)',None),
 ('beetroot powder powder (100% beetroot powder)',None),
 ('Mango (beetroot powder Powder)',None),('Mango (100% beetroot powder Powder)',1),
 ('Mango (forage beets Powder)',None),('Mango (100% sugar beets Powder)',None),
 ('beetroot',1),('beets',None),('beetroots',1)  # beetroot-24: label 'beetroot' staged (CoFID 13-164); 'beets' stays out
 ,('red beets',None),
 ('beetroot powder',None),('100% beetroot powder',1),
 ('whole beetroot powder',1),('beetroot powder (Sugar)',None)])
def test_narrow_food_names_preserve_the_older_beetroot_powder_surface(text,expected):
 assert result(text)==expected

@pytest.mark.parametrize('name',['beets','beetroots','red beets','beetroot','beet red','beetroot red'])
@pytest.mark.parametrize('form',['{t}','{t} powder','100% {t} powder','Whole {t} powder','Mango (100% {t} Powder)'])
def test_held_beet_food_colour_collision_is_not_forced_into_a_plain_food(name,form):
 expected=1 if name in {'beetroot','beetroots'} and form in ['{t}','100% {t} powder','Whole {t} powder','Mango (100% {t} Powder)'] else None  # beetroot-24: bare label now a row
 assert result(form.format(t=name))==expected  # Existing explicit beetroot-powder routes stay supported; no new root head.
