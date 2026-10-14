#!/usr/bin/env python3
"""Run mini-swe-agent (v2.4.6, swebench.yaml prompts) on the club-3090 tasks against one OpenAI-compatible endpoint,
then score each patch offline: base tree + agent patch + the PR's hidden tests -> every PR test must pass.

usage: run_agent.py --config TAG --base-url URL --model SERVED_ID [--draw N] [--jobs N] [--only PR,...]
Writes runs/<TAG>/draw<N>/<pr>/{traj.json,patch.diff,eval.log,result.json} and runs/<TAG>/draw<N>/summary.json.
"""
import argparse, concurrent.futures as cf, json, os, subprocess, tempfile, time, traceback
from pathlib import Path

import yaml
from minisweagent.agents.default import DefaultAgent
from minisweagent.environments.docker import DockerEnvironment
from minisweagent.models import get_model

HERE = Path(__file__).resolve().parent
IMAGE = "club-tasks-env:1"
UID = f"{os.getuid()}:{os.getgid()}"
CFG = Path(__import__("minisweagent").__file__).parent / "config/benchmarks/swebench.yaml"
TASK_WALL_S = 3600


from scoring import changed_files, count_checks, export, put_tests, run_tests

REFS = json.load(open(HERE / "refs.json")) if (HERE / "refs.json").exists() else {}


def make_tree(commit: str, dst: Path):
    """Base tree as its own git repo (one commit), so the agent's changes are a plain `git diff`."""
    export(commit, dst, as_repo=True)


def score(task: dict, patch: str, out: Path) -> dict:
    """Pass/fail + partial credit (hidden-test checks, scaled base->merge) + localization + regressions."""
    ref = REFS.get(str(task["n"]), {})
    with tempfile.TemporaryDirectory(dir=HERE / "tmp") as td:
        tree = Path(td) / "t"
        make_tree(task["base"], tree)
        applied = True
        if patch.strip():
            p = subprocess.run(["git", "-C", str(tree), "apply", "--whitespace=nowarn", "-"], input=patch.encode(),
                               capture_output=True)
            applied = p.returncode == 0
            (out / "apply.log").write_bytes(p.stdout + p.stderr)
        p2p = ref.get("p2p", [])
        reg = run_tests(tree, p2p, timeout=120) if applied else {}  # before the hidden tests land
        put_tests(tree, task["merge"], task["tests"])  # hidden tests overwrite any agent edits to them
        hid = run_tests(tree, task["tests"])
    (out / "eval.log").write_text("\n".join(f"@@ {t} rc={r['rc']}\n{r['out']}" for t, r in (hid | reg).items()))
    passed = applied and bool(patch.strip()) and all(hid[t]["rc"] == 0 for t in task["tests"])
    # partial credit: checks passed, scaled so the base tree = 0 and the merged PR = 1
    cp = sum(count_checks(hid[t]["out"])[0] for t in task["tests"]) if applied else None
    b, h = ref.get("checks_base", {}).get("passed"), ref.get("checks_head", {}).get("passed")
    if passed:
        partial = 1.0
    elif cp is not None and b is not None and h is not None and h > b:
        partial = round(min(1.0, max(0.0, (cp - b) / (h - b))), 3)
    else:
        partial = 0.0
    src = set(ref.get("src_files") or [f for f in task["files"] if not f.startswith("scripts/tests/")])
    touched = {f for f in changed_files(patch) if not f.startswith("scripts/tests/")}
    loc = round(len(touched & src) / len(src), 3) if src else None
    regressions = [t for t, r in reg.items() if r["rc"] != 0]
    return dict(applied=applied, empty_patch=not patch.strip(), passed=passed, partial=partial,
                checks_passed=cp, localization=loc, files_touched=sorted(touched),
                p2p_run=len(reg), regressions=regressions,
                test_rc={t: r["rc"] for t, r in hid.items()})


