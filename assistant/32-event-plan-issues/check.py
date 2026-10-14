#!/usr/bin/env python3
"""check.py for 32-event-plan-issues: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"g": 85, "i": [{"code": "CAPACITY", "files": ["rsvp.csv", "venue.json"]}, {"code": "CATERING_SHORT", "files": ["catering.csv", "rsvp.csv"]}, {"code": "OVER_BUDGET", "files": ["budget.md", "quotes.csv"]}, {"code": "TIME_MISMATCH", "files": ["schedule.md"]}, {"code": "WEEKDAY_MISMATCH", "files": ["schedule.md"]}]}')
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
    iss = jl("issues.json")
    chk("issues-parses", isinstance(iss, list))
    got = {o.get("code"): o.get("files") for o in iss if isinstance(o, dict)} if isinstance(iss, list) else {}
    exp = {o["code"]: o["files"] for o in E["i"]}
    chk("issues-sorted-by-code", isinstance(iss, list) and [o.get("code") for o in iss if isinstance(o, dict)] == sorted(exp))
    for c in sorted(set(exp) | set(got)):
        if c in exp: chk("issue-found-" + c, c in got and got[c] == exp[c], got.get(c))
    chk("no-invented-issues", set(got) <= set(exp), sorted(set(got) - set(exp)))
    chk("issue-count-exact", isinstance(iss, list) and len(iss) == len(exp))
    s = rd("plan.md") or ""
    chk("plan-date", re.search(r"(?m)^Date: 2026-11-14\s*$", s) is not None)
    chk("plan-venue", re.search(r"(?m)^Venue: Harbor Hall\s*$", s) is not None)
    chk("plan-confirmed-guests", re.search(r"(?m)^Confirmed guests: %d\s*$" % E["g"], s) is not None, E["g"])
    chk("plan-open-issues", re.search(r"(?m)^Open issues: %d\s*$" % len(exp), s) is not None)

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
