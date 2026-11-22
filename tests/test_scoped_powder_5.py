"""Private experimental powder controls. Not a release verdict."""
import pytest
from foodscan.pipeline import analyse_text
from foodscan.classify import lexicon

NUTS=[r['term'] for r in lexicon().values() if r['kind']=='nut_seed']
HEADS=['Cashew Nuts','Pistachio Nuts','Chickpea','Semolina','Suji','Mango']

def a(text):
    return analyse_text('Ingredients: '+text+'.',source='text')

def g(text):
    x=a(text)
    return x.group if x.answered else None

@pytest.mark.parametrize('term',NUTS)
@pytest.mark.parametrize('form',['{t} powder','{t} (powder)','Whole {t} (Banana Powder)','100% {t} (Banana Powder)','{t} (Banana Powder, 100% Rice)'])
def test_no_borrowed_composition(term,form):
    assert g(form.format(t=term)) is None

@pytest.mark.parametrize('term',NUTS)
@pytest.mark.parametrize('form',['100% {t} powder','Whole {t} powder','{t} (100% powder)','{t} (Milk Powder)','{t} (100% Banana Powder)','{t} (Banana Powder (100%))','{t} (Rice)','{t} (Vitamins, Minerals)'])
def test_existing_positive_forms_and_child_own_evidence(term,form):
    assert g(form.format(t=term))==1

@pytest.mark.parametrize('term',NUTS)
@pytest.mark.parametrize('form',['Salted {t} powder','{t} powder (Salt)','{t} powder (Sugar)'])
def test_supported_salted_sugared_forms_keep_priority(term,form):
    assert g(form.format(t=term))==3

@pytest.mark.parametrize('head',HEADS)
@pytest.mark.parametrize('child',['Banana Powder','Spinach Powder','Cashew Nuts Powder'])
def test_nested_powder_without_own_evidence_abstains(head,child):
    assert g(f'{head} ({child})') is None
    assert g(f'100% {head} ({child})') is None

@pytest.mark.parametrize('head',HEADS)
@pytest.mark.parametrize('child',['100% Banana Powder','Whole Spinach Powder','100% Cashew Nuts Powder'])
def test_nested_own_evidence_is_preserved(head,child):
    assert g(f'{head} ({child})')==1

@pytest.mark.parametrize('head',['Cashew Nuts','Pistachio Nuts','Semolina','Suji'])
def test_named_milk_powder_exception_does_not_turn_the_parent_into_a_powder(head):
    assert g(f'{head} (Milk Powder)')==1
    assert g(f'{head} (Whole Milk Powder)')==1

@pytest.mark.parametrize('text',['Cashew Nuts Powder (XQ9)','Semolina (Banana Powder, XQ9)','Cashew Nuts (Sprouted Ragi)','100% Cashew Nuts (Banana Powder, Whole Rice)'])
def test_unknown_or_sibling_proof_does_not_launder_the_child(text):
    assert g(text) is None

@pytest.mark.parametrize('text',['Cashew Nuts (Banana Powder), Maltodextrin','Cashew Nuts Powder (Maltodextrin)','Semolina (Banana Powder), Maltodextrin'])
def test_strong_marker_still_decides(text):
    assert g(text)==4

@pytest.mark.parametrize('text',[
    'Cashew Nuts (Sunflower Oil Powder (100%))',
    'Cashew Nuts (100% Mango (Banana Powder))',
    'Cashew Nuts (Whole Mango (Banana Powder))',
    'Semolina (Whole Mango (Banana Powder))',
    'Cashew Nuts (Banana Powder (Salt), 100% Rice)',
    'Semolina (Banana Powder (Salt), Whole Rice)',
    'Cashew Nuts [Banana Powder {Salt}, 100% Rice]',
    'Cashew Nuts (Banana Powder and 100% Rice)',
    'Cashew Nuts (Banana Powder & Whole Rice)',
    'Cashew Nuts (Banana Powder; 100% Rice)',
])
def test_deeper_child_or_sibling_composition_cannot_escape(text):
    assert g(text) is None

@pytest.mark.parametrize('text',[
    'Cashew Nuts (100% Banana Powder)',
    'Cashew Nuts (Banana Powder (100%))',
    'Cashew Nuts [Banana Powder {100%}]',
])
def test_child_own_composition_survives_nested_syntax(text):
    assert g(text)==1


def test_deeper_positive_composition_is_not_rejected_by_the_new_check():
    from foodscan.classify import nested_powder_unresolved
    from foodscan.normalise import normalise_ingredient
    text='Cashew Nuts (Whole Mango (100% Banana Powder))'
    assert nested_powder_unresolved(normalise_ingredient(text))==[]
    # Existing flattened bracket recognition still abstains on this shape.
    # This patch does not widen that older parser/recognition behavior.
    assert g(text) is None


def test_raw_split_preserves_which_item_owns_a_percentage():
    from foodscan.classify import raw_bracket_parts
    assert raw_bracket_parts('Cashew Nuts (Banana Powder (100%), Rice)')==['Banana Powder (100%)','Rice']
    assert raw_bracket_parts('Cashew Nuts [Banana Powder {Salt, Rice}, Milk Powder]')==['Banana Powder {Salt, Rice}','Milk Powder']
    assert raw_bracket_parts('Cashew Nuts (Banana Powder and Rice)')==['Banana Powder','Rice']
    assert raw_bracket_parts('Cashew Nuts (Banana Powder (Salt, Rice), Milk Powder')==['Banana Powder (Salt, Rice)','Milk Powder']

@pytest.mark.parametrize('term',NUTS+['Banana','Spinach','Chickpea'])
@pytest.mark.parametrize('child',['100% Rice','Whole Rice','100% Milk Powder','Whole Milk Powder'])
def test_an_actual_powder_cannot_borrow_its_childs_composition(term,child):
    assert g(f'{term} Powder ({child})') is None

@pytest.mark.parametrize('head',['Mango','Chickpea','Carrot','Cashew Nuts','Pistachio Nuts','Semolina'])
@pytest.mark.parametrize('child',['Milk Powder','Whole Milk Powder','100% Milk Powder','Milk Powder (100%)'])
def test_named_child_is_not_mistaken_for_the_parents_form(head,child):
    assert g(f'{head} ({child})')==1

@pytest.mark.parametrize('term',NUTS)
@pytest.mark.parametrize('child',['Milk','Milk Powder'])
def test_explicit_whole_nut_powder_does_not_misread_a_milk_child_as_a_fat_grade(term,child):
    assert g(f'Whole {term} Powder ({child})')==1

@pytest.mark.parametrize('text',[
    'Banana Powder (100%)','Banana Powder (100.0%)','Banana Powder [100%]',
    'Banana Powder (whole)','Whole Banana Powder','100% Banana Powder (Rice)',
])
def test_supported_own_claims_are_retained(text):
    assert g(text)==1

@pytest.mark.parametrize('term',NUTS+['Banana','Spinach','Chickpea'])
@pytest.mark.parametrize('form',['{t} Powder (100% {t})','{t} Powder (Whole {t})','{t} Powder ({t} 100%)'])
def test_explicit_same_food_composition_is_not_misread_as_a_different_child(term,form):
    assert g(form.format(t=term))==1

@pytest.mark.parametrize('term',['Banana Powder','Date Powder','Strawberry Powder','Beetroot Powder'])
@pytest.mark.parametrize('form',['{t} (100% {t})','{t} (Whole {t})','{t} ({t} 100%)'])
def test_same_named_powder_composition_is_retained(term,form):
    assert g(form.format(t=term))==1
