"""Survey: where does the exact-term rule (Python) differ from the isRecognised rule (JS) in _peel_label, over every text in the parity corpus + saved inputs."""
import sys, json, glob, os, csv, collections
sys.path.insert(0,'/home/user/foodscan_peel/src'); sys.path.insert(0,'/home/user/foodscan_peel')
from foodscan import parser as P, classify as C
from foodscan.pipeline import analyse_text
from scripts import parity_check as pc
exact = P._known_phrase
def jsrule(flat): return C.lookup(flat) is not None or flat in P._marker_terms()
log = {}
orig = P._peel_label
cur = {'t': None}
def wrapped(item):
    P._known_phrase = exact; a = orig(item)
    P._known_phrase = jsrule; b = orig(item)
    P._known_phrase = exact
    if a != b: log.setdefault(item, (a, b, set()))[2].add(cur['t'][:60])
    return a
P._peel_label = wrapped
texts = {}
for t, s in pc.PAIRS: texts[(t, s)] = 1
for f in glob.glob('evaluation/*/inputs/*.txt') + glob.glob('data/**/*.txt', recursive=True):
    texts[(open(f, encoding='utf-8').read(), 'text')] = 1
n = 0
for (t, s) in texts:
    cur['t'] = t
    try: analyse_text(t, source=s)
    except Exception as e: pass
    n += 1
print('texts', n, 'differing items', len(log))
out = [{'item': k, 'py': v[0], 'js': v[1], 'n_texts': len(v[2])} for k, v in log.items()]
json.dump(out, open('/tmp/claude-0/peel/survey.json', 'w'), indent=1, ensure_ascii=False)
for o in out[:60]: print(o['n_texts'], '|', o['item'][:90], '|', o['py'], '=>', o['js'])
