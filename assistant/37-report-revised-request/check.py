#!/usr/bin/env python3
"""check.py for 37-report-revised-request: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"rev": {"East": 88663.48, "North": 70641.15, "South": 91351.89}, "top": ["Prod-C", "Prod-H", "Prod-F"], "tot": 250656.52}')
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
    o = o if isinstance(o, dict) else {}
    chk("report-keys-exact", set(o) == {"quarter", "revenue_by_region", "top_products", "total_revenue"}, sorted(o))
    chk("quarter-is-2026-Q3", o.get("quarter") == "2026-Q3", o.get("quarter"))
    rv = o.get("revenue_by_region") if isinstance(o.get("revenue_by_region"), dict) else {}
    chk("west-dropped", "West" not in rv and "West" not in (o.get("top_products") or []) and bool(rv))
    chk("regions-exact", sorted(rv) == sorted(E["rev"]), sorted(rv))
    for g, v in E["rev"].items():
        chk("revenue-" + g, isinstance(rv.get(g), (int, float)) and abs(rv[g] - v) < 0.005, rv.get(g))
    chk("top-products-by-revenue", o.get("top_products") == E["top"], o.get("top_products"))
    chk("total-revenue", isinstance(o.get("total_revenue"), (int, float)) and abs(o["total_revenue"] - E["tot"]) < 0.005, o.get("total_revenue"))

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
