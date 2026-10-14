#!/usr/bin/env python3
"""check.py for 06-job-chain-status: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"r": [{"attempts": "1", "duration_s": "278", "end": "2026-10-04T01:04:41Z", "result": "ok", "stage": "fetch", "start": "2026-10-04T01:00:03Z"}, {"attempts": "2", "duration_s": "342", "end": "2026-10-04T01:15:02Z", "result": "ok", "stage": "quant", "start": "2026-10-04T01:09:20Z"}, {"attempts": "1", "duration_s": "1105", "end": "2026-10-04T01:33:30Z", "result": "ok", "stage": "bench", "start": "2026-10-04T01:15:05Z"}, {"attempts": "1", "duration_s": "389", "end": "2026-10-04T01:40:00Z", "result": "failed", "stage": "quality", "start": "2026-10-04T01:33:31Z"}, {"attempts": "0", "duration_s": "", "end": "", "result": "skipped", "stage": "report", "start": ""}, {"attempts": "0", "duration_s": "", "end": "", "result": "skipped", "stage": "publish", "start": ""}]}')
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
    r = rows("status.csv")
    chk("csv-parses", r is not None and len(r) > 0)
    if r:
        chk("header-exact", (rd("status.csv") or "").splitlines()[0].strip() == "stage,attempts,start,end,result,duration_s")
        chk("stage-order", [x.get("stage") for x in r] == [e["stage"] for e in E["r"]], [x.get("stage") for x in r])
        got = {x.get("stage"): {k: (v or "").strip() for k, v in x.items()} for x in r}
        for e in E["r"]:
            chk("row-" + e["stage"], got.get(e["stage"]) == e, got.get(e["stage"]))

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
