#!/usr/bin/env python3
"""check.py for 19-bank-categorisation: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"d": {"2026-07|dining": "-412.07", "2026-07|fuel": "-216.39", "2026-07|groceries": "-185.51", "2026-07|household": "-24.55", "2026-07|housing": "-900.00", "2026-07|income": "5000.00", "2026-07|subscriptions": "-323.32", "2026-07|transport": "-147.52", "2026-07|uncategorised": "-134.70", "2026-08|dining": "-225.27", "2026-08|fuel": "-236.25", "2026-08|groceries": "-300.51", "2026-08|household": "-16.03", "2026-08|housing": "-2700.00", "2026-08|income": "7500.00", "2026-08|transport": "-189.92", "2026-08|uncategorised": "-232.84", "2026-09|dining": "-257.69", "2026-09|fuel": "-317.61", "2026-09|groceries": "-338.07", "2026-09|household": "-13.95", "2026-09|housing": "-900.00", "2026-09|income": "7500.00", "2026-09|refunds": "34.55", "2026-09|subscriptions": "-177.52", "2026-09|transport": "-196.19", "2026-09|uncategorised": "-380.03"}, "r": [[["2026-07", "dining"], "-412.07"], [["2026-07", "fuel"], "-216.39"], [["2026-07", "groceries"], "-185.51"], [["2026-07", "household"], "-24.55"], [["2026-07", "housing"], "-900.00"], [["2026-07", "income"], "5000.00"], [["2026-07", "subscriptions"], "-323.32"], [["2026-07", "transport"], "-147.52"], [["2026-07", "uncategorised"], "-134.70"], [["2026-08", "dining"], "-225.27"], [["2026-08", "fuel"], "-236.25"], [["2026-08", "groceries"], "-300.51"], [["2026-08", "household"], "-16.03"], [["2026-08", "housing"], "-2700.00"], [["2026-08", "income"], "7500.00"], [["2026-08", "transport"], "-189.92"], [["2026-08", "uncategorised"], "-232.84"], [["2026-09", "dining"], "-257.69"], [["2026-09", "fuel"], "-317.61"], [["2026-09", "groceries"], "-338.07"], [["2026-09", "household"], "-13.95"], [["2026-09", "housing"], "-900.00"], [["2026-09", "income"], "7500.00"], [["2026-09", "refunds"], "34.55"], [["2026-09", "subscriptions"], "-177.52"], [["2026-09", "transport"], "-196.19"], [["2026-09", "uncategorised"], "-380.03"]]}')
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
    r = rows("budget.csv")
    chk("header-exact", (rd("budget.csv") or "").splitlines()[:1] == ["month,category,total"])
    got = [(x["month"], x["category"], x["total"]) for x in (r or [])]
    chk("row-count", len(got) == len(E["r"]), len(got))
    chk("sorted", got == sorted(got))
    d = {(a, b): c for a, b, c in got}
    bad = [k for k, v in E["d"].items() if d.get(tuple(k.split("|"))) != v]
    chk("all-cells-correct", not bad and len(d) == len(E["d"]), bad[:4])
    chk("at-least-90pct-cells", sum(d.get(tuple(k.split("|"))) == v for k, v in E["d"].items()) >= 0.9 * len(E["d"]))
    chk("transfers-ignored", not any("TRANSFER" in c for c in d) and len(d) > 0)

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
