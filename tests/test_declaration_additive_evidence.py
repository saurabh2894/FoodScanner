import pytest
from foodscan.pipeline import analyse_text
@pytest.mark.parametrize('entry',['Stabilizer (INS 999)','INS 999','Raising Agent (INS 500(ii))','Preservative (INS 211)','INS 102'])
def test_positive_declaration_blocks_unsupported_plain_food_answer(entry):
 a=analyse_text('Ingredients: Milk. Contains '+entry+'.',source='text')
 assert a.group is None
 assert a.ins_mappings
 assert a.declared
@pytest.mark.parametrize('claim',['Contains no Stabilizer (999)','May contain INS 999','No added preservative (211)','Contains milk','Contains wheat','Contains 37% millets'])
def test_denied_or_allergen_claim_does_not_add_evidence(claim):
 a=analyse_text('Ingredients: Milk. '+claim+'.',source='text')
 assert a.group==1 and not a.ins_mappings

def test_independent_marker_still_decides():
 assert analyse_text('Ingredients: Milk, maltodextrin. Contains INS 999.',source='text').group==4
