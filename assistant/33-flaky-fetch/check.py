#!/usr/bin/env python3
"""check.py for 33-flaky-fetch: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"r": ["i04", "i09", "i11", "i17"], "t": 951297}')
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
    man = {x["id"]: x for x in (rows("manifest.csv") or [])}
    for i in sorted(man):
        f = p("data", i + ".json")
        ok = os.path.isfile(f) and hashlib.sha256(open(f, "rb").read()).hexdigest() == man[i]["sha256"]
        chk("item-" + i, ok)
    chk("all-20-items", sum(1 for i in man if os.path.isfile(p("data", i + ".json"))) == 20)
    s = jl("summary.json")
    chk("summary-count", isinstance(s, dict) and s.get("count") == 20)
    chk("summary-total", isinstance(s, dict) and s.get("total_amount_cents") == E["t"], s.get("total_amount_cents") if isinstance(s, dict) else None)
    chk("summary-retried", isinstance(s, dict) and s.get("retried") == E["r"], s.get("retried") if isinstance(s, dict) else None)
    log = (rd(".remote/.state/calls.log") or "").split()
    chk("fetched-via-script", all(i in log for i in man), "calls.log missing ids" )
    chk("retries-actually-made", all(log.count(i) >= 2 for i in E["r"]))

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
