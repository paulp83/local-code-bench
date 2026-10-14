#!/usr/bin/env python3
"""check.py for 26-invoice-reconciliation: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"c": [["P03", "44.50"], ["P04", "410.00"], ["P06", "100.00"]], "r": [["INV-1001", "paid", "500.00", "0.00"], ["INV-1002", "paid", "250.00", "0.00"], ["INV-1003", "overdue", "800.00", "400.00"], ["INV-1004", "paid", "300.00", "0.00"], ["INV-1005", "paid", "75.50", "0.00"], ["INV-1006", "paid", "980.00", "0.00"], ["INV-1007", "unpaid", "0.00", "410.00"]]}')
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
    r = rows("reconcile.csv")
    chk("reconcile-header", (rd("reconcile.csv") or "").splitlines()[:1] == ["inv_id,status,paid,outstanding"])
    got = [(x["inv_id"], x["status"], x["paid"], x["outstanding"]) for x in (r or [])]
    chk("reconcile-order", [g[0] for g in got] == [e[0] for e in E["r"]])
    for e in E["r"]:
        g = [x for x in got if x[0] == e[0]]
        chk("invoice-" + e[0], g == [tuple(e)], g)
    c = rows("credits.csv")
    chk("credits-header", (rd("credits.csv") or "").splitlines()[:1] == ["pay_id,credit"])
    chk("credits-exact", [(x["pay_id"], x["credit"]) for x in (c or [])] == [tuple(x) for x in E["c"]], c)

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
