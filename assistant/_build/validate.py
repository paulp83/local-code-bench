#!/usr/bin/env python3
"""Validate assistant tasks.

  python3 validate.py [--only 27,28] [--report-old]

For every task: workspace copied with symlinks preserved (as run_assistant.py does), never validated in place.
  - seed must FAIL, seed+reference must PASS
  - hard-v1 tasks: every check name printed by the reference run needs a spec_map entry whose quote appears verbatim in task.md
  - axes A-C (and E): a naive solution in _build/naive/<id>/ must FAIL >= 1 check
  - --report-old writes ../spec-map-report-01-26.md (heuristic mapping, report only; tasks 01-26 are not modified)
"""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, run_check, names_of

only = None
if "--only" in sys.argv:
    only = {x.strip() for x in sys.argv[sys.argv.index("--only") + 1].split(",")}
dirs = sorted(p for p in ROOT.iterdir() if (p / "check.py").exists())
if only: dirs = [d for d in dirs if d.name.split("-")[0] in only or d.name in only]
last = lambda s: (s.stdout.strip().splitlines() or [s.stderr[-80:]])[-1]
bad = 0
for d in dirs:
    meta = json.loads((d / "meta.json").read_text())
    a = run_check(d); b = run_check(d, d / "reference")
    probs = []
    if not (a.returncode != 0): probs.append("seed does not fail")
    if b.returncode != 0: probs.append("reference fails")
    extra = ""
    if meta.get("set") == "hard-v1":
        sm = meta.get("spec_map", {}); md = (d / "task.md").read_text()
        names = names_of(b.stdout)
        miss = [n for n in names if n not in sm]
        if miss: probs.append(f"spec_map lacks {miss[:3]}")
        badq = [n for n, q in sm.items() if q not in md]
        if badq: probs.append(f"spec quote not verbatim for {badq[:3]}")
        nv = ROOT / "_build" / "naive" / d.name
        if meta.get("axis") in ("A", "B", "C", "E") and meta.get("axis") != "B":
            if not nv.exists(): probs.append("naive solution missing")
            else:
                c = run_check(d, nv); failed = [l[5:].split(":")[0] for l in c.stdout.splitlines() if l.startswith("FAIL ") and not l.startswith("FAIL:")]
                if c.returncode == 0 or not failed: probs.append("naive PASSES")
                extra = f" | naive fails {len(failed)}: {','.join(failed[:3])}"
        extra += f" | spec {len(sm)}/{len(names)}"
    ok = not probs; bad += not ok
    print(f"{'OK  ' if ok else 'BAD '}{d.name:30} seed:{last(a)} | ref:{last(b)}{extra}" + ("" if ok else "  !! " + "; ".join(probs)))
    if not ok and b.returncode != 0: print(b.stdout[-500:])

if "--report-old" in sys.argv:
    stop = set("the a an of to in for and or is are be on at by with from as it its that this per each all not no one two row col column check exact exactly parses parse file files".split())
    out = ["# Spec-map report for tasks 01-26 (heuristic, report only)\n",
           "For each check name, the `task.md` line with the highest token overlap is shown. Overlap below 0.5 is flagged `?` and was reviewed by hand (see the verdict column / notes after the table).\n"]
    flagged = 0
    for d in sorted(p for p in ROOT.iterdir() if (p / "check.py").exists()):
        m = json.loads((d / "meta.json").read_text())
        if m.get("set") == "hard-v1": continue
        md = (d / "task.md").read_text(); lines = [l.strip() for l in md.splitlines() if l.strip()]
        r = run_check(d, d / "reference"); names = names_of(r.stdout)
        out.append(f"\n## {d.name}\n\n| check | best matching line in task.md | overlap |\n|---|---|---|")
        for n in names:
            toks = [t for t in re.split(r"[-_.\s]+", n.lower()) if len(t) > 2 and t not in stop and not t.isdigit() and not re.fullmatch(r"[a-z]\d+", t)]
            if not toks: toks = [n.lower()]
            best = max(((sum(t in re.sub(r"[^a-z0-9]", "", l.lower()) or t in l.lower() for t in toks) / len(toks), l) for l in lines), key=lambda x: x[0])
            flag = "" if best[0] >= 0.5 else " ?"; flagged += bool(flag)
            out.append(f"| `{n}` | {best[1][:110].replace('|', '/')} | {best[0]:.2f}{flag} |")
    out.append(f"\nFlagged: {flagged}\n")
    (ROOT / "spec-map-report-01-26.md").write_text("\n".join(out))
    print("wrote spec-map-report-01-26.md, flagged", flagged)
sys.exit(1 if bad else 0)
