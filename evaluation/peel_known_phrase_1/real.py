import sys, glob, collections
sys.path.insert(0,'src'); sys.path.insert(0,'.')
from foodscan import parser as P, classify as C
from foodscan.pipeline import analyse_text
exact=P._known_phrase
def jsr(f): return C.lookup(f) is not None or f in P._marker_terms()
orig=P._peel_label
rows={}
def peel(item, rule, guard=False):
    P._known_phrase=rule
    try:
        if guard:
            colon=P._colon_at_depth0(item)
            left=item[:colon]
            import re
            mp=re.search(r"\s+(\d+(?:\.\d+)?\s*%)\s*$",left) or re.search(r"\s*\(\s*(\d+(?:\.\d+)?\s*%)\s*\)\s*$",left)
            if mp: left=left[:mp.start()]
            if rule(P._flat(" ".join(left.split()))): return None
        return orig(item)
    finally: P._known_phrase=exact
def w(item):
    if item not in rows and P._colon_at_depth0(item)>0:
        rows[item]=(peel(item,exact),peel(item,jsr),peel(item,jsr,True))
    return orig(item)
P._peel_label=w
files=sorted(glob.glob('evaluation/*/inputs/*.txt'))+sorted(glob.glob('/home/user/FoodScanner/data/cache/oos_herb_spice_1/**/*.txt',recursive=True))+sorted(glob.glob('tests/fixtures/*.txt'))
seen=set()
for f in files:
    t=open(f,encoding='utf-8').read()
    if t in seen: continue
    seen.add(t); analyse_text(t,source='text')
print('real texts',len(seen),'items with a depth-0 colon:',len(rows))
for it,(a,b,c) in rows.items(): print('exact' ,bool(a),'js',bool(b),'js+whole-guard',bool(c),'|',it[:100])
