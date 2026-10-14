#!/usr/bin/env python3
"""check.py for 34-messy-orders-rejects: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"c": [["O1001", "Elm Street", "2026-08-06", "2089.23", "GBP"], ["O1002", "Fjord", "2026-08-21", "8767.63", "EUR"], ["O1003", "Birch & Co", "2026-07-20", "2351.87", "GBP"], ["O1004", "Fjord", "2026-07-29", "324.57", "GBP"], ["O1006", "Fjord", "2026-08-14", "7238.01", "GBP"], ["O1007", "Fjord", "2026-07-19", "7309.91", "EUR"], ["O1008", "Fjord", "2026-07-16", "1479.82", "GBP"], ["O1009", "Gamma Industries", "2026-08-31", "8592.75", "GBP"], ["O1010", "Acme", "2026-08-04", "3452.34", "USD"], ["O1012", "Birch & Co", "2026-06-23", "1019.65", "GBP"], ["O1013", "Cobalt", "2026-07-11", "4432.41", "GBP"], ["O1014", "Acme", "2026-06-20", "7082.20", "EUR"], ["O1015", "Elm Street", "2026-06-25", "3898.12", "USD"], ["O1016", "Acme", "2026-08-07", "8141.72", "USD"], ["O1018", "Elm Street", "2026-06-27", "6264.82", "GBP"], ["O1019", "Cobalt", "2026-06-14", "6525.08", "EUR"], ["O1020", "Acme", "2026-07-20", "2405.08", "USD"], ["O1021", "Acme", "2026-08-03", "7240.19", "EUR"], ["O1022", "Acme", "2026-06-07", "3675.08", "GBP"], ["O1024", "Elm Street", "2026-09-08", "7796.00", "EUR"], ["O1025", "Cobalt", "2026-08-04", "7704.13", "USD"], ["O1026", "Dune \\"North\\"", "2026-07-13", "3587.41", "EUR"], ["O1027", "Fjord", "2026-08-18", "7919.12", "EUR"], ["O1028", "Birch & Co", "2026-07-29", "7780.82", "EUR"], ["O1030", "Elm Street", "2026-06-08", "8105.74", "GBP"], ["O1031", "Elm Street", "2026-08-05", "1991.59", "USD"], ["O1032", "Dune \\"North\\"", "2026-06-24", "6533.09", "USD"], ["O1033", "Cobalt", "2026-06-06", "6446.41", "USD"], ["O1035", "Fjord", "2026-07-27", "6205.83", "USD"], ["O1036", "Dune \\"North\\"", "2026-08-09", "7714.99", "GBP"], ["O1037", "Acme", "2026-08-24", "5003.24", "GBP"], ["O1038", "Birch & Co", "2026-08-08", "1875.19", "USD"], ["O1039", "Fjord", "2026-07-13", "6242.09", "EUR"], ["O1040", "Birch & Co", "2026-08-21", "7299.05", "EUR"]], "r": [["5", "MISSING_ID"], ["11", "BAD_DATE"], ["17", "BAD_AMOUNT"], ["23", "BAD_CURRENCY"], ["29", "BAD_COLUMNS"], ["34", "DUPLICATE_ID"]]}')
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
    c = list(csv.DictReader(io.StringIO((rd("clean.csv") or "").lstrip("\ufeff")))); rj = rows("rejects.csv")
    chk("clean-header", (rd("clean.csv") or "").lstrip("\ufeff").splitlines()[:1] == ["order_id,customer,date,amount,currency"])
    chk("rejects-header", (rd("rejects.csv") or "").splitlines()[:1] == ["record,reason"])
    got = [[x[k] for k in ("order_id", "customer", "date", "amount", "currency")] for x in (c or [])]
    chk("clean-row-count", len(got) == len(E["c"]), len(got))
    chk("clean-sorted", [g[0] for g in got] == sorted(g[0] for g in got))
    chk("clean-exact", got == E["c"], "first diff at %s" % next((i for i, (a, b) in enumerate(zip(got, E["c"])) if a != b), "-"))
    chk("clean-multiline-customer-flattened", any(g[1] == "Gamma Industries" for g in got))
    chk("clean-dates-iso", all(re.fullmatch(r"\d{4}-\d\d-\d\d", g[2]) for g in got) and bool(got))
    g2 = [[x["record"], x["reason"]] for x in (rj or [])]
    chk("rejects-exact", g2 == E["r"], g2)
    chk("rejects-none-silently-dropped", len(got) + len(g2) == 40, len(got) + len(g2))

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
