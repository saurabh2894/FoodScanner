import json,sys
P=json.load(open('/tmp/claude-0/peel/ba_pairs.json')); pairs=P['pairs']; n=P['n_corpus']
def load(t): return json.load(open(f'/tmp/claude-0/peel/ba_{t}.json'))['res']
def st(r): return (bool(r['answered']), r['group'] if r['answered'] else None, (r.get('completeness') or {}).get('status'))
def cls(o,n_):
    (oa,og,os_),(na,ng,ns)=st(o),st(n_)
    if (oa,og,os_)==(na,ng,ns): return 'same answer/status (structure only)' if o!=n_ else 'identical'
    if oa and not na: return 'more cautious (answer -> abstain)'
    if not oa and na: return 'MORE CONFIDENT (abstain -> answer)'
    if oa and na and og!=ng: return 'ANSWERED GROUP CHANGED'
    if os_=='complete' and ns=='uncertain': return 'more cautious (complete -> uncertain)'
    if os_=='uncertain' and ns=='complete': return 'MORE CONFIDENT (uncertain -> complete)'
    return 'other'
def compare(a,b,label):
    A,B=load(a),load(b); import collections
    c=collections.Counter(); rows=[]
    for i,(x,y) in enumerate(zip(A,B)):
        k=cls(x,y)
        if k!='identical':
            c[k]+=1; rows.append((i,k,st(x),st(y)))
    print(f'== {label}: pairs {len(A)}; changed {sum(c.values())}'); [print('  ',k,v) for k,v in c.items()]
    return rows
if __name__=='__main__':
    r1=compare('foodscan_peel_base','foodscan_peel','base ddc717e -> new')
    r2=compare('foodscan_peel_prev','foodscan_peel','PR head b886096 -> new')
    r3=compare('foodscan_peel_base','foodscan_peel_prev','base ddc717e -> PR head b886096 (reference)')
    json.dump({'base_new':r1,'prev_new':r2,'base_prev':r3},open('/tmp/claude-0/peel/ba_rows.json','w'))
