#!/usr/bin/env python3
"""check.py for 30-room-booking-queue: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"f": [{"date": "2026-10-14", "end": "10:00", "id": "BK-001", "room": "Aspen", "start": "09:00", "who": "Marta Voss"}, {"date": "2026-10-14", "end": "10:30", "id": "BK-004", "room": "Dogwood", "start": "09:30", "who": "Lee Park"}, {"date": "2026-10-14", "end": "12:00", "id": "BK-007", "room": "Aspen", "start": "10:00", "who": "Dana Whit"}, {"date": "2026-10-14", "end": "12:30", "id": "BK-009", "room": "Birch", "start": "11:00", "who": "Omar Reyes"}, {"date": "2026-10-14", "end": "12:00", "id": "BK-013", "room": "Cedar", "start": "11:30", "who": "Marta Voss"}, {"date": "2026-10-14", "end": "15:00", "id": "BK-003", "room": "Aspen", "start": "13:00", "who": "Priya Shah"}, {"date": "2026-10-15", "end": "12:00", "id": "BK-011", "room": "Cedar", "start": "09:00", "who": "Omar Reyes"}, {"date": "2026-10-15", "end": "11:00", "id": "BK-012", "room": "Birch", "start": "10:00", "who": "Lee Park"}, {"date": "2026-10-15", "end": "12:00", "id": "BK-005", "room": "Aspen", "start": "11:00", "who": "Omar Reyes"}, {"date": "2026-10-15", "end": "12:00", "id": "BK-010", "room": "Birch", "start": "11:30", "who": "Kim Lau"}], "l": [["R01", "ok", "BK-007"], ["R02", "ok", "BK-008"], ["R03", "ok", "BK-007"], ["R04", "rejected", "CONFLICT"], ["R05", "rejected", "CONFLICT"], ["R06", "ok", "BK-002"], ["R07", "ok", "BK-009"], ["R08", "rejected", "CONFLICT"], ["R09", "rejected", "REF_NOT_BOOKED"], ["R10", "rejected", "OUTSIDE_HOURS"], ["R11", "rejected", "BAD_ROOM"], ["R12", "rejected", "NOT_FOUND"], ["R13", "ok", "BK-010"], ["R14", "ok", "BK-006"], ["R15", "ok", "BK-003"], ["R16", "ok", "BK-011"], ["R17", "rejected", "OUTSIDE_HOURS"], ["R18", "rejected", "NO_ROOM"], ["R19", "rejected", "CONFLICT"], ["R20", "ok", "BK-012"], ["R21", "ok", "BK-012"], ["R22", "rejected", "CONFLICT"], ["R23", "ok", "BK-013"], ["R24", "ok", "BK-008"], ["R25", "rejected", "AMBIGUOUS"]]}')
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
    fb = jl("state/bookings.json")
    chk("final-state-exact", fb == E["f"], "differs" if fb is not None else "missing")
    chk("final-state-count", isinstance(fb, list) and len(fb) == len(E["f"]), None if not isinstance(fb, list) else len(fb))
    r = rows("log.csv")
    chk("log-header", (rd("log.csv") or "").splitlines()[:1] == ["request,outcome,detail"])
    got = {x["request"]: (x["outcome"], x["detail"]) for x in (r or [])}
    for rid, o, d in E["l"]:
        chk("log-" + rid, got.get(rid) == (o, d), got.get(rid))

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
