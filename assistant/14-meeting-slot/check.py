#!/usr/bin/env python3
"""check.py for 14-meeting-slot: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"s": "20261014T100000Z"}')
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
    s = rd("meeting.ics") or ""
    chk("one-vevent", s.count("BEGIN:VEVENT") == 1 and s.count("END:VEVENT") == 1)
    ds = re.search(r"(?m)^DTSTART:(\d{8}T\d{6}Z)\s*$", s); de = re.search(r"(?m)^DTEND:(\d{8}T\d{6}Z)\s*$", s)
    chk("dtstart-dtend-utc-format", bool(ds and de))
    chk("summary-sync", re.search(r"(?m)^SUMMARY:Sync\s*$", s) is not None)
    if ds and de:
        a = ds.group(1); b = de.group(1)
        from datetime import datetime as D
        pa = D.strptime(a, "%Y%m%dT%H%M%SZ"); pb = D.strptime(b, "%Y%m%dT%H%M%SZ")
        chk("duration-45-min", (pb - pa).total_seconds() == 45 * 60)
        chk("earliest-valid-slot", a == E["s"], "got %s expected %s" % (a, E["s"]))

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
