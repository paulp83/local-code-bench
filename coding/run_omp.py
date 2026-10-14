#!/usr/bin/env python3
"""Run the club-tasks with omp (the user's daily harness) instead of mini-swe-agent, then score exactly as run_agent.py.

omp runs INSIDE the offline task container (--network none, host binary mounted read-only, fresh HOME per task). The
only route out is fwd.py: container 127.0.0.1:18000 -> mounted unix socket -> host -> the model server. No web, no
GitHub, so the agent can't look up the merged fix.

usage: run_omp.py --config TAG --base-url http://HOST:PORT/v1 --model SERVED_ID [--context N] [--thinking low]
                  [--draw N] [--jobs N] [--only PR,...] [--rescore]
Writes runs/<TAG>/draw<N>/<task>/{omp.log,omp.jsonl,patch.diff,eval.log,result.json}, same result schema as
run_agent.py (+ harness="omp"), so report.py compares the two harnesses directly.
"""
import argparse, concurrent.futures as cf, json, os, shutil, subprocess, tempfile, time, urllib.parse
from pathlib import Path

from run_agent import HERE, IMAGE, UID, make_tree, score

OMP = Path(os.environ.get("OMP_BIN") or shutil.which("omp") or Path.home() / ".local/bin/omp")
FWD = HERE / "fwd.py"
WALL_S = 3600
# Everything omp offers except what can't work offline, needs a human, or carries memory across tasks.
TOOLS = "read,bash,edit,write,glob,grep,ast_edit,todo,task,wait,eval"  # print-mode set; find/ast_grep/checkpoint/rewind/context_notes are unavailable there
FOOTER_NOTE = ("\n\nWhen you are done, stop. Your edits to the files in /testbed are your answer; "
               "you don't need to write or submit a patch.")


def omp_home(home: Path, model: str, context: int, thinking: str, efforts: str = "low,medium,high"):
    agent = home / ".omp" / "agent"
    agent.mkdir(parents=True)
    (agent / "models.yml").write_text(f"""providers:
  eval:
    api: openai-completions
    baseUrl: http://127.0.0.1:18000/v1
    auth: none
    compat:
      supportsDeveloperRole: false
      # openai = top-level reasoning_effort, the same request shape as the bare runner. qwen-chat-template (used
      # until 2026-10-12) sent only enable_thinking and dropped the effort, so each server fell back to its own
      # default: ThinkingCap low (server default), Strata xhigh (template default), GLM max (--reasoning-effort max).
      thinkingFormat: openai
      extraBody:
        chat_template_kwargs:
          enable_thinking: true
    models:
      - id: {model}
        name: {model}
        contextWindow: {context}
        maxTokens: {8192 + 32768}
        reasoning: true
        thinking:
          mode: effort
          efforts: [{efforts}]
          defaultLevel: {thinking}
        compat:
          supportsReasoningEffort: true
""")
    (agent / "config.yml").write_text(f"""modelRoles:
  default: eval/{model}
startup:
  setupWizard: false
tools:
  approvalMode: yolo
plan:
  defaultOnStartup: false
defaultThinkingLevel: {thinking}
""")


