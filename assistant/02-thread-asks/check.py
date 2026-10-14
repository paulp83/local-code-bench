#!/usr/bin/env python3
"""check.py for 02-thread-asks: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"s": {"11": ["please add a regression test", "Can you also run `bash scripts/preflight.sh` before pushing"], "2": ["Could you rerun with `--ctx 32768` and post the preflight output", "Also please attach the compose file you used"], "6": ["Can you confirm that GPU 0 stays under 20 GiB"], "9": ["Could you open a PR with the one-line fix", "Please link this issue in the description"]}}')
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
    a = jl("asks.json")
    chk("asks-is-list", isinstance(a, list))
    if isinstance(a, list):
        got = {}
        for o in a:
            if isinstance(o, dict): got[str(o.get("comment_id"))] = [re.sub(r"[.?!\s]+$", "", s).strip().lower() for s in o.get("requests", []) if isinstance(s, str)]
        chk("ids-exact", set(got) == set(E["s"]), sorted(got))
        chk("ordered-by-id", [o.get("comment_id") for o in a if isinstance(o, dict)] == sorted(int(k) for k in E["s"]))
        for k, v in E["s"].items():
            want = sorted(re.sub(r"[.?!\s]+$", "", s).strip().lower() for s in v)
            chk("comment-" + k, sorted(got.get(k, [])) == want, got.get(k))

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
