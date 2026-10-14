#!/usr/bin/env python3
"""check.py for 18-contacts-cleanup: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"r": [["Dana Reyes", "dana.reyes@example.com", "+14155550132", "Acme"], ["Ira", "ira@example.com", "", ""], ["Lee Wu", "lee@example.org", "+442079460958", "LW Co"], ["M. Okafor", "mo@example.net", "+447700900123", "Okafor Ltd"], ["Pat", "pat@example.com", "", ""], ["Sam K", "", "+14155550188", "Kite"]], "s": {"input_rows": 9, "invalid_phones": 2, "output_rows": 6}}')
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
    r = rows("contacts_clean.csv")
    chk("header-exact", (rd("contacts_clean.csv") or "").splitlines()[:1] == ["name,email,phone,company"])
    got = [[x[k] for k in ("name", "email", "phone", "company")] for x in (r or [])]
    chk("row-count", len(got) == len(E["r"]), len(got))
    chk("rows-exact-in-order", got == E["r"], got)
    chk("all-emails-lowercase", all(g[1] == g[1].lower() for g in got))
    chk("all-phones-e164-or-empty", all(re.fullmatch(r"\+\d{8,15}", g[2]) or g[2] == "" for g in got))
    chk("summary-exact", jl("summary.json") == E["s"], jl("summary.json"))

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
