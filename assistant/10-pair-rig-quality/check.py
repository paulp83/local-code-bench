#!/usr/bin/env python3
"""check.py for 10-pair-rig-quality: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"p": [["glm53-flash-q4", "2026-10-01", "2026-10-01_glm53-flash-q4_run2.json", "q-2026-10-01-glm53f-q4.json"], ["qfn-fp8", "2026-10-02", "2026-10-02_qfn-fp8_run1.json", "q-2026-10-02-qfn8.json"], ["qwen-27b-q4", "2026-10-05", "2026-10-05_qwen-27b-q4_run3.json", "q-2026-10-05-qwen-27b-q4.json"]], "s": ["2026-10-01_glm53-flash-q4_run1.json", "2026-10-05_qwen-27b-q4_run1.json", "2026-10-05_qwen-27b-q4_run2.json"], "uq": ["q-2026-10-04-qfn-awq.json", "q-2026-10-06-llama-8b-q8.json"], "ur": ["2026-10-03_qfn-awq_run1.json", "2026-10-05_llama-8b-q8_run1.json"]}')
R = []
def chk(name, ok, why=""):
    R.append((name, bool(ok), why))
def p(*a): return os.path.join(W, *a)
def rd(rel):
    try:
        with open(p(rel), encoding="utf-8") as f: return f.read()
    except Exception: return None
def jl(rel):
    s = rd(rel)
    if s is None: return None
    try: return json.loads(s)
    except Exception: return None
def rows(rel):
    s = rd(rel)
    if s is None: return None
    try: return list(csv.DictReader(io.StringIO(s)))
    except Exception: return None
def finish():
    for n, ok, why in R:
        print(("PASS " if ok else "FAIL ") + n + ("" if ok or not why else ": " + str(why)[:200]))
    f = sum(1 for r in R if not r[1])
    print("PASS: %d FAIL: %d" % (len(R) - f, f))
    sys.exit(0 if f == 0 and R else 1)
try:
    r = rows("pairs.csv")
    chk("pairs-header", (rd("pairs.csv") or "").splitlines()[:1] == ["slug,date,rig_file,quality_file"])
    got = [tuple(x[k] for k in ("slug", "date", "rig_file", "quality_file")) for x in (r or [])]
    chk("pairs-exact", got == [tuple(x) for x in E["p"]], got)
    lst = lambda n: None if rd(n) is None else [l for l in rd(n).splitlines() if l.strip()]
    chk("superseded-exact", lst("superseded.txt") == E["s"], lst("superseded.txt"))
    chk("unpaired-rig-exact", lst("unpaired_rig.txt") == E["ur"], lst("unpaired_rig.txt"))
    chk("unpaired-quality-exact", lst("unpaired_quality.txt") == E["uq"], lst("unpaired_quality.txt"))
    chk("no-nearest-date-pairing", not any(x[1] == "2026-10-04" for x in got))

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
