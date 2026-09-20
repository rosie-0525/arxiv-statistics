import json, glob, datetime, statistics, collections
ALIAS = {'math-ph': 'math.MP', 'cs.IT': 'math.IT', 'stat.TH': 'math.ST'}
NAMES = {
 'math.AC':'Commutative Algebra','math.AG':'Algebraic Geometry','math.AP':'Analysis of PDEs','math.AT':'Algebraic Topology',
 'math.CA':'Classical Analysis and ODEs','math.CO':'Combinatorics','math.CT':'Category Theory','math.CV':'Complex Variables',
 'math.DG':'Differential Geometry','math.DS':'Dynamical Systems','math.FA':'Functional Analysis','math.GM':'General Mathematics',
 'math.GN':'General Topology','math.GR':'Group Theory','math.GT':'Geometric Topology','math.HO':'History and Overview',
 'math.IT':'Information Theory','math.KT':'K-Theory and Homology','math.LO':'Logic','math.MG':'Metric Geometry',
 'math.MP':'Mathematical Physics','math.NA':'Numerical Analysis','math.NT':'Number Theory','math.OA':'Operator Algebras',
 'math.OC':'Optimization and Control','math.PR':'Probability','math.QA':'Quantum Algebra','math.RA':'Rings and Algebras',
 'math.RT':'Representation Theory','math.SG':'Symplectic Geometry','math.SP':'Spectral Theory','math.ST':'Statistics Theory'}
CATS = sorted(NAMES); CATSET = set(CATS)
start = datetime.date(2018, 1, 1)
seen = set(); recs = []; nread = 0; nold = 0
for fn in sorted(glob.glob('data/w*.jsonl')):
    for line in open(fn):
        r = json.loads(line); nread += 1
        if r['id'] in seen: continue
        seen.add(r['id'])
        d = datetime.date.fromisoformat(r['c'])
        if d < start: nold += 1; continue
        toks = [ALIAS.get(t, t) for t in (r['k'] or '').split()]
        prim = toks[0] if toks and toks[0] in CATSET else None
        anyc = {t for t in toks if t in CATSET}
        recs.append((d, prim, anyc))
maxd = max(r[0] for r in recs)
N = (maxd - start).days + 1
tot = [0] * N
for d, p, a in recs:
    if a: tot[(d - start).days] += 1
# last complete day: count not far below the median of the same weekday over the previous 4 weeks
end_i = N - 1
while end_i > 28:
    ref = statistics.median(tot[end_i - k] for k in (7, 14, 21, 28))
    if tot[end_i] >= 0.6 * ref: break
    end_i -= 1
end = start + datetime.timedelta(days=end_i)
M = end_i + 1
prim = {c: [0] * M for c in CATS + ['ALL']}
anyd = {c: [0] * M for c in CATS + ['ALL']}
for d, p, a in recs:
    i = (d - start).days
    if i >= M: continue
    if p: prim[p][i] += 1; prim['ALL'][i] += 1
    if a: anyd['ALL'][i] += 1
    for c in a: anyd[c][i] += 1
out = {'start': start.isoformat(), 'end': end.isoformat(), 'generated': datetime.date.today().isoformat(),
       'nPrimary': sum(prim['ALL']), 'nAny': sum(anyd['ALL']), 'cats': CATS, 'names': NAMES, 'primary': prim, 'any': anyd}
json.dump(out, open('data.json', 'w'), separators=(',', ':'))
print(f"read={nread} unique={len(seen)} pre2018={nold} kept={len(recs)} maxCreated={maxd} lastComplete={end}")
print("last 16 days (any-math totals):", [(str(start + datetime.timedelta(days=i))[5:], tot[i]) for i in range(N - 16, N)])
yr = collections.Counter(); yra = collections.Counter()
for d, p, a in recs:
    if (d - start).days < M:
        if p: yr[d.year] += 1
        if a: yra[d.year] += 1
print("per year primary:", sorted(yr.items())); print("per year any:", sorted(yra.items()))
