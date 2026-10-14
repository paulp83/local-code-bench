#!/usr/bin/env python3
"""check.py for 27-notes-current-state: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"a": {"q1": "Wednesday", "q2": "Omar Reyes", "q3": 47000, "q4": "Cirrus", "q5": 3, "q6": "2026-10-15", "q7": 148500, "q8": "Platform"}}')
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
    a = jl("answers.json")
    chk("answers-parses", isinstance(a, dict))
    a = a if isinstance(a, dict) else {}
    for k, v in E["a"].items():
        chk(k, a.get(k) == v and type(a.get(k)) is type(v), a.get(k))

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
