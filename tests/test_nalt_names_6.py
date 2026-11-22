"""Source-backed naming intake and inherited form conditions, not photo-OCR evidence."""
import importlib.util
import io
import json
from pathlib import Path
import pytest
from foodscan.classify import lookup
from foodscan.normalise import normalise_ingredient
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = json.loads((ROOT / 'evaluation/nalt_names_6/admission.json').read_text())
FOODS = [x['term'] for x in MANIFEST['new_foods']]
ALIASES = [(x['name'], x['targets'][0]) for x in MANIFEST['aliases']]

def answer(text):
    x = analyse_text('Ingredients: ' + text + '.', source='text')
    return x.group if x.answered else None

@pytest.mark.parametrize('term', FOODS)
@pytest.mark.parametrize('form', ['{t}', 'Fresh {t}', 'Raw {t}', 'Dried {t}', '100% {t} powder', 'Whole {t} powder'])
def test_admitted_plain_and_source_minimal_forms(term, form):
    assert answer(form.format(t=term)) == 1

@pytest.mark.parametrize('term', FOODS)
@pytest.mark.parametrize('form', ['Salted {t}', '{t} (Salt)', '{t} (Sugar)', '{t} (Brine)'])
def test_item_own_additions_never_take_plain_group_one(term, form):
    assert answer(form.format(t=term)) == 3

@pytest.mark.parametrize('term', FOODS)
@pytest.mark.parametrize('form', ['Canned {t}', 'Brined {t}', '{t} juice', '{t} milk', '{t} extract', '{t} puree', '{t} pulp', '{t} starch', '{t} sauce', '{t} concentrate', '{t} powder', '{t} powder (100% Rice)', '{t} (Banana Powder)', '100% {t} (Banana Powder)', '{t} (100% Rice, Banana Powder)', 'Toasted {t}'])
def test_unsupported_or_borrowed_forms_still_abstain(term, form):
    assert answer(form.format(t=term)) is None

@pytest.mark.parametrize('term', FOODS)
def test_source_supported_milk_mixture_keeps_its_route(term):
    assert answer(term + ' (Milk Powder)') == 1

@pytest.mark.parametrize('alias,target', ALIASES)
@pytest.mark.parametrize('form', ['{t}', 'Salted {t}', '{t} (Sugar)', '{t} powder', '100% {t} powder', '{t} powder (100% Rice)', '{t} (Banana Powder)', '{t} (Milk Powder)', '{t} oil', '{t} extract', '{t} juice', 'Mango ({t} Powder)', 'Mango (100% {t} Powder)', 'Cashew Nuts ({t} Powder)', 'Cashew Nuts (100% {t} Powder)'])
def test_alias_inherits_exact_target_not_an_extra_form_permission(alias, target, form):
    assert lookup(normalise_ingredient(alias).name)['term'] == target
    assert answer(form.format(t=alias)) == answer(form.format(t=target))

@pytest.mark.parametrize('term', ['star anise', 'winter melon', 'gherkin', 'haricot beans', 'catjang peas', 'mustard leave', 'poisonous mushrooms', 'coconut milk powder', 'cranberry extract', 'tamarind concentrate'])
def test_unadmitted_ambiguities_and_derivatives_have_no_new_route(term):
    assert answer(term) is None


def intake_module():
    spec = importlib.util.spec_from_file_location('nalt_intake', ROOT / 'scripts/ingest_nalt_names.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_intake_is_product_only_verbatim_and_never_assigns_nova():
    m = intake_module()
    root = 'https://lod.nal.usda.gov/nalt/root'
    records = {
        'product': {'uri':'product','pref':['Example leaves'],'alt':['Example leaf'],'scope':[], 'types':[m.PRODUCT],'broader':[root]},
        'plant': {'uri':'plant','pref':['Other leaves'],'alt':[],'scope':[], 'types':['Organism'],'broader':[root]},
    }
    q = m.build_queue(records, {root}, [], lambda label: False)
    assert {x['label'] for x in q} == {'Example leaves','Example leaf'}
    assert all(x['decision'] == 'NEEDS_REVIEW' for x in q)
    assert all('group' not in x and 'kind' not in x and 'to' not in x for x in q)
    assert 'Example leave' not in [x['label'] for x in q]


def test_intake_parser_ignores_non_english_labels_and_handles_taxonomy_cycle():
    m = intake_module()
    xml = b'''<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:skos="http://www.w3.org/2004/02/skos/core#"><rdf:Description rdf:about="one"><rdf:type rdf:resource="https://lod.nal.usda.gov/naltv#Product"/><skos:prefLabel xml:lang="en">Example food</skos:prefLabel><skos:prefLabel xml:lang="es">Otro</skos:prefLabel><skos:broader rdf:resource="two"/></rdf:Description><rdf:Description rdf:about="two"><skos:broader rdf:resource="one"/></rdf:Description></rdf:RDF>'''
    records = m.parse_records(io.BytesIO(xml))
    assert records['one']['pref'] == ['Example food']
    assert m.ancestors('one', records) == {'one','two'}


def test_established_flaxseed_oil_route_is_not_destroyed_by_a_short_alias():
    assert answer('Flaxseed Oil') == 2
    assert normalise_ingredient('Flaxseed Oil').name == 'flaxseed oil'


@pytest.mark.parametrize('term', ['cranberry', 'Dried Cranberries', 'Dried Cranberries (Sugar)', 'tamarind', 'coconut', 'celery', 'Celery Powder'])
def test_existing_standing_food_and_form_holds_are_not_lifted_by_thesaurus_identity(term):
    assert answer(term) is None
