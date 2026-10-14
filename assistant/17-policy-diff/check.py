#!/usr/bin/env python3
"""check.py for 17-policy-diff: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"added": ["2.3", "4.3"], "changed": ["2.1", "3.2"], "removed": ["2.2"], "renumbered": [{"from": "2.3", "title": "Links", "to": "2.2"}]}')
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
    o = jl("changes.json")
    chk("parses-with-4-keys", isinstance(o, dict) and set(o) == {"added", "removed", "changed", "renumbered"}, o)
    if isinstance(o, dict):
        for k in ("added", "removed", "changed", "renumbered"):
            chk("key-" + k, o.get(k) == E[k], o.get(k))

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
