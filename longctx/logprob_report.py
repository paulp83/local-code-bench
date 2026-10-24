#!/usr/bin/env python3
"""Paired comparison of two logprob.py outputs (A = baseline, B = variant): per prefix length, mean NLL of each, the
paired NLL difference with a bootstrap 95% CI over docs, mean |log-prob difference|, and top-1 agreement.
If error accumulates with position, the |difference| and disagreement grow with L.

  python3 logprob_report.py logprob_bf16.json logprob_fp32.json"""
import json, random, statistics as st, sys

a = {(r["doc"], r["L"]): r for r in json.load(open(sys.argv[1]))}
b = {(r["doc"], r["L"]): r for r in json.load(open(sys.argv[2]))}
random.seed(0)
print(f"{'L':>7} {'docs':>4} {'NLL A':>8} {'NLL B':>8} {'A-B':>8} {'95% CI':>19} {'mean|dlp|':>10} {'top1 agree':>10}")
for L in sorted({k[1] for k in b}):
    docs = sorted(d for (d, l) in b if l == L and (d, l) in a)
    rows = []
    for d in docs:
        x, y = a[(d, L)], b[(d, L)]
        assert x["ids"] == y["ids"], "arms scored different tokens"
        n = len(x["lp"])
        rows.append((-sum(x["lp"]) / n, -sum(y["lp"]) / n, sum(abs(p - q) for p, q in zip(x["lp"], y["lp"])) / n,
                     sum(p == q for p, q in zip(x["top1"], y["top1"])) / n))
    diff = [r[0] - r[1] for r in rows]
    boot = sorted(st.mean(random.choices(diff, k=len(diff))) for _ in range(5000))
    print(f"{L:>7} {len(docs):>4} {st.mean(r[0] for r in rows):>8.4f} {st.mean(r[1] for r in rows):>8.4f} {st.mean(diff):>+8.4f} "
          f"[{boot[125]:+.4f},{boot[4875]:+.4f}] {st.mean(r[2] for r in rows):>10.4f} {st.mean(r[3] for r in rows):>10.3f}")
