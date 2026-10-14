"""Shared emit machinery for the assistant task set. Stdlib only."""
import json, os, random, shutil, textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS = []
DIFF = {}  # id -> easy|medium|hard

PRELUDE = '''#!/usr/bin/env python3
"""check.py for {id}: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads({exp!r})
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
'''
POST = '''
except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
'''

def task(id, source, category, est, title, md, workspace, check, reference, exp=None, notes="", needs_web=False,
         axis=None, spec=None, naive=None):
    """spec: [(check-name-prefix, verbatim quote from task.md)]; naive: files overlaying the seed that a lazy one-liner would produce."""
    TASKS.append(dict(id=id, source=source, category=category, est=est, md=md, ws=workspace, check=check,
                      ref=reference, exp=exp if exp is not None else {}, notes=notes, title=title, axis=axis, spec=spec, naive=naive))

def _w(base, files):
    for rel, c in files.items():
        f = base / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(c, bytes): f.write_bytes(c)
        elif isinstance(c, tuple) and c[0] == "link": os.symlink(c[1], f)
        elif isinstance(c, tuple) and c[0] == "exec": f.write_text(c[1]); os.chmod(f, 0o755)
        else: f.write_text(c)

def run_check(d, overlay=None):
    """Copy workspace (symlinks kept, as run_assistant.py does), apply an overlay dir, run check.py. Returns CompletedProcess."""
    import subprocess, sys, tempfile
    with tempfile.TemporaryDirectory() as td:
        w = Path(td) / "w"
        shutil.copytree(d / "workspace", w, symlinks=True)
        if overlay is not None and Path(overlay).exists():
            shutil.copytree(overlay, w, symlinks=True, dirs_exist_ok=True)
            dl = w / "_delete.txt"
            if dl.exists():
                for rel in dl.read_text().split():
                    t = w / rel
                    shutil.rmtree(t) if t.is_dir() and not t.is_symlink() else t.unlink()
                dl.unlink()
        return subprocess.run([sys.executable, "-I", str(d / "check.py"), str(w)], capture_output=True, text=True)

def names_of(out):
    return [l.split(" ", 1)[1].split(":", 1)[0] for l in out.splitlines() if l.startswith(("PASS ", "FAIL ")) and not l.startswith(("PASS:", "FAIL:"))]

def emit():
    for t in TASKS:
        d = ROOT / t["id"]
        if d.exists(): shutil.rmtree(d)
        d.mkdir(parents=True)
        md = textwrap.dedent(t["md"]).strip() + "\n"
        (d / "task.md").write_text(md)
        _w(d / "workspace", t["ws"])
        _w(d / "reference", t["ref"])
        body = textwrap.indent(textwrap.dedent(t["check"]).strip("\n"), "    ")
        (d / "check.py").write_text(PRELUDE.format(id=t["id"], exp=json.dumps(t["exp"], sort_keys=True, default=str)) + body + "\n" + POST)
        os.chmod(d / "check.py", 0o755)
        if t["naive"] is not None:
            nd = ROOT / "_build" / "naive" / t["id"]
            if nd.exists(): shutil.rmtree(nd)
            _w(nd, t["naive"])
        meta = dict(id=t["id"], set="hard-v1" if t["axis"] else None, axis=t["axis"], source=t["source"], category=t["category"],
                    difficulty=DIFF.get(t["id"], "hard"), est_minutes=t["est"], needs_web=False, notes=t["notes"])
        if t["spec"] is not None:
            r = run_check(d, d / "reference")
            sm = {}
            for n in names_of(r.stdout):
                hits = [(len(p), q) for p, q in t["spec"] if n.startswith(p)]
                assert hits, f"{t['id']}: no spec entry for check {n!r}"
                q = max(hits)[1]
                assert q in md, f"{t['id']}: quote not verbatim in task.md: {q!r}"
                sm[n] = q
            meta["spec_map"] = sm
        (d / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print("emitted", len(TASKS))
