#!/usr/bin/env python3
"""check.py for 13-inbox-triage: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"r": [["m00", "P1", "unassigned", "2026-10-09"], ["m01", "P1", "finance", "2026-10-12"], ["m02", "P2", "tooling", "2026-10-13"], ["m03", "P1", "unassigned", "2026-10-11"], ["m04", "P1", "unassigned", "2026-10-06"], ["m05", "P2", "docs", "2026-10-09"], ["m06", "P2", "finance", "2026-10-13"], ["m07", "P2", "hardware", "2026-10-13"], ["m08", "P2", "unassigned", "2026-10-13"], ["m09", "P2", "security", "2026-10-13"], ["m10", "P1", "hardware", "2026-10-12"], ["m11", "P3", "unassigned", "2026-10-16"], ["m12", "P1", "finance", "2026-10-05"], ["m13", "P2", "tooling", "2026-10-13"], ["m14", "P1", "unassigned", "2026-10-08"], ["m15", "P3", "unassigned", "2026-10-16"], ["m16", "P2", "docs", "2026-10-14"], ["m17", "P2", "finance", "2026-10-14"], ["m18", "P1", "hardware", "2026-10-09"], ["m19", "P2", "unassigned", "2026-10-13"], ["m20", "P2", "security", "2026-10-12"], ["m21", "P1", "hardware", "2026-10-05"], ["m22", "P1", "unassigned", "2026-10-12"], ["m23", "P1", "finance", "2026-10-05"], ["m24", "P2", "tooling", "2026-10-13"], ["m25", "P1", "unassigned", "2026-10-07"], ["m26", "P1", "unassigned", "2026-10-05"], ["m27", "P1", "docs", "2026-10-12"], ["m28", "P1", "finance", "2026-10-13"], ["m29", "P1", "hardware", "2026-10-13"]]}')
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
    r = rows("triage.csv")
    chk("csv-parses", bool(r))
    if r:
        chk("header-exact", (rd("triage.csv") or "").splitlines()[0].strip() == "id,priority,owner,due")
        chk("ids-complete-sorted", [x["id"] for x in r] == [e[0] for e in E["r"]])
        got = {x["id"]: x for x in r}
        for col, idx in (("priority", 1), ("owner", 2), ("due", 3)):
            good = sum(1 for e in E["r"] if got.get(e[0], {}).get(col) == e[idx])
            chk("column-%s-all-correct" % col, good == len(E["r"]), "%d/%d" % (good, len(E["r"])))
            chk("column-%s-at-least-27" % col, good >= 27)

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
