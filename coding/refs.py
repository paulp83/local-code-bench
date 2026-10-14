#!/usr/bin/env python3
"""Reference pass per task (run once): hidden-test check counts at base (+tests) and at merge, and up to 5
regression tests (existing tests that reference the PR's source files and pass both before and after the PR).
Writes refs.json, keyed by PR number."""
import concurrent.futures as cf, json, os, tempfile
from pathlib import Path

from scoring import count_checks, export, put_tests, run_tests

HERE = Path(__file__).resolve().parent
MAX_P2P = 5


def ref(t: dict) -> dict:
    src = [f for f in t["files"] if not f.startswith("scripts/tests/")]
    with tempfile.TemporaryDirectory(dir=HERE / "tmp") as td:
        td = Path(td)
        export(t["base"], td / "base")
        export(t["merge"], td / "head")
        cands = []
        tests_dir = td / "base" / "scripts/tests"
        keys = {Path(s).name for s in src} | {Path(s).stem for s in src if Path(s).stem not in ("README", "AGENTS")}
        for f in sorted(tests_dir.glob("test-*")):
            rel = f"scripts/tests/{f.name}"
            if rel in t["tests"] or not f.is_file():
                continue
            txt = f.read_text(errors="ignore")
            if any(k and k in txt for k in keys):
                cands.append(rel)
        cands = cands[:15]  # bound the probe
        b = run_tests(td / "base", cands, timeout=120)
        h = run_tests(td / "head", cands, timeout=120)
        p2p = [c for c in cands if b[c]["rc"] == 0 and h[c]["rc"] == 0 and (td / "head" / c).exists()][:MAX_P2P]
        put_tests(td / "base", t["merge"], t["tests"])
        hb = run_tests(td / "base", t["tests"])
        hh = run_tests(td / "head", t["tests"])
    checks_base = [sum(x) for x in zip(*(count_checks(hb[x]["out"]) for x in t["tests"]))]
    checks_head = [sum(x) for x in zip(*(count_checks(hh[x]["out"]) for x in t["tests"]))]
    return dict(n=t["n"], src_files=src, p2p=p2p, p2p_candidates=len(cands),
                checks_base=dict(passed=checks_base[0], failed=checks_base[1]),
                checks_head=dict(passed=checks_head[0], failed=checks_head[1]))


def recount(t: dict) -> dict:
    """Hidden-test check counts only (regression-test selection unchanged)."""
    with tempfile.TemporaryDirectory(dir=HERE / "tmp") as td:
        td = Path(td)
        export(t["base"], td / "base")
        export(t["merge"], td / "head")
        put_tests(td / "base", t["merge"], t["tests"])
        hb, hh = run_tests(td / "base", t["tests"]), run_tests(td / "head", t["tests"])
    cb = [sum(x) for x in zip(*(count_checks(hb[x]["out"]) for x in t["tests"]))]
    ch = [sum(x) for x in zip(*(count_checks(hh[x]["out"]) for x in t["tests"]))]
    return dict(n=t["n"], checks_base=dict(passed=cb[0], failed=cb[1]), checks_head=dict(passed=ch[0], failed=ch[1]))


def main():
    (HERE / "tmp").mkdir(exist_ok=True)
    tasks = json.load(open(HERE / "tasks.json"))
    if "--checks-only" in os.sys.argv:
        refs = json.load(open(HERE / "refs.json"))
        with cf.ThreadPoolExecutor(2) as ex:
            for r in ex.map(recount, tasks):
                refs[str(r["n"])] |= r
                print(f"#{r['n']}: checks base {r['checks_base']} head {r['checks_head']}", flush=True)
        json.dump(refs, open(HERE / "refs.json", "w"), indent=1)
        return
    out = {}
    with cf.ThreadPoolExecutor(5) as ex:
        for r in ex.map(ref, tasks):
            out[str(r["n"])] = r
            print(f"#{r['n']}: checks base {r['checks_base']} head {r['checks_head']}, "
                  f"p2p {len(r['p2p'])}/{r['p2p_candidates']}", flush=True)
    json.dump(out, open(HERE / "refs.json", "w"), indent=1)


if __name__ == "__main__":
    main()
