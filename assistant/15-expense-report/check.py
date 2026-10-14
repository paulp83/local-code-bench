#!/usr/bin/env python3
"""check.py for 15-expense-report: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"c": {"lodging": {"claimed": 703.65, "reimbursable": 703.65}, "meals": {"claimed": 488.34, "reimbursable": 34.25}, "supplies": {"claimed": 1041.01, "reimbursable": 1041.01}, "transport": {"claimed": 819.31, "reimbursable": 819.31}}, "d": ["R23", "R24"], "o": ["R12", "R17", "R21", "R22"], "t": 2598.22}')
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
    o = jl("report.json")
    chk("report-parses", isinstance(o, dict))
    if isinstance(o, dict):
        cats = o.get("categories", {}) if isinstance(o.get("categories"), dict) else {}
        chk("four-categories", set(cats) == set(E["c"]), sorted(cats))
        near = lambda a, b: isinstance(a, (int, float)) and abs(a - b) < 0.005
        for c, v in E["c"].items():
            g = cats.get(c, {}) if isinstance(cats.get(c), dict) else {}
            chk("claimed-" + c, near(g.get("claimed"), v["claimed"]), (g.get("claimed"), v["claimed"]))
            chk("reimbursable-" + c, near(g.get("reimbursable"), v["reimbursable"]), (g.get("reimbursable"), v["reimbursable"]))
        chk("total-reimbursable", near(o.get("total_reimbursable"), E["t"]), (o.get("total_reimbursable"), E["t"]))
        chk("duplicates-dropped", o.get("duplicates_dropped") == E["d"], o.get("duplicates_dropped"))
        chk("over-cap", o.get("over_cap") == E["o"], o.get("over_cap"))

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
