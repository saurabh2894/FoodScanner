import sys, glob, json, collections
sys.path.insert(0,'/home/user/foodscan_peel/src'); sys.path.insert(0,'/home/user/foodscan_peel')
import foodscan.classify as C, foodscan.pipeline as PL
from foodscan.pipeline import analyse_text
from scripts import parity_check as pc
orig = C.classify_ingredients
MODE = {'m': 'off'}
FALL = "recognised ingredients, but the combination does not match a group 1, 2 or 3 pattern"
def sim(ings, *a, **k):
    r = orig(ings, *a, **k)
    if MODE['m'] != 'off' and r.group is None and r.reason == FALL and ings:
        rows = [C.lookup(i.name) for i in ings]
        if all(x and x['kind'] == 'herb_spice' for x in rows) and (len(ings) == 1 or MODE['m'] == 'list'):
            r = C.Classification(1, drivers=[C.Driver(i.raw, "SIMULATION herb/spice", x['source'], i.section) for i, x in zip(ings, rows)])
    return r
C.classify_ingredients = sim
if hasattr(PL, 'classify_ingredients'): PL.classify_ingredients = sim
def run(texts):
    return [ (lambda a: (a.answered, a.group, a.completeness['status']))(analyse_text(t, source=s)) for t, s in texts]
frozen = []
for d in ("fresh_batch_1","fresh_batch_2","fresh_batch_3","negation_addendum","dev_regression_15"):
    frozen += [(open(f,encoding='utf-8').read(),'text') for f in sorted(glob.glob(f"evaluation/{d}/inputs/*.txt"))]
oos = [(open(f,encoding='utf-8').read(),'text') for f in sorted(glob.glob('/home/user/FoodScanner/data/cache/oos_herb_spice_1/inputs/*.txt'))]
sets = {'frozen66': frozen, 'oos32': oos, 'parity': pc.PAIRS}
res = {}
for m in ('off','sole','list'):
    MODE['m'] = m
    res[m] = {k: run(v) for k, v in sets.items()}
for m in ('sole','list'):
    for k, v in sets.items():
        ch = [i for i,(x,y) in enumerate(zip(res['off'][k], res[m][k])) if x != y]
        print(m, k, 'changed', len(ch), 'of', len(v), '| abstain->G1:', sum(1 for i in ch if not res['off'][k][i][0] and res[m][k][i][1]==1), '| answered->other:', sum(1 for i in ch if res['off'][k][i][0]))
        if k != 'parity':
            for i in ch[:12]: print('    ', v[i][0][:90].replace('\n',' '), res['off'][k][i], '->', res[m][k][i])
import re, collections
ch = [i for i,(x,y) in enumerate(zip(res['off']['parity'], res['sole']['parity'])) if x != y]
txt = sorted({pc.PAIRS[i][0] for i in ch})
print('distinct texts', len(txt))
pat = collections.Counter()
for t in txt:
    body = t.replace('Ingredients: ','').rstrip('.')
    for k,rx in [('bracket',r'\('),('salt/sugar/oil word',r'\b(salt|sugar|oil|fat|butter|ghee|starch|vinegar|sauce)\b'),('paste/extract/oleoresin/flavour',r'\b(paste|extract|oleoresin|flavou?r\w*|essence|masala|mix|blend|seasoning)\b'),('dried/roasted/ground/powder/whole/fresh',r'\b(dried|dry|roasted|ground|powder\w*|whole|fresh|raw)\b')]:
        if re.search(rx, body, re.I): pat[k]+=1
print(pat)
import random; random.seed(1)
for t in random.sample(txt, 40): print('  ', t.replace('Ingredients: ','')[:100])
