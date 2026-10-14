#!/usr/bin/env python3
"""check.py for 12-plan-revision: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"h": "672bef6125d2b7dcd431542164c091f8df2b4d86e1959d5e77c27a55ff2d3d70", "s": {"### Step 1: Prepare the rig": ["- Stop the dev server.", "- Confirm both GPUs are idle.", "- (see Step 7) for the stop procedure."], "### Step 2: Fetch weights": ["- Download the checkpoint.", "- AC-2.1: checksums match the manifest"], "### Step 3: Warm-up run": ["- Run one throwaway request.", "- Discard its timing.", "- AC-3.1: server answers 200 on /health"], "### Step 4: Quantize": ["- Run the fp8 recipe.", "- Needs the output of Step 2.", "- AC-4.1: fp8 files exist"], "### Step 5: Bench and verify": ["- Run the 5-run bench.", "- Run the quality gate.", "- AC-5.1: median decode recorded in out/bench.json", "- AC-5.2: score within 1 point of baseline"], "### Step 6: Write results": ["- Fill the results template.", "- Cite the Step 5 numbers and the Step 5 score."], "### Step 7: Teardown": ["- Remove temp files.", "- Restart the dev server."]}, "t": ["Prepare the rig", "Fetch weights", "Warm-up run", "Quantize", "Bench and verify", "Write results", "Teardown"]}')
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
    s = rd("plan-v2.md") or ""
    chk("plan-v1-untouched", hashlib.sha256((rd("plan.md") or "").encode()).hexdigest() == E["h"])
    toc = re.findall(r"(?m)^(\d+)\. (.+)$", s)
    chk("contents-matches", [(int(a), b.strip()) for a, b in toc] == [(i + 1, t) for i, t in enumerate(E["t"])], toc)
    heads = re.findall(r"(?m)^### Step (\d+): (.+)$", s)
    chk("headings-match", [(int(a), b.strip()) for a, b in heads] == [(i + 1, t) for i, t in enumerate(E["t"])], heads)
    secs = {}
    for blk in re.split(r"(?m)^(?=### Step )", s)[1:]:
        ls = [l.rstrip() for l in blk.splitlines() if l.strip()]; secs[ls[0]] = ls[1:]
    for h, body in E["s"].items():
        chk("section-" + h.split(":")[1].strip().lower().replace(" ", "-"), secs.get(h) == body, secs.get(h))
    chk("no-stale-refs", "legacy" not in s.lower() and "??" not in s)

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
