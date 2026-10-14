#!/usr/bin/env python3
"""check.py for 04-archive-filing: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"doc": "---\\ntitle: Draft result\\ndate: 2026-10-04\\nmodel: Qwen3.8_Flash Next\\nquant: UD-Q4_K_XL\\ntype: bench\\n---\\n\\n# Bench run\\n\\nEight runs, median decode 71.3 tok/s.\\n\\nVerdict: stable at 71 tok/s, no stalls over 2 h\\n", "idx": "# Archive index\\n\\n## 2026-09\\n\\n| date | slug | kind | file | verdict |\\n|---|---|---|---|---|\\n| 2026-09-02 | glm-5-3-flash-q4 | rig | 2026-09-02_glm-5-3-flash-q4_rig.md | fits on 2 cards, 62 tok/s |\\n| 2026-09-20 | qwen-flash-next-fp8 | bench | 2026-09-20_qwen-flash-next-fp8_bench.md | fastest decode so far |\\n\\n## 2026-10\\n\\n| date | slug | kind | file | verdict |\\n|---|---|---|---|---|\\n| 2026-10-01 | glm-5-3-flash-q6 | quality | 2026-10-01_glm-5-3-flash-q6_quality.md | no quality loss vs fp16 |\\n| 2026-10-04 | qwen3-8-flash-next-ud-q4-k-xl | bench | 2026-10-04_qwen3-8-flash-next-ud-q4-k-xl_bench.md | stable at 71 tok/s, no stalls over 2 h |\\n| 2026-10-07 | qwen-flash-next-fp8 | rig | 2026-10-07_qwen-flash-next-fp8_rig.md | OOM above 64k context |\\n", "name": "2026-10-04_qwen3-8-flash-next-ud-q4-k-xl_bench.md", "names": ["2026-09-02_glm-5-3-flash-q4_rig.md", "2026-09-20_qwen-flash-next-fp8_bench.md", "2026-10-01_glm-5-3-flash-q6_quality.md", "2026-10-04_qwen3-8-flash-next-ud-q4-k-xl_bench.md", "2026-10-07_qwen-flash-next-fp8_rig.md"], "old": ["| 2026-09-02 | glm-5-3-flash-q4 | rig | 2026-09-02_glm-5-3-flash-q4_rig.md | fits on 2 cards, 62 tok/s |", "| 2026-09-20 | qwen-flash-next-fp8 | bench | 2026-09-20_qwen-flash-next-fp8_bench.md | fastest decode so far |", "| 2026-10-01 | glm-5-3-flash-q6 | quality | 2026-10-01_glm-5-3-flash-q6_quality.md | no quality loss vs fp16 |", "| 2026-10-07 | qwen-flash-next-fp8 | rig | 2026-10-07_qwen-flash-next-fp8_rig.md | OOM above 64k context |"], "row": "| 2026-10-04 | qwen3-8-flash-next-ud-q4-k-xl | bench | 2026-10-04_qwen3-8-flash-next-ud-q4-k-xl_bench.md | stable at 71 tok/s, no stalls over 2 h |"}')
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
    t = "archive/results/" + E["name"]
    chk("file-named-correctly", rd(t) == E["doc"], "expected " + E["name"])
    chk("draft-removed-from-inbox", not os.path.exists(p("inbox/result-draft.md")))
    chk("no-stray-files-in-results", sorted(os.listdir(p("archive/results"))) == sorted(E["names"]), sorted(os.listdir(p("archive/results"))))
    s = rd("archive/INDEX.md") or ""
    chk("index-matches-expected", s.strip() == E["idx"].strip(), "index differs from expected text")
    chk("index-row-present", E["row"] in s)
    chk("old-rows-kept", all(l in s for l in E["old"]))
    chk("section-order", s.find("## 2026-09") < s.find("## 2026-10") and s.count("## ") == 2)

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
