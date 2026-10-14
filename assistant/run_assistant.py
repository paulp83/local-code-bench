#!/usr/bin/env python3
"""Run the club-tasks assistant set (26 non-coding tasks) through Hermes or omp in an offline container, then score
with each task's check.py on the HOST, where the agent never saw it.

Only task.md and workspace/ enter the sandbox. The container runs --network none as the host user; the only route out
is fwd.py (container 127.0.0.1:18000 -> mounted unix socket -> host -> model server).

usage: run_assistant.py --harness hermes|omp --config TAG --base-url http://HOST:PORT/v1 --model SERVED_ID
                        [--draw N] [--jobs N] [--only 23,24-needle-in-notes] [--effort low] [--wall-s 1200]
                        [--efforts low,medium,high] [--no-thinking-kwarg] [--rescore]
Writes assistant/runs/<TAG>/<harness>/draw<N>/<task>/{result.json,agent.log,check.out} + summary.json.
"""
import argparse, concurrent.futures as cf, json, os, re, shutil, subprocess, sys, tempfile, time, urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
CT = HERE.parent / "coding"
sys.path.insert(0, str(CT))
from run_omp import FWD, OMP, TOOLS, count_tool_calls, omp_home  # noqa: E402

UID = f"{os.getuid()}:{os.getgid()}"
OMP_IMAGE = "club-tasks-env:1"
HERMES_IMAGE = os.environ.get("HERMES_IMAGE", "benchlocal-sandbox-hermes:latest")
# agent-runner.py from noonghunna/benchlocal-cli (sandboxes/hermes/verification/), MIT
AGENT_RUNNER = Path(os.environ.get("HERMES_AGENT_RUNNER", "benchlocal-cli/sandboxes/hermes/verification/agent-runner.py"))
TOOLSETS = ["file", "terminal", "code_execution"]  # no web/browser/memory: offline, and nothing may carry over
FOOTER = "\n\nWork in /workspace. When you are done, stop; the files you leave are your answer.\n"


def hermes_files(home: Path, sock: Path, a, prompt: str):
    """config.yaml in HERMES_HOME + request.json for benchlocal's agent-runner.py (same shape as hermes-runtime.mjs)."""
    home.mkdir(parents=True)
    (home / "config.yaml").write_text(f"""model:
  default: "{a.model}"
  provider: "custom"
  base_url: "http://127.0.0.1:18000/v1"
  context_length: {a.context}
terminal:
  backend: "local"
  cwd: "/workspace"
  timeout: 120
  lifetime_seconds: 600
display:
  tool_progress: "off"
  streaming: false
  inline_diffs: false
  show_reasoning: false
compression:
  enabled: false
approvals:
  mode: "off"
agent:
  max_turns: {a.max_turns}
""")
    extra = {"reasoning_effort": a.effort}
    if not a.no_thinking_kwarg:
        extra["chat_template_kwargs"] = {"enable_thinking": True}
    (sock / "request.json").write_text(json.dumps(dict(
        workspaceDir="/workspace", hermesHomeDir="/tmp/home/.hermes", prompt=prompt, toolsets=TOOLSETS,
        maxTurns=a.max_turns, resultPath="/io/result.json", sessionId=None,
        model=dict(id=a.model, exposedModel=a.model, providerModel=a.model, inferenceBaseUrl="http://127.0.0.1:18000/v1",
                   apiKey="dummy", provider="custom", authMode="bearer", extraBody=extra),
        generation=dict(max_tokens=a.max_tokens),
        followUps=dict(defaultApprovalResponse="once"))))


