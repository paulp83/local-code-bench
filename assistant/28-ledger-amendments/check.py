#!/usr/bin/env python3
"""check.py for 28-ledger-amendments: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"b": {"ACC-01": -15252819, "ACC-02": -16532550, "ACC-03": -19518351, "ACC-04": -15346105, "ACC-05": -10296302, "ACC-06": -18086502, "ACC-07": -17852581, "ACC-08": -19953143, "ACC-09": -16933496, "ACC-10": -20303016, "ACC-11": -17405716, "ACC-12": -16392504}, "i": ["emails/msg-004.txt", "emails/msg-009.txt", "emails/msg-014.txt", "emails/msg-021.txt", "emails/msg-023.txt", "emails/msg-028.txt", "emails/msg-032.txt", "emails/msg-037.txt", "emails/msg-038.txt", "emails/msg-039.txt", "emails/msg-053.txt", "emails/msg-056.txt", "emails/msg-064.txt", "emails/msg-065.txt"]}')
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
    b = jl("balances.json"); ig = jl("ignored_emails.json")
    chk("balances-parses", isinstance(b, dict))
    b = b if isinstance(b, dict) else {}
    chk("balances-all-12-accounts", set(b) == set(E["b"]), sorted(b))
    good = [a for a in E["b"] if b.get(a) == E["b"][a] and type(b.get(a)) is int]
    for a in sorted(E["b"]):
        chk("balance-" + a, a in good, b.get(a))
    chk("ignored-emails-exact", ig == E["i"], None if not isinstance(ig, list) else "got %d expected %d" % (len(ig), len(E["i"])))
    chk("ignored-emails-sorted", isinstance(ig, list) and ig == sorted(ig))

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