def run_one(task: dict, a, cfg: dict, root: Path) -> dict:
    out = root / str(task["n"])
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    res = dict(n=task["n"], config=a.config, draw=a.draw)
    with tempfile.TemporaryDirectory(dir=HERE / "tmp") as td:
        tree = Path(td) / "testbed"
        make_tree(task["base"], tree)
        env = DockerEnvironment(**(cfg["environment"] | dict(
            image=IMAGE, cwd="/testbed", timeout=120, container_timeout="3h",
            env={k: v for k, v in cfg["environment"].get("env", {}).items() if k != "BASH_ENV"} | {"HOME": "/tmp"},
            run_args=["--rm", "--network", "none", "--user", UID, "-e", "HOME=/tmp", "-v", f"{tree}:/testbed"])))
        model = get_model(config=dict(
            model_class="litellm", model_name=f"openai/{a.model}", cost_tracking="ignore_errors",
            model_kwargs=dict(api_base=a.base_url, api_key="none", drop_params=True, timeout=1800,
                              extra_body={"reasoning_effort": "low"} | json.loads(a.extra_body), max_tokens=8192 + 32768)))
        agent_cfg = cfg["agent"] | dict(step_limit=a.step_limit, cost_limit=0, wall_time_limit_seconds=TASK_WALL_S)
        agent = DefaultAgent(model, env, **agent_cfg)
        try:
            info = agent.run(task["problem"])
            res |= dict(exit_status=info.get("exit_status"), submission=info.get("submission") or "")
        except Exception as e:  # noqa: BLE001 — record and score whatever is there
            res |= dict(exit_status=type(e).__name__, submission="", error=traceback.format_exc()[-2000:])
        finally:
            try:
                agent.save(out / "traj.json")
            except Exception:  # noqa: BLE001
                pass
            # Score the working tree, not the submit ritual: every tracked + new file the agent changed
            # (patch.txt excluded). The submitted text is kept for reference.
            subprocess.run(["git", "-C", str(tree), "add", "-A", "--", ".", ":!patch.txt"], capture_output=True)
            res["patch"] = subprocess.run(["git", "-C", str(tree), "diff", "--cached"], capture_output=True,
                                          text=True).stdout
            env.cleanup() if hasattr(env, "cleanup") else None
    res["agent_s"] = round(time.time() - t0, 1)
    res["steps"] = getattr(agent, "n_calls", None) or len([m for m in getattr(agent, "messages", []) if m.get("role") == "assistant"])
    (out / "patch.diff").write_text(res["patch"])
    (out / "submission.txt").write_text(res.pop("submission", "") or "")
    res |= score(task, res["patch"], out)
    res.pop("patch")
    (out / "result.json").write_text(json.dumps(res, indent=1))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--draw", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--step-limit", type=int, default=100)
    ap.add_argument("--only")
    ap.add_argument("--extra-body", default='{"reasoning_effort": "low"}',
                    help="JSON merged over {reasoning_effort: low} on every request (ThinkingCap adds chat_template_kwargs)")
    ap.add_argument("--rescore", action="store_true", help="re-score saved patches in runs/<config>/draw<N>, no model")
    a = ap.parse_args()
    (HERE / "tmp").mkdir(exist_ok=True)
    cfg = yaml.safe_load(CFG.read_text())
    tasks = json.load(open(HERE / "tasks.json"))
    if a.only:
        keep = {int(x) for x in a.only.split(",")}
        tasks = [t for t in tasks if t["n"] in keep]
    root = HERE / "runs" / a.config / f"draw{a.draw}"
    root.mkdir(parents=True, exist_ok=True)
    if a.rescore:
        for t in tasks:
            d = root / str(t["n"])
            if not (d / "result.json").exists():
                continue
            r = json.load(open(d / "result.json"))
            r |= score(t, (d / "patch.diff").read_text(), d)
            (d / "result.json").write_text(json.dumps(r, indent=1))
            print(f"#{t['n']}: passed={r['passed']} partial={r['partial']} loc={r['localization']} reg={r['regressions']}")
        return
    t0, results = time.time(), []
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        futs = {ex.submit(run_one, t, a, cfg, root): t["n"] for t in tasks}
        for f in cf.as_completed(futs):
            try:
                r = f.result()
            except Exception as e:  # noqa: BLE001
                r = dict(n=futs[f], passed=False, exit_status=f"runner:{type(e).__name__}")
            results.append(r)
            print(f"[{time.time() - t0:6.0f}s] #{r['n']}: {'PASS' if r.get('passed') else 'fail'} "
                  f"partial={r.get('partial')} loc={r.get('localization')} reg={len(r.get('regressions') or [])} "
                  f"({r.get('exit_status')}, {r.get('agent_s')} s, {r.get('steps')} steps)", flush=True)
    s = dict(config=a.config, draw=a.draw, model=a.model, n=len(results), passed=sum(r.get("passed", False) for r in results),
             wall_s=round(time.time() - t0), results=sorted(results, key=lambda r: r["n"]))
    (root / "summary.json").write_text(json.dumps(s, indent=1))
    print(f"{a.config} draw {a.draw}: {s['passed']}/{s['n']} in {s['wall_s']} s")


if __name__ == "__main__":
    main()
