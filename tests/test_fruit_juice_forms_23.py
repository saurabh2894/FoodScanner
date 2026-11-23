"""Synthetic source-fit controls, not OCR/accuracy evidence."""
import pytest
from foodscan.pipeline import analyse_text
from foodscan.classify import lookup
from foodscan.normalise import normalise_ingredient

JUICES=['apple juice','grape juice','orange juice','pineapple juice']
FRUITS=['cranberry','cranberries','tamarind','tamarinds']
FORMS=['{t}','Fresh {t}','Pasteurized {t}','Pasteurised {t}','100% {t}','100% Fresh {t}','Fresh 100% {t}','100% Pasteurized {t}','100% Pasteurised {t}','{t} (100%)','100% Fresh {t} (100%)','100% Fresh {t} (Sugar)','100% Fresh {t} (100% Rice)','Dried {t}','Roasted {t}','Salted {t}','Powdered {t}','100% Powdered {t}','100% Fresh {t} powder','{t} concentrate','{t} nectar','{t} from concentrate','Milk ({t})','Mango ({t})','Mango (100% Fresh {t})','{t}, Sugar','100% Fresh {t}, Sugar','100% Fresh {t}, Water','100% Fresh {t}, Milk','100% Fresh {t}, 100% Fresh {t}','{t}, Flavour','{t}, INS 999','{t}, Maltodextrin','{t}, XQ9']

def result(t):
 a=analyse_text('Ingredients: '+t+'.',source='text')
 return a.group if a.answered else None

@pytest.mark.parametrize('name',JUICES)
@pytest.mark.parametrize('form',FORMS)
def test_juice_source_conditions_are_not_satisfied_by_name_or_other_items(name,form):
 expected=1 if form in ['100% Fresh {t}','Fresh 100% {t}','100% Pasteurized {t}','100% Pasteurised {t}'] else 4 if form in ['{t}, Flavour','{t}, Maltodextrin'] or (name=='apple juice' and form=='{t} concentrate') else None
 assert result(form.format(t=name))==expected

@pytest.mark.parametrize('name',JUICES)
def test_new_juice_name_is_distinct_from_base_fruit(name):
 assert lookup(normalise_ingredient(name).name)['kind']=='fruit_juice'

@pytest.mark.parametrize('t,expected',[('cranberry beans',1),('cranberry beans (Brine)',3),('lemon juice concentrate',4),('apple juice concentrate',4),('Milk',1),('Mango, Sugar',3)])
def test_existing_routes_remain(t,expected):
 assert result(t)==expected

@pytest.mark.parametrize('name',JUICES)
def test_bare_juice_is_visible_as_not_placed_even_when_independent_marker_decides(name):
 a=analyse_text('Ingredients: '+name+', Maltodextrin.',source='text')
 assert a.group==4 and name in a.unplaced and a.completeness['assessed']['not_assessed']==1
 a=analyse_text('Ingredients: '+name+'.',source='text')
 assert not a.answered and name in a.unplaced and name not in a.unassessed
 a=analyse_text('Ingredients: 100% Fresh '+name+'.',source='text')
 assert a.group==1 and not a.unplaced and a.completeness['assessed']['not_assessed']==0

@pytest.mark.parametrize('name',JUICES)
def test_weak_marker_reason_also_names_unresolved_juice(name):
 a=analyse_text('Ingredients: '+name+', Preservative (INS 211).',source='text')
 assert not a.answered and name in a.reason and name in a.unplaced
