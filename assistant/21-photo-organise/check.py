#!/usr/bin/env python3
"""check.py for 21-photo-organise: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"h": {"organised/2025/12/20251231_235959_x100.jpg": "00a345c9e2e52a3dd70910395a7f6d26f7c82c6c7fa84b55b5a1758d1e404ba2", "organised/2026/08/20260814_172209_gr3.jpg": "f536bb486db1eb3cd92b58c62a21cbe1f47a32636abf5ab7db0ae02e85298059", "organised/2026/08/20260814_172209_x100-2.jpg": "23642381b97bb4de62077087a923b1640bdb970a5cf6c9dd16b45a6ca64bf9dd", "organised/2026/08/20260814_172209_x100.jpg": "74699f9debb0ff1fcfe16e54e04a513ed2c6b155ca2453adb7d35406a24f38c3", "organised/2026/09/20260902_080145_gr3.jpg": "1944107c42794761fa79eb669860e8894f099296e0045a533c69becf32a9e1df", "organised/2026/09/20260902_080146_x100.jpg": "8f29a82103678cb228b0d1bbd237a455ff76f350a27e974abaffe5e29d5b1133"}, "m": "old,new\\nphotos/IMG_0001.jpg,organised/2026/08/20260814_172209_x100.jpg\\nphotos/IMG_0002.jpg,organised/2026/08/20260814_172209_x100-2.jpg\\nphotos/IMG_0003.jpg,organised/2026/08/20260814_172209_gr3.jpg\\nphotos/IMG_0004.jpg,organised/2026/09/20260902_080145_gr3.jpg\\nphotos/IMG_0005.jpg,organised/2025/12/20251231_235959_x100.jpg\\nphotos/IMG_0006.jpg,organised/2026/09/20260902_080146_x100.jpg\\n"}')
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
    r = rows("manifest.csv")
    chk("manifest-exact", (rd("manifest.csv") or "") == E["m"], "manifest differs")
    chk("photos-dir-empty", not os.path.isdir(p("photos")) or not os.listdir(p("photos")), os.listdir(p("photos")) if os.path.isdir(p("photos")) else "")
    for new, h in E["h"].items():
        f = p(new)
        chk("photo-" + new.split("/")[-1], os.path.isfile(f) and hashlib.sha256(open(f, "rb").read()).hexdigest() == h)
    sc = sum(1 for new in E["h"] if os.path.isfile(p(new[:-4] + ".json")))
    chk("sidecars-moved", sc == len(E["h"]), sc)

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
