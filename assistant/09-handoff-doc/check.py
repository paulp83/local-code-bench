#!/usr/bin/env python3
"""check.py for 09-handoff-doc: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"cmd": "bash scripts/run_quality.sh --slug glm53 --port 8000"}')
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
    s = rd("HANDOFF.md") or ""
    parts = re.split(r"(?m)^## +", s)
    secs = {}
    for part in parts[1:]:
        head, _, body = part.partition("\n"); secs[head.strip()] = body
    chk("headings-exact-order", [h.strip() for h in re.findall(r"(?m)^## +(.*)$", s)] == ["Done", "In progress", "Blockers", "Next"], list(secs))
    ids = lambda t: set(re.findall(r"\bT\d\b", t or ""))
    chk("done-has-T1-T2-only", ids(secs.get("Done")) == {"T1", "T2"}, ids(secs.get("Done")))
    chk("inprogress-T4-only", ids(secs.get("In progress")) == {"T4"}, ids(secs.get("In progress")))
    chk("blockers-T3-only", ids(secs.get("Blockers")) == {"T3"}, ids(secs.get("Blockers")))
    chk("blockers-exact-command", "`" + E["cmd"] + "`" in (secs.get("Blockers") or ""))
    chk("blockers-exit-status-3", re.search(r"\b3\b", secs.get("Blockers") or "") is not None)
    ip = (secs.get("In progress") or "")
    chk("inprogress-configs", "tp2-fp8" in ip and "tp2-awq" in ip)
    chk("next-script-path", "scripts/run_bench.sh" in (secs.get("Next") or ""))
    chk("todo-not-in-done-or-blockers", not ids(secs.get("Done")) & {"T5", "T6"} and not ids(secs.get("Blockers")) & {"T5", "T6"})
    chk("max-250-words", 0 < len(s.split()) <= 250, len(s.split()))

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
