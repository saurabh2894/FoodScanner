"""Extract only literal codes after already-existing direct additive-class aliases."""
import pytest
from foodscan.normalise import extract_ins, normalise_list
from foodscan.pipeline import analyse_text
@pytest.mark.parametrize('term,codes',[
 ('Stabilizer',['414']),('Stabilizers',['414']),('Stabilizing Agent',['414']),
 ('Color',['150d']),('Synthetic Food Color',['102']),('Flavor Enhancers',['627','631']),
 ('Emulsifying Agent',['322']),('Raising Agents',['500(ii)']),('Acidity Regulators',['339(ii)'])])
def test_direct_existing_class_alias_literal_codes(term,codes):
 suffix=', '.join(codes);raw=f'{term} ({suffix})';clean,uses=extract_ins(raw)
 assert [u.code for u in uses]==codes
 assert normalise_list([raw])[0].raw==raw
@pytest.mark.parametrize('term',['Salt','Milk','Sugar','Soy','Colorful','Stabilizerx','Maltodextrin'])
def test_non_classes_do_not_gain_bare_codes(term):
 assert extract_ins(term+' (414)')[1]==[]
@pytest.mark.parametrize('raw',['Stabilizer (41O)','Color (15Od)','Stabilizer (414mg)','Stabilizer (4 14)'])
def test_no_guessed_or_unit_codes(raw):
 assert extract_ins(raw)[1]==[]
@pytest.mark.parametrize('raw',['Ingredients: Sugar. Contains no Color (102).','Ingredients: Sugar. No added Stabilizer (414).','Ingredients: Sugar. Nutrition Information: Color (102).'])
def test_denied_or_negated_tail_not_promoted(raw):
 a=analyse_text(raw);assert not a.ins_mappings

def test_unmapped_code_does_not_gain_placement():
 a=analyse_text('Ingredients: Milk, Stabilizer (999).');assert a.group is None
 assert [u.code for u in a.ins_mappings]==['999']

@pytest.mark.parametrize('term',['Color','Colour','Stabilizer','Stabiliser','Emulsifiers','Flavor Enhancers'])
@pytest.mark.parametrize('shape',['no added {} (102)','without {} (102)','free from {} (102)','{} (102) free','{} (102) not used','no added {} (INS 102)'])
def test_item_absence_claim_is_visible_but_not_positive(term,shape):
 raw=shape.format(term);a=analyse_text('Ingredients: Milk, '+raw+'.',source='text')
 assert a.group is None
 assert raw in a.ingredients
 assert not a.ins_mappings
 assert not a.drivers

@pytest.mark.parametrize('s',['Milk, no added Color (102), maltodextrin','Milk, no added Color (102), Color (110)','Milk, Color (102), no added Color (110)'])
def test_absence_claim_does_not_suppress_independent_positive_marker(s):
 a=analyse_text('Ingredients: '+s+'.',source='text');assert a.group==4
 assert all('no added' not in d.ingredient for d in a.drivers)
 assert all(u.code!='110' or 'no added' not in u.ingredient for u in a.ins_mappings)

@pytest.mark.parametrize('s',['salted','sugared','brined','powdered','dried','roasted'])
def test_conditioned_positive_alias_not_suppressed(s):
 a=analyse_text('Ingredients: '+s+' Milk, Color (102).',source='text');assert a.group==4
 assert [u.code for u in a.ins_mappings]==['102']

@pytest.mark.parametrize('term,code',[('Stabilizer','102'),('Stabiliser','102'),('Color','211'),('Colour','211')])
@pytest.mark.parametrize('prefix',['','INS ','E'])
@pytest.mark.parametrize('tail',[False,True])
def test_code_class_mismatch_stays_visible_unresolved(term,code,prefix,tail):
 raw=term+' ('+prefix+code+')'
 text='Ingredients: Milk'+('. Contains 'if tail else ', ')+raw+'.'
 a=analyse_text(text,source='text')
 assert a.group is None
 assert [u.code for u in a.ins_mappings]==[code]
 assert a.ins_mappings[0].class_conflict
 assert any('mapping differ' in w for w in a.warnings)
 assert not any('INS '+code+' (' in d.detail for d in a.drivers)

@pytest.mark.parametrize('tail',[False,True])
def test_independent_positive_entry_survives_code_conflict(tail):
 text='Ingredients: Milk'+('. Contains 'if tail else ', ')+'Color (211), sweetener (950).'
 assert analyse_text(text,source='text').group==4

def test_mixed_code_entry_does_not_show_usable_marker_for_its_other_code():
 a=analyse_text('Ingredients: Milk, Color (102, 211).',source='text')
 assert a.group is None
 assert [u.code for u in a.ins_mappings]==['102','211']
 assert all(u.class_conflict for u in a.ins_mappings)
