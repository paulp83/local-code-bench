#!/usr/bin/env python3
"""check.py for 25-config-edit: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"head": ["# club node settings", "[server]", "host = 0.0.0.0", "port = 8090   ; inline note stays", "max_ctx = 32768", "[logging]", "# keep this comment", "level = debug", "[gpu]"]}')
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
    import configparser
    s = rd("node.ini") or ""
    cp = configparser.ConfigParser(inline_comment_prefixes=(";",)); 
    try: cp.read_string(s); ok = True
    except Exception: ok = False
    chk("parses", ok)
    g = lambda a, b: cp.get(a, b, fallback=None) if ok else None
    chk("server-port", g("server", "port") == "8090")
    chk("logging-level", g("logging", "level") == "debug")
    chk("rotate-removed", ok and not cp.has_option("logging", "rotate"))
    chk("gpu-mem-fraction", g("gpu", "mem_fraction") == "0.85")
    chk("metrics-section", g("metrics", "enabled") == "true" and g("metrics", "port") == "9100")
    chk("untouched-values", g("server", "host") == "0.0.0.0" and g("server", "max_ctx") == "32768" and g("gpu", "devices") == "0,1")
    chk("comments-kept", "# club node settings" in s and "# keep this comment" in s and "; inline note stays" in s)
    chk("only-expected-lines-changed", [l for l in s.splitlines() if l.strip()][:len(E["head"])] == E["head"], "head changed")

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
