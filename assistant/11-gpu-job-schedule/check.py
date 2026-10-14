#!/usr/bin/env python3
"""check.py for 11-gpu-job-schedule: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"mk": 215}')
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
    jobs = {j["name"]: j for j in jl("jobs.json") or []}
    s = jl("schedule.json")
    ok = isinstance(s, dict) and set(s) == set(jobs) and all(isinstance(v, int) and not isinstance(v, bool) for v in s.values())
    chk("schedule-complete-ints", ok, s)
    if ok:
        end = lambda n: s[n] + jobs[n]["duration_min"]
        chk("not-before-respected", all(s[n] >= jobs[n]["not_before_min"] for n in jobs))
        chk("dependencies-respected", all(s[n] >= end(d) for n in jobs for d in jobs[n]["after"]))
        pts = sorted(set(s.values()))
        chk("gpu-capacity-never-exceeded", all(sum(jobs[n]["gpus"] for n in jobs if s[n] <= t < end(n)) <= 2 for t in pts))
        mk = max(end(n) for n in jobs)
        chk("makespan-optimal", mk == E["mk"], "makespan %d, optimum %d" % (mk, E["mk"]))
        chk("makespan-within-10-percent", mk <= E["mk"] * 1.10, mk)

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
