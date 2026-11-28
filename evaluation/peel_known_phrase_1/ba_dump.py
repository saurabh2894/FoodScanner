import sys, json
tree, mode, out = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, tree + '/src'); sys.path.insert(0, tree)
from scripts import parity_check as pc
from foodscan import parser as P, classify as C
if mode == 'pairs':       # emit the pair list of THIS tree
    json.dump(pc.PAIRS, open(out, 'w')); sys.exit(0)
pairs = json.load(open(mode))
res = [pc.py_result(t, s) for t, s in pairs]
terms = sorted(C.lexicon())
multi = {t: P._peel_label(f"{t.title()}: Roasted Sesame") for t in terms if ' ' in t}
json.dump({'res': res, 'multi': multi}, open(out, 'w'), default=str)
print(len(res), 'results', len(multi), 'multi-word terms', sum(1 for v in multi.values() if v), 'peel')
