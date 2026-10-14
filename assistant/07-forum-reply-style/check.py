#!/usr/bin/env python3
"""check.py for 07-forum-reply-style: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"ban": ["great question", "i hope this helps", "happy to help", "delve", "leverage", "game-changer", "certainly"], "cmd": "bash launch.sh --slug glm53 --tp 2 --quant fp8"}')
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
    s = rd("reply.md") or ""
    chk("reply-exists", bool(s.strip()))
    chk("starts-with-mention", s.startswith("@sam-k"))
    chk("max-150-words", 0 < len(s.split()) <= 150, len(s.split()))
    chk("no-dashes", not re.search("[\u2013\u2014]", s))
    chk("no-exclamation", "!" not in s)
    low = s.lower()
    chk("no-banned-phrases", not [b for b in E["ban"] if b in low], [b for b in E["ban"] if b in low])
    chk("A1-decode-88.2", "88.2" in s)
    chk("A2-vram-31.4", "31.4" in s)
    chk("A3-context-65536", "65536" in s)
    chk("A4-command-in-backticks", "`" + E["cmd"] + "`" in s)
    chk("no-wrong-values", not re.search(r"\b(84\.9|51\.6|98304|32768|29\.7|27\.3)\b", s), "value from a different row")

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
