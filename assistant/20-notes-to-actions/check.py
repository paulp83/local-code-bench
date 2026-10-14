#!/usr/bin/env python3
"""check.py for 20-notes-to-actions: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"a": [{"due": "2026-10-09", "owner": "Dana", "task": "send the vendor quote"}, {"due": "2026-10-13", "owner": "Lee", "task": "review the rig report"}, {"due": "2026-10-21", "owner": "Priya", "task": "draft the results post"}, {"due": "2026-10-31", "owner": "Omar", "task": "book the test window"}, {"due": "2026-10-08", "owner": "Dana", "task": "update the runbook"}, {"due": "2026-10-19", "owner": "Lee", "task": "rerun the bench"}, {"due": "2026-10-12", "owner": "Priya", "task": "confirm the budget"}]}')
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
    a = jl("actions.json")
    chk("is-list-of-expected-length", isinstance(a, list) and len(a) == len(E["a"]), None if not isinstance(a, list) else len(a))
    if isinstance(a, list):
        norm = lambda s: re.sub(r"[^a-z0-9 ]", "", str(s).lower()).strip()
        for i, e in enumerate(E["a"]):
            g = a[i] if i < len(a) and isinstance(a[i], dict) else {}
            chk("owner-%d-%s" % (i + 1, e["owner"]), g.get("owner") == e["owner"], g.get("owner"))
            chk("due-%d-%s" % (i + 1, e["owner"]), g.get("due") == e["due"], g.get("due"))
            chk("task-%d-%s" % (i + 1, e["owner"]), norm(g.get("task")) == norm(e["task"]), g.get("task"))

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
