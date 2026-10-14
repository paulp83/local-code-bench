#!/usr/bin/env python3
"""check.py for 01-issue-effort-buckets: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"b": {"300": "small", "307": "large", "314": "small", "321": "large", "328": "large", "335": "large", "342": "medium", "349": "large", "356": "large", "363": "large", "370": "large", "377": "large", "384": "large", "391": "medium", "398": "large", "405": "medium", "412": "large", "419": "large"}, "j": [300, 314]}')
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
    b = jl("buckets.json"); j = jl("junior.json")
    chk("buckets-is-object", isinstance(b, dict))
    if isinstance(b, dict):
        chk("buckets-keys-complete", set(b) == set(E["b"]), "missing/extra keys")
        bad = [k for k in E["b"] if b.get(k) != E["b"][k]]
        chk("buckets-all-correct", not bad, "wrong: " + ",".join(bad[:6]))
        chk("buckets-at-least-14-correct", sum(b.get(k) == v for k, v in E["b"].items()) >= 14)
    chk("junior-exact", j == E["j"], j)

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
