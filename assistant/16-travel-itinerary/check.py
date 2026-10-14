#!/usr/bin/env python3
"""check.py for 16-travel-itinerary: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"r": [["1", "QA101", "Seattle 2026-11-03 21:40", "Reykjavik 2026-11-04 06:15", "1h 35m", "1h 50m"], ["2", "QA202", "Reykjavik 2026-11-04 08:05", "Frankfurt 2026-11-04 12:50", "3h 45m", "6h 30m"], ["3", "QA303", "Frankfurt 2026-11-04 19:20", "Mumbai 2026-11-05 07:45", "7h 55m", "14h 25m"], ["4", "QA404", "Mumbai 2026-11-05 22:10", "Tokyo 2026-11-06 09:35", "7h 55m", "-"]], "t": "43h 55m"}')
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
    s = rd("itinerary.md") or ""
    tb = [[c.strip() for c in l.strip().strip("|").split("|")] for l in s.splitlines() if l.strip().startswith("|")]
    chk("header-exact", bool(tb) and tb[0] == ["leg", "flight", "depart (local)", "arrive (local)", "duration", "layover"], tb[:1])
    body = tb[2:] if len(tb) > 2 else []
    chk("four-rows", len(body) == 4)
    for i, e in enumerate(E["r"]):
        chk("row-%d" % (i + 1), i < len(body) and body[i] == e, body[i] if i < len(body) else None)
    chk("total-line", ("Total travel time: " + E["t"]) in s, E["t"])

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
