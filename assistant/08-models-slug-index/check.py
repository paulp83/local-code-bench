#!/usr/bin/env python3
"""check.py for 08-models-slug-index: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"m": ["llama-8b-q8", "qfn-awq"], "r": [["GLM-5.3-Flash-UD-Q4_K_XL", "glm53-flash-q4", 8400, 3], ["Qwen3.8-27B-Q4_K_M", "qwen-27b-q4", 6800, 2], ["Qwen3.8-Flash-Next-fp8", "qfn-fp8", 8730, 4], ["glm5.3-flash_Q6_K", "glm53-flash-q6", 7400, 2], ["misc-notes", "", 50, 1], ["qwen3.8-flash-next_FP8_old", "", 1350, 2]]}')
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
    r = rows("index.csv")
    chk("index-parses", bool(r))
    if r:
        chk("header-exact", (rd("index.csv") or "").splitlines()[0].strip() == "folder,slug,size_bytes,files")
        chk("sorted-folders", [x["folder"] for x in r] == [e[0] for e in E["r"]], [x["folder"] for x in r])
        got = {x["folder"]: (x["slug"], x["size_bytes"], x["files"]) for x in r}
        for f, s, z, n in E["r"]:
            chk("row-" + f, got.get(f) == (s, str(z), str(n)), got.get(f))
    chk("missing-exact", jl("missing.json") == E["m"], jl("missing.json"))

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
