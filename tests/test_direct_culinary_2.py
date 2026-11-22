"""Source-scoped culinary additions. Synthetic form tests, not market accuracy."""
import csv
from pathlib import Path
import pytest
from foodscan.pipeline import analyse_text
from foodscan.classify import lookup

ROOT=Path(__file__).resolve().parent.parent
TERMS=['corn starch','baking powder','baking soda','cornstarch','maize starch']
FORMS=[('{t}',2),('{t} (salt)',2),('{t} (sugar)',2),('{t} (XQ9)',None),('{t} (Rice)',None),('{t} (Mango, Sugar)',None),('{t} (Milk)',None),('100% {t} (Rice)',None),('{t}, Maltodextrin',4),('Wheat Flour ({t})',None),('Refined Wheat Flour ({t})',None),('Corn Oil ({t})',2),('{t} (Corn Oil)',2),('{t} (no added salt)',2)]

def g(text):
 a=analyse_text('Ingredients: '+text+'.',source='text')
 return a.group if a.answered else None

@pytest.mark.parametrize('term',TERMS)
@pytest.mark.parametrize('form,expected',FORMS)
def test_source_scoped_culinary_forms(term,form,expected):
 # Existing oil-powder caution remains in force, rather than invent a new exception.
 if form=='Corn Oil ({t})' and term=='baking powder':expected=None
 assert g(form.format(t=term))==expected

@pytest.mark.parametrize('term',['corn starch','cornstarch','maize starch'])
@pytest.mark.parametrize('source',['corn','maize'])
def test_closed_starch_source_identity(term,source):
 assert g(f'{term} ({source})')==2

@pytest.mark.parametrize('term',TERMS)
@pytest.mark.parametrize('form',['Modified {t}','{t} (modified)','{t} (pregelatinized)','{t} flour','{t} milk','{t} oil'])
def test_other_forms_do_not_borrow_plain_culinary_placement(term,form):
 assert g(form.format(t=term))!=2

def test_source_roles_and_exact_scope():
 rows=list(csv.DictReader((ROOT/'evaluation/direct_culinary_2/rows.csv').open()))
 assert {r['term'] for r in rows}=={'corn starch','baking powder','baking soda'}
 for r in rows:
  assert lookup(r['term'])['kind']=='culinary'
  assert 'placement clause:' in r['source']
  assert 'Naming only, not NOVA placement:' in r['source']
 assert 'class-instance' in lookup('corn starch')['source']
 assert 'exact-named' in lookup('baking powder')['source']
 assert g('Potato Starch') is None