def run_one(task: dict, a, root: Path) -> dict:
    out = root / str(task["n"])
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    res = dict(n=task["n"], config=a.config, draw=a.draw, harness="omp")
    u = urllib.parse.urlparse(a.base_url)
    t0 = time.time()
    with tempfile.TemporaryDirectory(dir=HERE / "tmp") as td:
        td = Path(td)
        tree, home, sock = td / "testbed", td / "home", td / "sock"
        make_tree(task["base"], tree)
        omp_home(home, a.model, a.context, a.thinking, a.efforts)
        sock.mkdir()
        shutil.copy(FWD, sock / "fwd.py")
        (sock / "problem.md").write_text(task["problem"] + FOOTER_NOTE)
        host_fwd = subprocess.Popen(["python3", str(FWD), "unix2tcp", str(sock / "model.sock"), u.hostname, str(u.port)])
        try:
            for _ in range(50):
                if (sock / "model.sock").exists():
                    break
                time.sleep(0.1)
            inner = (
                "python3 /io/fwd.py tcp2unix 18000 /io/model.sock & sleep 0.5; cd /testbed && "
                f"omp -p --no-session --mode json --cwd /testbed --model eval/{a.model} --thinking {a.thinking} "
                f"--max-time {WALL_S} --auto-approve --no-lsp --no-extensions --no-title --tools={TOOLS} "
                "@/io/problem.md 'Solve the task described in the attached file.' > /io/omp.jsonl 2> /io/omp.err; "
                "echo $? > /io/omp.rc")
            name = f"omp-task-{a.config}-{task['n']}-{os.getpid()}"
            p = subprocess.run(["docker", "run", "--rm", "--name", name, "--network", "none", "--user", UID,
                                "-e", "HOME=/tmp/home", "-v", f"{tree}:/testbed", "-v", f"{home}:/tmp/home",
                                "-v", f"{sock}:/io", "-v", f"{OMP}:/usr/local/bin/omp:ro", IMAGE, "bash", "-c", inner],
                               capture_output=True, text=True, timeout=WALL_S + 300)
        except subprocess.TimeoutExpired:
            subprocess.run(["docker", "kill", name], capture_output=True)
            res["exit_status"] = "TimeExceeded(host)"
        finally:
            host_fwd.terminate()
        for f in ("omp.jsonl", "omp.err", "omp.rc"):
            if (sock / f).exists():
                shutil.copy(sock / f, out / f)
        rc = (sock / "omp.rc").read_text().strip() if (sock / "omp.rc").exists() else "?"
        res.setdefault("exit_status", "Submitted" if rc == "0" else f"omp-rc-{rc}")
        # working tree = answer; omp's own state dirs don't count
        subprocess.run(["git", "-C", str(tree), "add", "-A", "--", ".", ":!.omp", ":!patch.txt"], capture_output=True)
        res["patch"] = subprocess.run(["git", "-C", str(tree), "diff", "--cached"], capture_output=True, text=True).stdout
    res["agent_s"] = round(time.time() - t0, 1)
    res["steps"] = count_tool_calls(out / "omp.jsonl")
    (out / "patch.diff").write_text(res["patch"])
    res |= score(task, res["patch"], out)
    res.pop("patch")
    (out / "result.json").write_text(json.dumps(res, indent=1))
    return res


def count_tool_calls(path: Path):
    """Tool calls in omp's JSON event stream (event names vary by version; count anything that looks like a call)."""
    if not path.exists():
        return None
    n = 0
    for line in path.read_text(errors="ignore").splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = str(ev.get("type", ""))
        if t in ("tool_execution_start", "tool_call", "toolCall", "tool_use"):
            n += 1
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--context", type=int, default=204800)
    ap.add_argument("--thinking", default="low")
    ap.add_argument("--efforts", default="low,medium,high", help="the model's effort ladder (GLM: low,high,max; Qwen3.8: low,medium,xhigh)")
    ap.add_argument("--draw", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--only")
    a = ap.parse_args()
    (HERE / "tmp").mkdir(exist_ok=True)
    tasks = json.load(open(HERE / "tasks.json"))
    if a.only:
        keep = {int(x) for x in a.only.split(",")}
        tasks = [t for t in tasks if t["n"] in keep]
    root = HERE / "runs" / a.config / f"draw{a.draw}"
    root.mkdir(parents=True, exist_ok=True)
    t0, results = time.time(), []
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        futs = {ex.submit(run_one, t, a, root): t["n"] for t in tasks}
        for f in cf.as_completed(futs):
            try:
                r = f.result()
            except Exception as e:  # noqa: BLE001
                r = dict(n=futs[f], passed=False, exit_status=f"runner:{type(e).__name__}: {e}"[:200])
            results.append(r)
            print(f"[{time.time() - t0:6.0f}s] #{r['n']}: {'PASS' if r.get('passed') else 'fail'} "
                  f"partial={r.get('partial')} loc={r.get('localization')} reg={len(r.get('regressions') or [])} "
                  f"({r.get('exit_status')}, {r.get('agent_s')} s, {r.get('steps')} steps)", flush=True)
    s = dict(config=a.config, draw=a.draw, model=a.model, harness="omp", n=len(results),
             passed=sum(r.get("passed", False) for r in results), wall_s=round(time.time() - t0),
             results=sorted(results, key=lambda r: r["n"]))
    (root / "summary.json").write_text(json.dumps(s, indent=1))
    print(f"{a.config} draw {a.draw}: {s['passed']}/{s['n']} in {s['wall_s']} s")


if __name__ == "__main__":
    main()
