"""Current-source naming controls. Synthetic, not photo OCR or label-accuracy evidence."""
from pathlib import Path
import json
import pytest
from foodscan.pipeline import analyse_text
from foodscan.normalise import normalise_ingredient
from foodscan.classify import lookup
ROOT=Path(__file__).resolve().parent.parent
M=json.loads((ROOT/'evaluation/nalt_names_7/admission.json').read_text())
ALIASES=[(x['name'],x['target']) for x in M['aliases']]

def result(text):
    a=analyse_text('Ingredients: '+text+'.',source='text')
    return a.group if a.answered else None

@pytest.mark.parametrize('alias,target',ALIASES)
@pytest.mark.parametrize('form',[
'{t}','Raw {t}','Dried {t}','Roasted {t}','Salted {t}','{t} (Salt)','{t} (Sugar)','{t} (Brine)',
'{t} (XQ9)','{t} powder','100% {t} powder','{t} powder (100% Rice)','{t} powder (Sugar)',
'{t} butter','{t} flour','{t} oil','{t} extract','{t} juice','{t} solids','{t} protein isolate',
'Mango ({t} Powder)','Mango (100% {t} Powder)','Cashew Nuts ({t} Powder)','Cashew Nuts (100% {t} Powder)',
'{t} (Milk Powder)','{t} (Banana Powder)','{t} (100% Rice, Banana Powder)',
'Hydrogenated {t}','Interesterified {t}','{t} (Rice)','{t} (Palm, Salt)'])
def test_alias_inherits_target_not_extra_processing_or_composition_scope(alias,target,form):
    assert lookup(normalise_ingredient(alias).name)['term']==target
    assert result(form.format(t=alias))==result(form.format(t=target))

@pytest.mark.parametrize('name',['peanut','peanuts','groundnuts','ground nuts'])
@pytest.mark.parametrize('form',['{t}','Raw {t}','Fresh {t}','Dried {t}','Roasted {t}','Unsalted {t}','100% {t} powder','Whole {t} powder'])
def test_new_plain_ground_nut_food_and_named_minimal_processes(name,form):
    assert result(form.format(t=name))==1

@pytest.mark.parametrize('name',['peanut','peanuts','groundnuts','ground nuts'])
@pytest.mark.parametrize('form',['Salted {t}','{t} (Salt)','{t} (Sugar)','{t}, Salt','{t}, Sugar','{t} (Sunflower Oil)'])
def test_ground_nut_item_own_additions_are_not_group_one(name,form):
    assert result(form.format(t=name))==3

@pytest.mark.parametrize('name',['peanut','peanuts','groundnuts','ground nuts'])
@pytest.mark.parametrize('form',['{t} butter','{t} flour','{t} extract','{t} concentrate','{t} sauce','{t} powder','{t} powder (100% Rice)','100% {t} (Banana Powder)','Oil Roasted {t}','Honey Roasted {t}'])
def test_new_food_name_does_not_prove_a_derivative_or_borrowed_claim(name,form):
    assert result(form.format(t=name)) is None

@pytest.mark.parametrize('name',['ewe milk','ovine milk','caprine milk'])
@pytest.mark.parametrize('form',['{t} solids','{t} fat','{t} powder (100% Rice)','{t} powder (Sugar)','{t} (Sugar)'])
def test_species_milk_aliases_do_not_admit_fractions_or_unproved_composition(name,form):
    assert result(form.format(t=name)) is None

@pytest.mark.parametrize('name',['copra oil','maize oil','grape seed oil','soy oil','sunflower seed oil','sunflowerseed oil','linseed oil','flax seed oil','ground nut oil','butteroil','cacao butter'])
def test_oil_names_keep_group_two_and_unknown_or_food_bracket_guards(name):
    assert result(name)==2
    assert result(name+' (Salt)')==2  # FAO Table1 also includes products consisting of Group2 items.
    assert result(name+' (Milk)') is None
    assert result(name+' (XQ9)') is None
    assert result(name+' Powder') is None
    assert result('Hydrogenated '+name)==4

@pytest.mark.parametrize('name',['swiss chard','groundnut oil','flaxseed oil','coconut oil','sunflower oil','soybean oil'])
def test_short_suffix_and_nut_aliases_preserve_established_canonical_spelling(name):
    assert normalise_ingredient(name).name==name
    assert result(name)==(1 if name=='swiss chard' else 2)

@pytest.mark.parametrize('name',['chard','bovine milk','bovine milk solids','star anise','winter melon','haricot beans','catjang peas','mustard leave','cranberry','tamarind','coconut','celery','Oil Roasted Peanuts','Peanut Butter','Peanut Milk','Sugared Peanuts'])
def test_held_names_and_derivatives_are_not_lifted(name):
    if name in ['celery', 'scallions', 'spring onions']:
     assert result(name)==1  # Independently sourced slice14 lift; older manifest retained.
     return
    if name in ['greengram', 'blackgram', 'mungo beans', 'mungobeans', 'catjang peas', 'haricot beans', 'mungbeans', 'urd beans']:
     assert result(name)==1  # Source-backed slice13 lift; historical manifest retained.
     return
    assert result(name) is None


def test_current_source_record_keeps_identity_separate_from_nova():
    p=M['new_foods'][0]
    assert p['term']=='peanut' and p['kind']=='nut_seed'
    assert 'Nuts, peanuts, and other oilseeds without salt or sugar' in p['source'] and 'with no added salt or sugar' in p['source']
    assert 'milk solids' in M['rationale']['bovine milk']
    assert 'swiss swiss chard' in M['rationale']['chard']


@pytest.mark.parametrize('name',['peanut','peanuts','groundnuts','ground nuts'])
def test_existing_protein_isolate_marker_is_not_a_plain_food_route(name):
    # FAO Table1 Group4 names protein isolates. This marker predates this new food.
    assert result(name+' protein isolate')==4
