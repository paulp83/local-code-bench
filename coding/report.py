#!/usr/bin/env python3
"""Combine runs/<config>/draw*/<pr>/result.json into a comparison (markdown to stdout).

Per config: solve rate (all draws pooled) with Wilson 95% CI, mean partial credit, mean localization, regressions,
median steps / agent time, tasks per hour (agent time), exit-status mix.
Per pair: per-task solve-rate difference, tasks only A / only B solved (draw-1, exact McNemar p).
"""
import json, math, statistics as st, sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent


def wilson(k, n, z=1.96):
    if n == 0:
        return (0, 0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0, c - h), min(1, c + h))


def mcnemar_p(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def load(configs):
    data = defaultdict(lambda: defaultdict(list))  # config -> task -> [result per draw]
    for c in configs:
        for d in sorted(p for p in (HERE / "runs" / c).glob("draw*") if p.name[4:].isdigit()):  # draw1-v1 = archived old text
            for f in d.glob("*/result.json"):
                r = json.load(open(f))
                data[c][r["n"]].append(r)
    return data


def main():
    configs = sys.argv[1:] or sorted(p.name for p in (HERE / "runs").iterdir() if not p.name.startswith("smoke"))
    data = load(configs)
    tasks = sorted({n for c in data for n in data[c]})
    print(f"# club-3090 agent tasks: {len(tasks)} tasks, configs: {', '.join(configs)}\n")
    print("| Config | Draws | Solved | Solve rate (95% CI) | Mean partial | Mean localization | Regressions | "
          "Median steps | Median agent min | Tasks/hour | Exit statuses |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for c in configs:
        rs = [r for n in data[c] for r in data[c][n]]
        if not rs:
            continue
        k, n = sum(r.get("passed", False) for r in rs), len(rs)
        lo, hi = wilson(k, n)
        part = st.mean(r.get("partial", 0) or 0 for r in rs)
        locs = [r["localization"] for r in rs if r.get("localization") is not None]
        reg = sum(bool(r.get("regressions")) for r in rs)
        steps = st.median(r.get("steps") or 0 for r in rs)
        secs = [r.get("agent_s") or 0 for r in rs]
        tph = k / (sum(secs) / 3600) if sum(secs) else 0
        ex = Counter(r.get("exit_status") for r in rs).most_common(4)
        draws = max(len(v) for v in data[c].values())
        print(f"| {c} | {draws} | {k}/{n} | {k / n:.0%} ({lo:.0%}–{hi:.0%}) | {part:.2f} | "
              f"{st.mean(locs) if locs else 0:.2f} | {reg} | {steps:.0f} | {st.median(secs) / 60:.1f} | {tph:.2f} | "
              f"{', '.join(f'{e} {m}' for e, m in ex)} |")
    print("\n## Pairwise (same tasks)\n")
    print("| A vs B | Tasks both ran | Only A solved | Only B solved | McNemar p (draw 1) | Mean per-task solve-rate diff A−B |")
    print("|---|---|---|---|---|---|")
    for a, b in combinations(configs, 2):
        common = [n for n in tasks if data[a].get(n) and data[b].get(n)]
        if not common:
            continue
        oa = sum(data[a][n][0].get("passed", False) and not data[b][n][0].get("passed", False) for n in common)
        ob = sum(data[b][n][0].get("passed", False) and not data[a][n][0].get("passed", False) for n in common)
        rate = lambda c, n: st.mean(r.get("passed", False) for r in data[c][n])
        diff = st.mean(rate(a, n) - rate(b, n) for n in common)
        print(f"| {a} vs {b} | {len(common)} | {oa} | {ob} | {mcnemar_p(oa, ob):.2f} | {diff:+.2f} |")
    print("\n## Per task (solve rate across draws; partial credit in brackets)\n")
    print("| Task | " + " | ".join(configs) + " |")
    print("|---|" + "---|" * len(configs))
    for n in tasks:
        cells = []
        for c in configs:
            rs = data[c].get(n, [])
            cells.append("—" if not rs else f"{st.mean(r.get('passed', False) for r in rs):.1f} "
                                           f"[{st.mean(r.get('partial', 0) or 0 for r in rs):.2f}]")
        print(f"| #{n} | " + " | ".join(cells) + " |")


if __name__ == "__main__":
    main()