def inner_cmd(a) -> tuple[str, str]:
    """(image, shell command run in the container). Outputs go to /io."""
    fwd = "python3 /io/fwd.py tcp2unix 18000 /io/model.sock & sleep 0.5; cd /workspace && "
    if a.harness == "omp":
        return OMP_IMAGE, fwd + (
            f"omp -p --no-session --mode json --cwd /workspace --model eval/{a.model} --thinking {a.effort} "
            f"--max-time {a.wall_s} --auto-approve --no-lsp --no-extensions --no-title --tools={TOOLS} "
            "@/io/prompt.md 'Do the task described in the attached file.' > /io/agent.jsonl 2> /io/agent.err; "
            "echo $? > /io/agent.rc")
    return HERMES_IMAGE, fwd + (
        f"timeout {a.wall_s} /opt/hermes-venv/bin/python -I /io/agent-runner.py /io/request.json "
        "> /io/agent.out 2> /io/agent.err; echo $? > /io/agent.rc")


def hermes_stats(sock: Path):
    p = sock / "result.json"
    if not p.exists():
        return None, None, "no result.json"
    r = json.loads(p.read_text())
    calls = sum(1 for e in r.get("toolEvents", []) if e.get("phase") == "start")
    note = None if r.get("ok") else (r.get("error") or "hermes not ok")[:160]
    return calls, r.get("finalResponse"), note


def run_check(task_dir: Path, ws: Path, out: Path) -> dict:
    p = subprocess.run(["python3", "-I", str(task_dir / "check.py"), str(ws)], capture_output=True, text=True, timeout=120)
    (out / "check.out").write_text(p.stdout + p.stderr)
    m = re.search(r"PASS:\s*(\d+)\s+FAIL:\s*(\d+)", p.stdout)
    cp, cf_ = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    tot = cp + cf_
    return dict(passed=p.returncode == 0 and tot > 0, checks_passed=cp, checks_total=tot or None,
                partial=round(cp / tot, 3) if tot else 0.0)


def run_one(task_dir: Path, a, root: Path) -> dict:
    name = task_dir.name
    out = root / name
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    res = dict(task=name, config=a.config, harness=a.harness, draw=a.draw, model=a.model)
    u = urllib.parse.urlparse(a.base_url)
    t0 = time.time()
    with tempfile.TemporaryDirectory(dir=CT / "tmp") as td:
        td = Path(td)
        ws, home, sock = td / "workspace", td / "home", td / "io"
        shutil.copytree(task_dir / "workspace", ws, symlinks=True) if (task_dir / "workspace").exists() else ws.mkdir()
        sock.mkdir()
        home.mkdir()
        os.chmod(ws, 0o777)
        prompt = (task_dir / "task.md").read_text() + FOOTER
        (sock / "prompt.md").write_text(prompt)
        shutil.copy(FWD, sock / "fwd.py")
        if a.harness == "omp":
            omp_home(home, a.model, a.context, a.effort, a.efforts)
        else:
            shutil.copy(AGENT_RUNNER, sock / "agent-runner.py")
            hermes_files(home / ".hermes", sock, a, prompt)
        image, inner = inner_cmd(a)
        cname = f"assist-{a.harness}-{a.config}-{name}-{os.getpid()}"[:100]
        host_fwd = subprocess.Popen(["python3", str(FWD), "unix2tcp", str(sock / "model.sock"), u.hostname, str(u.port)])
        try:
            for _ in range(50):
                if (sock / "model.sock").exists():
                    break
                time.sleep(0.1)
            cmd = ["docker", "run", "--rm", "--name", cname, "--network", "none", "--user", UID, "-e", "HOME=/tmp/home",
                   "-v", f"{ws}:/workspace", "-v", f"{home}:/tmp/home", "-v", f"{sock}:/io"]
            if a.harness == "omp":
                cmd += ["-v", f"{OMP}:/usr/local/bin/omp:ro"]
            else:
                cmd += ["--entrypoint", ""]  # the sandbox image's entrypoint starts its own server
            dp = subprocess.run(cmd + [image, "bash", "-c", inner], capture_output=True, text=True, timeout=a.wall_s + 300)
            (out / "docker.err").write_text(dp.stdout + dp.stderr)
        except subprocess.TimeoutExpired:
            subprocess.run(["docker", "kill", cname], capture_output=True)
            res["exit_status"] = "TimeExceeded(host)"
        finally:
            host_fwd.terminate()
        res["agent_s"] = round(time.time() - t0, 1)
        for f in ("agent.jsonl", "agent.err", "agent.out", "agent.rc", "result.json"):
            if (sock / f).exists():
                shutil.copy(sock / f, out / {"agent.out": "agent.log", "result.json": "agent.result.json"}.get(f, f))
        rc = (sock / "agent.rc").read_text().strip() if (sock / "agent.rc").exists() else "?"
        if a.harness == "omp":
            res["tool_calls"] = count_tool_calls(out / "agent.jsonl")
            note = None
        else:
            res["tool_calls"], final, note = hermes_stats(sock)
            if final:
                (out / "final.txt").write_text(str(final))
        res.setdefault("exit_status", note and f"hermes:{note}" or ("done" if rc == "0" else f"rc-{rc}"))
        # score the workspace the agent left, host side
        res |= run_check(task_dir, ws, out)
        shutil.copytree(ws, out / "workspace_after", symlinks=True)
    (out / "result.json").write_text(json.dumps(res, indent=1))
    return res


