"""Source-backed naming only. Synthetic conditioned controls are not accuracy data."""
import csv
from pathlib import Path
import pytest
from foodscan.normalise import normalise_ingredient
from foodscan.pipeline import analyse_text
from foodscan.classify import lexicon
R=Path(__file__).resolve().parents[1]
ALIASES={r['from']:r['to'] for r in csv.DictReader((R/'evaluation/scoped_powder_5/aliases.csv').open())}
FORMS=['{t}','Raw {t}','Roasted {t}','Boiled {t}','Salted {t}','Sugared {t}','{t} (salt)','{t} (sugar)','{t} (honey)','{t} (brine)','{t} (corn oil)','{t} (XQ9)','{t} (sugar, XQ9)','{t} (no added salt, sugar)','{t} (Rice)','{t} (Milk)','{t} (Milk Powder)','{t} (Whole Milk Powder)','{t} (Cashew Nuts)','{t} powder','100% {t} powder','Whole {t} powder','{t} powder (100% Rice)','{t} powder (Whole Rice)','{t} (Banana Powder)','100% {t} (Banana Powder)','{t} (100% Banana Powder)','{t} (dried)','{t} (canned)','{t} (no added salt)','{t} milk','{t} oil','{t} butter','{t} apple','{t} tree','{t} sprout','x{t}','{t}x','Rice, {t}','{t}, Maltodextrin','Milk ({t})','Almonds ({t})','{t} (modified)','{t} (pregelatinized)','{t} (flavour)','{t} powder (maltodextrin)','{t} (salt free, sugar)','Protein Rich {t}','Durum {t}']

def result(t):
 a=analyse_text('Ingredients: '+t+'.',source='text')
 return (a.answered,a.group if a.answered else None,a.completeness['status'])

@pytest.mark.parametrize('alias',ALIASES)
def test_plain_name_is_same_food_and_group1(alias):
 target=ALIASES[alias]
 assert normalise_ingredient(alias).name==normalise_ingredient(target).name
 assert result(alias)[1]==1

@pytest.mark.parametrize('alias',ALIASES)
@pytest.mark.parametrize('form',FORMS)
def test_naming_does_not_change_target_form_policy(alias,form):
 assert result(form.format(t=alias))==result(form.format(t=ALIASES[alias]))

@pytest.mark.parametrize('alias',['garbanzo bean','garbanzo beans'])
def test_no_unsourced_chickpea_flour_to_besan_chain_is_added(alias):
 # Existing chickpea-flour alias provenance is a separate unresolved issue.
 # Do not make a new alias chain or force a positive merely for equality.
 assert result(alias+' flour')[1] is None

@pytest.mark.parametrize('t',['cashew apple','cashew tree','cashew oil','cashew milk','cashew butter','cashew flour','pistachio tree','pistachio oil','pistachio milk','pistachio butter','pistachio flour','Protein Rich Maida','Protein Prachur Maida','Durum Maida','xmaida','maidax','xcashew','cashewx'])
def test_no_new_derivative_plant_part_qualified_flour_or_substring_placement(t):
 assert result(t)[1] not in [1,2,3]


def test_canonical_names_remain_idempotent():
 for t in lexicon():
  assert normalise_ingredient(t).name==t


def test_exact_seven_names_only():
 assert ALIASES=={'maida':'refined wheat flour','garbanzo bean':'chickpea','garbanzo beans':'chickpea','cashew':'cashew nuts','cashews':'cashew nuts','pistachio':'pistachio nuts','pistachios':'pistachio nuts'}


def test_known_cashew_food_name_keeps_the_shared_salt_on_both_sides():
 from foodscan.pipeline import _split_amp_pair
 raw='Salted Almonds & Cashews'
 items,notes=_split_amp_pair(raw)
 assert items==['Salted Almonds','Salted Cashews'] and notes
 assert result(raw)[1]==3
 # Replacement negative retains the unknown-derivative boundary.
 assert _split_amp_pair('Salted Almonds & Cashew Milk')==(['Salted Almonds & Cashew Milk'],[])


def test_original_f07_maida_wordings_are_assessed_without_changing_group4():
 text=(R/'evaluation/dev_regression_15/inputs/F07.txt').read_text()
 a=analyse_text(text if text.lower().startswith('ingredients') else 'Ingredients: '+text,source='text')
 assert a.answered and a.group==4
 assert not any('maida' in u.lower() for u in a.unassessed)
 assert sum('maida' in t.lower() for t in a.ingredients)==2
