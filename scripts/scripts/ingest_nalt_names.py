"""Build a review-only naming queue from NALT RDF/XML, never runtime rows.

NALT Product labels are discovery evidence, not proof that every label is an
identical food or that any processed form has a NOVA placement. The bulk export
may lag current pages. Recheck admitted concepts live, preserve licence/source
attribution, review food part and every inherited route, then edit a separate
admission manifest. This command cannot write the lexicon or synonyms.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))
from foodscan.classify import _singular_phrase, lexicon, lookup
from foodscan.normalise import flatten, normalise_ingredient

RDF = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'
SKOS = '{http://www.w3.org/2004/02/skos/core#}'
LANG = '{http://www.w3.org/XML/1998/namespace}lang'
PRODUCT = 'https://lod.nal.usda.gov/naltv#Product'
# Food-product classes, not the similarly named organism/taxon records.
DEFAULT_ROOTS = ['12570', '6769', '16205', '16747', '13571']

def parse_records(stream):
    records = {}
    for _, elem in ET.iterparse(stream, events=('end',)):
        if elem.tag != RDF + 'Description':
            continue
        uri = elem.get(RDF + 'about')
        if not uri:
            elem.clear()
            continue
        def labels(tag):
            return [x.text.strip() for x in elem.findall(SKOS + tag)
                    if x.get(LANG) == 'en' and x.text and x.text.strip()]
        records[uri] = {
            'uri': uri, 'pref': labels('prefLabel'), 'alt': labels('altLabel'),
            'scope': labels('scopeNote'),
            'types': [x.get(RDF + 'resource') for x in elem.findall(RDF + 'type')],
            'broader': [x.get(RDF + 'resource') for x in elem.findall(SKOS + 'broader')],
        }
        elem.clear()
    return records

def ancestors(uri, records):
    seen = set()
    todo = list(records.get(uri, {}).get('broader', []))
    while todo:
        value = todo.pop()
        if value in seen or value is None:
            continue
        seen.add(value)
        todo.extend(records.get(value, {}).get('broader', []))
    return seen

def build_queue(records, roots, canonical_rows, recognised):
    index = {}
    for row in canonical_rows:
        index.setdefault(_singular_phrase(flatten(row['term'])), []).append(row['term'])
    out = []
    for uri, record in sorted(records.items()):
        if PRODUCT not in record['types']:
            continue
        labels = record['pref'] + record['alt']
        matches = sorted({term for label in labels
                          for term in index.get(_singular_phrase(flatten(label)), [])})
        paths = sorted(roots & ancestors(uri, records))
        if not matches and not paths:
            continue
        for label in dict.fromkeys(labels):
            # Retain only verbatim English labels. In particular, do not turn
            # 'mustard leaves' into the invalid generated 'mustard leave'.
            if not re.fullmatch(r'[A-Za-z][A-Za-z -]+', label) or recognised(label):
                continue
            out.append({
                'label': label, 'source_uri': uri, 'preferred_labels': record['pref'],
                'scope_notes': record['scope'], 'existing_head_hints': matches,
                'food_class_paths': paths, 'decision': 'NEEDS_REVIEW',
                'warning': 'No identity, form or NOVA decision. Head hints can be distinct foods.',
            })
    return out

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--rdf', type=Path, required=True, help='Local RDF/XML or official ZIP archive')
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--root', action='append', help='NALT Product class ID, repeatable')
    a = p.parse_args(argv)
    # An explicit safety boundary: output is a new review file, never runtime.
    if a.out.suffix.lower() != '.json' or a.out.resolve().is_relative_to((ROOT / 'src').resolve()):
        p.error('--out must be a review JSON outside src/')
    if zipfile.is_zipfile(a.rdf):
        with zipfile.ZipFile(a.rdf) as z:
            members = [n for n in z.namelist() if n.lower().endswith(('.rdf', '.xml'))]
            if len(members) != 1:
                p.error('archive must contain exactly one RDF/XML member')
            member = members[0]
            with z.open(member) as stream:
                records = parse_records(stream)
    else:
        member = None
        with a.rdf.open('rb') as stream:
            records = parse_records(stream)
    roots = {'https://lod.nal.usda.gov/nalt/' + x for x in (a.root or DEFAULT_ROOTS)}
    queue = build_queue(records, roots, list(lexicon().values()),
                        lambda label: lookup(normalise_ingredient(label).name) is not None)
    payload = {
        'purpose': 'naming discovery only, no runtime or NOVA assignments',
        'archive_sha256': hashlib.sha256(a.rdf.read_bytes()).hexdigest(),
        'archive_member': member, 'records': len(records), 'candidates': len(queue),
        'license': 'USDA National Agricultural Library, NALT, CC BY 4.0. Adapted discovery queue; no endorsement.',
        'freshness_warning': 'Archive date is not current-page verification. Check each admitted concept live.',
        'queue': queue,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: payload[k] for k in ('records', 'candidates', 'archive_member')}))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