def pick_tasks(only: str | None) -> list[Path]:
    dirs = sorted(d for d in HERE.iterdir() if d.is_dir() and (d / "check.py").exists())
    if not only:
        return dirs
    keys = only.split(",")
    return [d for d in dirs if any(d.name == k or d.name.split("-")[0] == k.zfill(2) for k in keys)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harness", required=True, choices=["hermes", "omp"])
    ap.add_argument("--config", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--draw", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--only")
    ap.add_argument("--effort", default="low", help="reasoning effort (GLM top rung: max; Qwen3.8 top: xhigh)")
    ap.add_argument("--efforts", default="low,medium,high", help="omp: the model's effort ladder")
    ap.add_argument("--no-thinking-kwarg", action="store_true", help="hermes: skip chat_template_kwargs.enable_thinking")
    ap.add_argument("--wall-s", type=int, default=1200)
    ap.add_argument("--context", type=int, default=204800)
    ap.add_argument("--max-turns", type=int, default=90, help="hermes iteration cap")
    ap.add_argument("--max-tokens", type=int, default=16384, help="hermes per-call max_tokens")
    a = ap.parse_args()
    (CT / "tmp").mkdir(exist_ok=True)
    tasks = pick_tasks(a.only)
    root = HERE / "runs" / a.config / a.harness / f"draw{a.draw}"
    root.mkdir(parents=True, exist_ok=True)
    t0, results = time.time(), []
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        futs = {ex.submit(run_one, t, a, root): t.name for t in tasks}
        for f in cf.as_completed(futs):
            try:
                r = f.result()
            except Exception as e:  # noqa: BLE001
                r = dict(task=futs[f], passed=False, partial=0.0, exit_status=f"runner:{type(e).__name__}: {e}"[:200])
            results.append(r)
            print(f"[{time.time() - t0:6.0f}s] {r['task']}: {'PASS' if r.get('passed') else 'fail'} "
                  f"{r.get('checks_passed')}/{r.get('checks_total')} ({r.get('exit_status')}, {r.get('agent_s')} s, "
                  f"{r.get('tool_calls')} calls)", flush=True)
    s = dict(config=a.config, harness=a.harness, draw=a.draw, model=a.model, n=len(results),
             passed=sum(bool(r.get("passed")) for r in results), wall_s=round(time.time() - t0),
             results=sorted(results, key=lambda r: r["task"]))
    (root / "summary.json").write_text(json.dumps(s, indent=1))
    print(f"{a.config}/{a.harness} draw {a.draw}: {s['passed']}/{s['n']} in {s['wall_s']} s")


if __name__ == "__main__":
    main()
