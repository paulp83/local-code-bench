#!/usr/bin/env python3
"""check.py for 03-rig-report-table: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"c": [["tp2-fp8", "108.5", "5837", "29.1"], ["tp2-awq", "84.5", "8803", "21.0"], ["single-q4", "88.2", "9574", "27.2"], ["pp2-q6", "91.7", "7460", "23.7"], ["offload-q8", "n/a", "n/a", "n/a"]]}')
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
    s = rd("summary.md")
    chk("summary-exists", s is not None)
    tb = [l for l in (s or "").splitlines() if l.strip().startswith("|")]
    chk("header-exact", bool(tb) and re.sub(r"\s+", " ", tb[0].strip()) == "| config | decode_tps | prefill_tps | peak_vram_gib |", tb[:1])
    body = [[c.strip() for c in l.strip().strip("|").split("|")] for l in tb[2:]] if len(tb) > 2 else []
    chk("row-order", [b[0] for b in body] == [x[0] for x in E["c"]], [b[0] for b in body])
    got = {b[0]: b[1:] for b in body if len(b) == 4}
    for k, *v in E["c"]:
        chk("row-" + k, got.get(k) == v, got.get(k))

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
