import sys, json, collections, re
sys.path.insert(0,'src'); sys.path.insert(0,'.')
from foodscan import classify as C, parser as P
terms=sorted(C.lexicon()); mk=sorted(P._marker_terms())
exact=P._known_phrase
def jsr(f): return C.lookup(f) is not None or f in P._marker_terms()
def peel(item, rule):
    P._known_phrase=rule
    try: return P._peel_label(item)
    finally: P._known_phrase=exact
# prefix forms (each is what a label could write before a section label)
descs=sorted(C._descriptors())
def forms(t):
    out={('plural' ,t+'s' if not t.endswith('s') else t)}
    for d in ('dried','refined','organic','fresh','powdered','whole','ground','roasted'):
        out.add(('desc:'+d, d+' '+t))
    out.add(('t_powder', t+' powder'))
    return out
# tails: genuine section words + real compound tails (last word of every multiword lexicon term) + other label-like words
tails=collections.Counter(t.split()[-1] for t in terms if ' ' in t)
genuine=['seasoning','sauce','soup','topping','filling','coating','base','dressing','garnish','masala','oleoresin','spread','crumb','biscuit','noodles','gravy','premix']
W=sorted(set(genuine)|{w for w,c in tails.items() if c>=2})
res=collections.defaultdict(lambda: collections.Counter()); examples=collections.defaultdict(list)
for t in terms:
    for kind,F in forms(t):
        if exact(F) : continue            # exact rule already knows this prefix: no divergence
        if not jsr(F): continue           # neither rule knows it
        for w in W:
            item=f"{F.title()} {w.title()}: Roasted Sesame"
            r=peel(item,jsr)
            if r:
                whole=C.lookup(P._flat(f"{F} {w}")) is not None
                res[w]['js_only_peels']+=1
                res[w]['of_which_whole_phrase_is_a_recognised_item']+= whole
                if whole and len(examples[w])<4: examples[w].append(f"{F} {w}")
print('js-only-known prefixes (not exact):', len({F for t in terms for k,F in forms(t) if not exact(F) and jsr(F)}))
tot=sum(c['js_only_peels'] for c in res.values()); wh=sum(c['of_which_whole_phrase_is_a_recognised_item'] for c in res.values())
print('js-only peels',tot,' of which whole left-hand phrase is itself a recognised ingredient:',wh)
for w,c in sorted(res.items(), key=lambda kv:-kv[1]['js_only_peels'])[:40]: print(f"{w:12s} {c['js_only_peels']:5d} whole-recognised {c['of_which_whole_phrase_is_a_recognised_item']:4d}  {examples[w]}")
