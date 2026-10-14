#!/usr/bin/env python3
"""Validate club-3090 PR candidates as agent tasks (FAIL at base + PR tests, PASS at merge), offline in Docker.

usage: validate.py [--jobs N] [--only PR,PR]
Reads candidates.json, writes validated.json + logs/<pr>-{base,head}.log.
"""
import argparse, concurrent.futures as cf, json, os, subprocess, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path(os.environ.get("CLUB3090_REPO", "club-3090")).expanduser().resolve()  # a clone of noonghunna/club-3090
IMAGE = "club-tasks-env:1"
TIMEOUT = 300


def git(*a, **kw):
    return subprocess.run(["git", "-C", str(REPO), *a], check=True, capture_output=True, **kw).stdout


def export(commit: str, dst: Path):
    dst.mkdir(parents=True)
    tar = git("archive", commit)
    subprocess.run(["tar", "-x", "-C", str(dst)], input=tar, check=True)


def run_tests(tree: Path, tests: list[str]) -> dict:
    """Run each test file in the offline container; return {test: exit_code}."""
    script = "set +e; cd /testbed; for t in \"$@\"; do " \
             f"case $t in *.py) timeout {TIMEOUT} python3 $t ;; *) timeout {TIMEOUT} bash $t ;; esac " \
             ">/tmp/out 2>&1; rc=$?; echo \"RC $rc $t\"; tail -15 /tmp/out | sed 's/^/    /'; done"
    p = subprocess.run(["docker", "run", "--rm", "--network", "none", "--user", f"{os.getuid()}:{os.getgid()}", "-e", "HOME=/tmp", "-v", f"{tree}:/testbed", IMAGE,
                        "bash", "-c", script, "_", *tests], capture_output=True, text=True,
                       timeout=TIMEOUT * len(tests) + 120)
    rcs = {}
    for line in p.stdout.splitlines():
        if line.startswith("RC "):
            _, rc, t = line.split(" ", 2)
            rcs[t] = int(rc)
    return rcs, p.stdout + p.stderr


def validate(c: dict) -> dict:
    n, merge = c["n"], c["merge"]
    base = git("rev-parse", f"{merge}^").decode().strip()
    present = [t for t in c["tests"] if subprocess.run(["git", "-C", str(REPO), "cat-file", "-e", f"{merge}:{t}"]).returncode == 0]
    out = dict(c, base=base, tests=present)
    if not present:
        return dict(out, ok=False, why="test files deleted in PR")
    with tempfile.TemporaryDirectory(dir=HERE / "tmp") as td:
        td = Path(td)
        export(base, td / "base")
        for t in present:  # the PR's versions of its tests, on the base tree
            dst = td / "base" / t
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(git("show", f"{merge}:{t}"))
        b_rc, b_log = run_tests(td / "base", present)
        export(merge, td / "head")
        h_rc, h_log = run_tests(td / "head", present)
    (HERE / "logs" / f"{n}-base.log").write_text(b_log)
    (HERE / "logs" / f"{n}-head.log").write_text(h_log)
    f2p = [t for t in present if b_rc.get(t, 1) != 0 and h_rc.get(t) == 0]
    p2p_broken = [t for t in present if h_rc.get(t) != 0]
    ok = bool(f2p) and not p2p_broken
    why = "ok" if ok else ("tests fail at head (env/GPU/docker/network?)" if p2p_broken else "tests already pass at base")
    return dict(out, ok=ok, why=why, fail_to_pass=f2p, base_rc=b_rc, head_rc=h_rc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--only")
    a = ap.parse_args()
    (HERE / "logs").mkdir(exist_ok=True)
    (HERE / "tmp").mkdir(exist_ok=True)
    cands = json.load(open(HERE / "candidates.json"))
    if a.only:
        keep = {int(x) for x in a.only.split(",")}
        cands = [c for c in cands if c["n"] in keep]
    res = []
    t0 = time.time()
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for r in ex.map(validate, cands):
            res.append(r)
            print(f"[{time.time() - t0:6.0f}s] #{r['n']}: {r['why']}", flush=True)
    json.dump(res, open(HERE / "validated.json", "w"), indent=1)
    print(f"{sum(r['ok'] for r in res)} / {len(res)} valid")


if __name__ == "__main__":
    main()
