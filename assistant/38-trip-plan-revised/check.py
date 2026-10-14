#!/usr/bin/env python3
"""check.py for 38-trip-plan-revised: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"lis": ["F06", "F07", "F08", "F09", "F10", "F11", "F12", "F13"], "ok2": ["F14", "F15", "F16", "F18", "F19", "F21"], "p": {"flights": ["F01", "F16", "F30"], "hotels": {"BER": "H-BER-5", "MAD": "H-MAD-5"}, "total_usd": 1373}}')
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
    o = jl("plan.json")
    chk("plan-parses", isinstance(o, dict) and set(o) == {"flights", "hotels", "total_usd"}, o)
    o = o if isinstance(o, dict) else {}
    chk("no-lisbon", "LIS" not in (o.get("hotels") or {}) and not any(f in E["lis"] for f in (o.get("flights") or [])))
    chk("three-flights", isinstance(o.get("flights"), list) and len(o["flights"]) == 3, o.get("flights"))
    chk("flights-exact", o.get("flights") == E["p"]["flights"], o.get("flights"))
    chk("berlin-madrid-leg-constraints", isinstance(o.get("flights"), list) and len(o["flights"]) == 3 and o["flights"][1] in E["ok2"], (o.get("flights") or [None] * 3)[1])
    chk("hotels-exact", o.get("hotels") == E["p"]["hotels"], o.get("hotels"))
    chk("total-exact", isinstance(o.get("total_usd"), (int, float)) and abs(o["total_usd"] - E["p"]["total_usd"]) < 0.005, o.get("total_usd"))
    chk("within-budget-cap", isinstance(o.get("total_usd"), (int, float)) and o["total_usd"] <= 2800)

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
