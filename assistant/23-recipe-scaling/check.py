#!/usr/bin/env python3
"""check.py for 23-recipe-scaling: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"r": [["rolled oats", "900 ml"], ["milk", "600 ml"], ["eggs", "5"], ["butter", "75 ml"], ["baking powder", "25 ml"], ["flour", "420 g"], ["salt", "1 pinch"]]}')
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
    s = rd("recipe-10.md") or ""
    chk("title-line", s.splitlines()[:1] == ["# Oat pancakes (serves 10)"] if s else False)
    tb = [[c.strip() for c in l.strip().strip("|").split("|")] for l in s.splitlines() if l.strip().startswith("|")]
    chk("header", tb[:1] == [["ingredient", "amount"]], tb[:1])
    got = dict((r[0], r[1]) for r in tb[2:] if len(r) == 2)
    chk("order", [r[0] for r in tb[2:]] == [e[0] for e in E["r"]])
    for k, v in E["r"]:
        chk("row-" + k.replace(" ", "-"), got.get(k) == v, got.get(k))

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
