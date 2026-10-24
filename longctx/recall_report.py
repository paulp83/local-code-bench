#!/usr/bin/env python3
"""Paired comparison of two recall.py outputs (A = baseline, B = variant), split by fact kind and prefix length:
mean margin of each arm, the paired difference with a bootstrap 95% CI over filler docs, and % of queries where the
correct name beats the alternative. Asserts both arms saw byte-identical prompts.

  python3 recall_report.py recall_bf16.json recall_fp32.json"""
import json, random, statistics as st, sys

key = lambda r: (r["doc"], r["L"], r["team"])
a = {key(r): r for r in json.load(open(sys.argv[1]))}
b = {key(r): r for r in json.load(open(sys.argv[2]))}
keys = sorted(set(a) & set(b))
random.seed(0)
assert all(a[k]["phash"] == b[k]["phash"] for k in keys), "arms saw different prompts"
print("paired queries:", len(keys), "docs:", "".join(sorted({k[0] for k in keys})))
print(f"{'kind':7}{'L':>7}{'n':>4}{'margin A':>10}{'margin B':>10}{'A-B':>8}{'95% CI (doc bootstrap)':>26}{'correct% A':>12}{'B':>6}")
for kind in ("plant", "update"):
    for L in sorted({k[1] for k in keys}):
        ks = [k for k in keys if k[1] == L and a[k]["kind"] == kind]
        if not ks:
            continue
        per = {}
        for k in ks:
            per.setdefault(k[0], []).append(a[k]["margin"] - b[k]["margin"])
        docs = sorted(per)
        boot = sorted(st.mean([v for d in random.choices(docs, k=len(docs)) for v in per[d]]) for _ in range(4000))
        diff = st.mean(v for d in docs for v in per[d])
        print(f"{kind:7}{L:>7}{len(ks):>4}{st.mean(a[k]['margin'] for k in ks):>10.2f}{st.mean(b[k]['margin'] for k in ks):>10.2f}"
              f"{diff:>+8.2f}   [{boot[100]:+.2f},{boot[3900]:+.2f}]{100 * st.mean(a[k]['margin'] > 0 for k in ks):>16.0f}{100 * st.mean(b[k]['margin'] > 0 for k in ks):>6.0f}")
