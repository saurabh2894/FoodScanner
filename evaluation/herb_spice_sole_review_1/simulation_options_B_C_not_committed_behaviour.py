import sys, re, glob, collections
sys.path.insert(0,'/home/user/foodscan_t2/src'); sys.path.insert(0,'/home/user/foodscan_t2')
import foodscan.classify as C, foodscan.pipeline as PL
from foodscan.pipeline import analyse_text
from scripts import parity_check as pc
orig = C.classify_ingredients
FALL = "recognised ingredients, but the combination does not match a group 1, 2 or 3 pattern"
BAD = re.compile(r"\b(salt\w*|sugar\w*|sweeten\w*|flavou?r\w*|oil\w*|fat|ghee|butter|milk|starch|vinegar|sauce|paste|extract\w*|oleoresin|masala|mix\w*|blend\w*|seasoning|pickle\w*|candied|caramel\w*|honey|jaggery|syrup|brine\w*|canned|bottled|preserved|colou?r\w*)\b", re.I)
FORMS_OK = {"whole","dried","dry","fresh","ground","crushed","powder","powdered","seeds","seed","leaves","leaf","flakes","pure","plain","organic","raw","natural"}
M = {'m': 'off'}
def sim(ings, *a, **k):
    r = orig(ings, *a, **k)
    m = M['m']
    if m != 'off' and r.group is None and r.reason == FALL and len(ings) == 1:
        ing = ings[0]; row = C.lookup(ing.name)
        if row and row['kind'] == 'herb_spice':
            raw = ing.raw
            ok = '(' not in raw and not BAD.search(raw)
            powder = bool(re.search(r"\bpowder(ed)?\b", raw, re.I))
            stated = bool(re.search(r"(?<![\d.])100(\.0+)?\s*%|\bwhole\b", raw, re.I))
            if ok and (m == 'C' or not powder or stated):
                r = C.Classification(1, drivers=[C.Driver(raw, "SIM", row['source'], ing.section)])
    return r
C.classify_ingredients = sim
if hasattr(PL, 'classify_ingredients'): PL.classify_ingredients = sim
def run(ts): return [(lambda a: (a.answered, a.group))(analyse_text(t, source=s)) for t, s in ts]
fr=[]
for d in ("fresh_batch_1","fresh_batch_2","fresh_batch_3","negation_addendum","dev_regression_15"): fr+=[(open(f,encoding='utf-8').read(),'text') for f in sorted(glob.glob(f"evaluation/{d}/inputs/*.txt"))]
oos=[(open(f,encoding='utf-8').read(),'text') for f in sorted(glob.glob('/home/user/FoodScanner/data/cache/oos_herb_spice_1/inputs/*.txt'))]
sets={'frozen66':fr,'oos32':oos,'parity':pc.PAIRS}
base={k:run(v) for k,v in sets.items()}
for m in ('B','C'):
    M['m']=m
    for k,v in sets.items():
        res=run(v); ch=[i for i,(x,y) in enumerate(zip(base[k],res)) if x!=y]
        print(m,k,'changed',len(ch),'of',len(v))
        if k=='parity':
            txt=sorted({v[i][0].replace('Ingredients: ','') for i in ch}); print('   distinct texts',len(txt))
            leak=[t for t in txt if BAD.search(t) or '(' in t]; print('   with guard word/bracket (must be 0):',len(leak), leak[:5])
            print('   sample:', txt[:12])
