# Coding bench: agent tasks from real club-3090 PRs

A small benchmark that asks one question: **given a real bug report or feature request from the club-3090 repo, can a
locally served model, driven by a standard coding agent, change the code so the project's own tests pass?**

It exists because the usual public coding benchmarks were all published before the models we wanted to compare
(GLM-5.3-Flash and Qwen3.8-Flash-Next both launched on 2026-08-26). Neither lab publishes a training cutoff, so the
release date is the only safe line. **Every task here comes from a PR merged after that date**, so neither model can
have seen the fix.

## At a glance

| | |
|---|---|
| Tasks | 20 (from 321 merged PRs, 2026-08-27 to 2026-10-10) |
| Source | `noonghunna/club-3090`: shell + Python tooling (launcher, setup, registry, preflight, quality/bench scripts) |
| Task text | the linked issue, or the PR's problem section with every solution section removed; 8 tasks also carry an `## Interface` section |
| Agent | [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) 2.4.6, its stock SWE-bench prompts, bash only |
| Sandbox | Docker, `--network none`, clean checkout of the commit before the PR |
| Pass check | the PR's own new or changed tests, hidden from the agent, all pass on the agent's tree |
| Extra measures | partial credit, localization, regressions, steps, time, tasks per hour |

## Why not an existing benchmark?

| Benchmark | Newest tasks (checked 2026-10-10) | Problem |
|---|---|---|
| LiveCodeBench v6 (as packaged in benchlocal) | problems dated from 2025-01-01 | before both models; Flash Next scored 86/90 (96%), so it also can't separate them |
| Aider polyglot | Exercism exercises, benchmark from Dec 2024 | public for years (Flash Next: 25/30) |
| SWE-rebench leaderboard (Hugging Face) | monthly split 2026_03 | before the models |
| SWE-rebench-V2 | tasks created up to 2025-10-31 | before the models |
| SWE-rebench on Harbor Hub | July 2026 evaluation split | before the models |
| Terminal-Bench 2.0 | late 2025 | before the models |

SWE-rebench will publish post-August batches later. Until then, mining our own repo is the only source of tasks that
are clean by construction. It also tests the work we actually do: shell and Python tooling, not algorithm puzzles.

## How the tasks were built

1. **Candidates.** Merged PRs since 2026-08-27 that touch `scripts/tests/` and are small enough for one agent session
   (≤ 6 files, ≤ 400 changed lines): **115** of 321.
2. **Validation, offline in Docker.** Take the commit before the PR, add the PR's versions of its test files, and run
   them: they must **fail**. Run the same tests on the merged commit: they must **pass**. **67** passed both checks.
   The rest either already passed before the PR (23) or need a GPU, Docker, or the network to pass (25).
3. **Task text.** The linked issue if the PR closes one; otherwise the PR title plus only its problem sections
   (`## Why`, `## What broke`, `## Problem`, ...). Solution sections (`## What`, `## Fix`, `## How`) are cut. PRs
   with no usable problem section were dropped (**38** left).
4. **Human screening** (the SWE-bench Verified step). I read each task's hidden-test failure messages against its
   text and dropped tasks whose tests demand something the text never names: a function, a new file, an env var, an
   exact output string. Issue bodies that were mostly pasted rig reports went too. **14 dropped, 20 kept**, across 9
   areas of the repo. Issue text is otherwise verbatim, including any "suggested fix" the reporter wrote, as in
   SWE-bench.
5. **Interface sections** (added after draw 1; the SWE-bench Pro approach). Screening in step 4 only saw what the
   tests print *before* the fix. Agents' attempts exposed 8 more tasks whose tests need something the text never
   states (see "What we learned mid-eval"). Those 8 got an `## Interface` section written from the hidden tests
   (`interfaces.json`): what the tests call and expect, not how to implement it.

Each task carries: the base commit, the merge commit, the hidden test files, the reference source files, the problem
text, and a short footer telling the agent to work in `/testbed` and that its test edits aren't graded.

## How a run works

- The agent gets the problem text and a bash shell in a container with a clean checkout of the base commit
  (Python 3.12, git, jq, shellcheck, pyyaml, pytest; no network). The container runs as the host user, with
  `HOME=/tmp` and without the SWE-bench config's `BASH_ENV=/root/.bashrc`.
- Limits: 100 steps, 60 minutes per task. Model requests: thinking on, `reasoning_effort: low`, 8,192 answer +
  32,768 thinking tokens, the server's own sampler. Engines that switch thinking per request get it on top
  (ThinkingCap on SGLang: `chat_template_kwargs.enable_thinking: true`; its compose already defaults effort to low,
  and a request's own effort wins).
- When the agent stops, **its working tree is the answer**: every changed or new file, as a diff. The agent's own
  "submit" text is kept but not scored, so a model isn't penalised for fumbling the submit ritual.
- Scoring, offline: fresh base checkout + agent diff + the PR's hidden tests (they overwrite anything the agent did to
  test files), then run them, plus the regression tests below.

## What gets measured

| Measure | Meaning |
|---|---|
| **Solved** | the patch applies and every hidden test passes |
| **Partial credit** | hidden-test checks passed, scaled so the base commit = 0 and the merged PR = 1. 14 of 20 tasks print enough checks (per-check lines or a `PASS: N FAIL: M` summary) to give a gradient; the other 6 are effectively all-or-nothing |
| **Localization** | share of the PR's changed source files the agent also changed |
| **Regressions** | up to 5 existing repo tests that reference the changed files and pass before and after the PR; any the agent's patch breaks are flagged (every task has 1 to 5) |
| **Efficiency** | steps, agent time per task, tasks solved per hour of agent time |
| **Exit status** | submitted, step limit, time limit, context-window errors, harness errors |

## Reading the results

20 binary tasks are a small sample. Before calling one config better than another:

| Draws per config | Gap needed to call it real (≈95%) |
|---|---|
| 1 | about 6 tasks |
| 2 | about 4–5 tasks |

So the report leans on measures with more resolution: partial credit, localization, and a **paired comparison**
(tasks only config A solved vs only config B, with an exact McNemar test). Configs face identical tasks, so pairing
removes task difficulty from the comparison. Expect this bench to separate **models** that differ meaningfully; quants
of the same model will usually come out equivalent, and that's a useful answer too.

Also read tasks per hour next to the solve rate. In an agent loop a fast config that solves a bit less can finish
more work in a day.

Known limits:
- One repository, mostly shell and Python. Strong at "fix this tooling bug", silent on other languages and on
  greenfield work.
- The models may have seen the repo's older code; the fixes themselves are new.
- Some hidden tests check behaviour through stubs, and the screening was one person's judgement.
- The agent harness is deliberately minimal. A model that does well inside a richer harness (omp, Claude Code) may
  rank differently; that's a second pass, run on the two finalists.

## What we learned mid-eval

**Draw 1 on the original text (2026-10-10/11, 2×RTX 5090).** Interim, superseded by the re-run below:

| Config | Solved | Mean partial | Localization | Median min/task | Solved per agent-hour |
|---|---|---|---|---|---|
| Qwen3.8-Flash-Next, Strata, UD-IQ4_XS | 9/20 | 0.54 | 0.92 | 13.0 | 1.75 |
| GLM-5.3-Flash avar6 Q2_K-Q3_K, llama.cpp moe-cache | 8/20 | 0.47 | 0.88 | 12.9 | 1.63 |
| Qwen3.8-Flash-Next, Strata, UD-Q4_K_XL | 6/20 | 0.38 | 0.84 | 9.1 | 1.73 |
| ThinkingCap-Qwen3.8-27B, SGLang dual-fast + RAM KV tier | 6/20 | 0.38 | 0.82 | 4.8 | 3.66 |

No pair differed significantly (best McNemar p = 0.25). Three findings shaped the next step:

1. **The task set split three ways.** 6 tasks every config solved, 4 tasks separated configs, and 10 tasks no
   config solved. Ten all-fail tasks is a warning sign, not proof of a hard bench.
2. **8 of those 10 were unfair as written.** Reading the failures across all configs showed the hidden tests checked
   something the text never stated: an exact CLI (`catalog.sh rename/update`, #1209), a new function name
   (`gpu_vram_report_lines`, #1571), unmentioned edge cases (#1518, #1555, #1610, #1612), a plan line (#1564), or one
   exact sentence the agents had paraphrased correctly (#1621). Only #1174 and #1510 were genuine misses.
   Step-4 screening missed them because it only read failure messages printed before the fix.
3. **GLM ran far faster than expected:** about 13 minutes per task, level with Strata, not the 30–60 the quality
   packs suggested. Agent turns are short, so decode speed matters less than in long-answer packs.

**Pivot (2026-10-11):** rather than drop the 8 (leaving 12 tasks, too few to rank anything), each got an
`## Interface` section, and they re-run on every config. Draw 1 then covers 20 fair tasks. The original-text results
for those 8 stay in `runs/<config>/draw1-v1/` as a before/after record of what the missing details cost each config.
Second draws (all 20, new text) follow on the Strata and ThinkingCap configs.

**Draw 1 on the fair text (2026-10-11, after the Interface re-runs).** Strata Q4_K_XL's re-run was still pending,
so it's left out here:

| Config | Solved | Partial | Right files | Median min/task | Median steps | s/step | Output tok/task | Solved per agent-hour |
|---|---|---|---|---|---|---|---|---|
| Qwen3.8-Flash-Next, Strata, UD-IQ4_XS | **16/20** | **0.88** | 0.94 | 12.1 | 39 | 21 | 19.6K | 3.5 |
| GLM-5.3-Flash avar6 Q2_K-Q3_K | 13/20 | 0.72 | 0.96 | 12.6 | 38 | 19 | 11.3K | 2.5 |
| GLM-5.3-Flash UD-IQ4_XS | 12/20 | 0.70 | 0.93 | 12.0 | 28 | 28 | 8.7K | 2.3 |
| ThinkingCap-Qwen3.8-27B, SGLang dual-fast | 12/20 | 0.67 | 0.88 | **5.0** | 34 | **7** | 31.7K | **7.3** |

No regressions in 80 runs; one run hit the 100-step limit. What the details say that the solve rate can't:

1. **Only 6 tasks separate the configs.** 11 were solved by all four and 3 by none (#1174, #1510, #1555). The best
   pairwise gap, Strata IQ4_XS vs ThinkingCap and vs GLM IQ4_XS, is 4 tasks to 0 (McNemar p = 0.12): close, not
   significant. The Interface sections overshot: 5 of the 8 revised tasks went from solved by nobody to solved by
   everyone (#1209, #1564, #1571, #1610, #1621), so they stopped separating configs the other way.
2. **Flash Next wins by persistence.** The tasks only it solved are the long ones: #1588 (100 steps, 44 min), #1556
   (26 min), and #1573 with avar6 (25 min). Its failures are real attempts. ThinkingCap's failures end in 2.5 to 9
   minutes, which reads as giving up or submitting a confident wrong fix.
3. **ThinkingCap leads on throughput.** It answers 3 to 4 times faster per turn (7 s/step vs 19 to 28) while writing
   the most tokens (about 23K on the tasks everyone solved, vs 8K to 19K), so it solves 7.3 tasks per agent-hour,
   twice Flash Next's 3.5, with 4 fewer solves. A check-and-retry loop gets more done per hour with ThinkingCap; Flash
   Next gets more of the hard ones right first time.
4. **GLM is terse and precise.** The fewest tokens per step (290 to 315 vs 500 to 750) and the best file
   localization (0.93 to 0.96); avar6 alone solved #1204, the hardest task here (93 steps). Slower decode holds it to
   about 2.4 solved per hour. Its two quants sit one task apart, as in the quality packs.
5. **On equal work** (the 11 tasks all four solved), median time is 2.7 min for ThinkingCap, 8.2 to 8.6 for GLM and
   11.0 for Flash Next, at similar step counts (23 to 33). The time gap is per-turn model speed, not strategy.

Next revision of the bench, from this: add harder PRs from the 47 validated candidates not used, trim the generous
Interface sections back to names and CLI shapes (no exact output wording), and report time to the first correct
fix next to the solve rate, since that's where the configs differ most.

**Harness and scoring fixes found along the way** (all applied before the numbers above, or re-scored):
- omp's `qwen-chat-template` thinking format never sent `reasoning_effort`, so `--thinking low` was ignored and each server used its own default: ThinkingCap low, Strata IQ4_XS xhigh, GLM max. The first omp runs on Strata and GLM were therefore at the top rung, not low. Fixed 2026-10-12 (`thinkingFormat: openai` + `enable_thinking` in `extraBody`, checked with a stub server).
- The SWE-bench config sets `BASH_ENV=/root/.bashrc`. Run as a non-root user, every command printed a permission
  error, which broke the submit step. Dropped `BASH_ENV`, set `HOME=/tmp`.
- Scoring the agent's submitted text made the score depend on the submit ritual. Switched to scoring the working tree.
- Some tests print only failures plus a `PASS: N FAIL: M` total. The check counter skipped totals, so a 12-of-15 near
  miss scored 0.0. It now uses the total; the references were recounted and finished runs re-scored (`--rescore`).
- One config briefly ran two copies of itself at once (a restarted chain left a run behind). The second run
  overwrote every task, so results are single-run, but the first few tasks' times are slightly inflated.
- A process check using `pgrep -f <pattern>` matched the checking shell's own command line and reported a finished
  run as still going. Check result files, not process names.
- Strata listens on 127.0.0.1 by default, which the club quality harness's sandboxes can't reach; serve it on
  `--host 172.17.0.1` for any containerised harness.

## Running it

Requirements: Docker, Python 3.12+, `uv`, a local clone of `club-3090` (path in `CLUB3090_REPO`), `gh` (only to rebuild the task set), and an
OpenAI-compatible endpoint. For the omp arm, omp v18.6.0 on the host (`OMP_BIN`, default: `omp` on `PATH`).

```bash
git clone https://github.com/noonghunna/club-3090 && export CLUB3090_REPO=$PWD/club-3090
uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt   # at the repo root
cd coding
docker build -t club-tasks-env:1 env/

# (Re)build the task set from scratch, about 1-2 hours of offline test runs:
gh pr list -R noonghunna/club-3090 --state merged --search "merged:>=2026-08-27" --limit 1000 \
  --json number,mergedAt,files,additions,deletions,title,body,mergeCommit > prs-raw.json
python3 make_candidates.py             # -> candidates.json (touches scripts/tests/, <= 6 files, <= 400 lines)
python3 validate.py --jobs 6            # -> validated.json (FAIL at base + tests, PASS at merge)
python3 build_tasks.py --n 25           # -> tasks.json + tasks-review.md (applies interfaces.json; read it first)
../.venv/bin/python refs.py                # -> refs.json (check counts + regression tests per task)
#   refs.py --checks-only re-counts the reference checks without re-picking regression tests

# Run one config (one draw), then score and compare:
../.venv/bin/python run_agent.py --config my-model --base-url http://HOST:PORT/v1 --model SERVED_ID --draw 1 --jobs 1
../.venv/bin/python run_omp.py --config my-model-omp --base-url http://HOST:PORT/v1 --model SERVED_ID --thinking low --efforts low,medium,xhigh
../.venv/bin/python report.py my-model other-model > report.md
```

Useful flags: `--jobs N` runs N tasks at once (only if the server batches); `--extra-body '{...}'` merges extra
request fields over `{"reasoning_effort": "low"}` (for example SGLang's `chat_template_kwargs`); `--only 1464,1307`
runs a subset; `--rescore` re-scores saved patches without calling the model (do it after any scorer change; a run
that was already going keeps the scorer it started with).

When a task text changes, re-run that task on every config and keep the old results aside, as the pivot did.

## Files

| File | What it is |
|---|---|
| `env/Dockerfile` | the offline sandbox image |
| `make_candidates.py` | PR export → candidates (size and test filters) |
| `validate.py` | FAIL-at-base / PASS-at-merge check per candidate |
| `build_tasks.py` | problem text, exclusions (with reasons), interface sections, area spread → `tasks.json`, `tasks-review.md` |
| `interfaces.json` | the 8 `## Interface` sections, written from the hidden tests |
| `refs.py`, `scoring.py` | reference check counts, regression-test selection, offline test runner, check counter |
| `run_agent.py` | mini-swe-agent driver + scorer; writes `runs/<config>/draw<N>/<task>/` (trajectory, diff, submission, eval log, result) |
| `report.py` | per-config table with Wilson 95% CIs, pairwise McNemar, per-task grid |
| `run_omp.py`, `fwd.py` | the same tasks through omp (v18.6.0): host binary mounted read-only into the offline container, fresh HOME per task, one socket forwarder to the model endpoint and no other network |
| `tasks.json`, `refs.json` | the 20 tasks and their references (`tasks.v1.json`: the original text) |
| `runs/<config>/draw1-v1/` | original-text results for the 8 revised tasks |

## Configs in this round (2×RTX 5090, TR PRO 3975WX, 2026-10)

| Config tag | Model and serving |
|---|---|
| `strata-iq4xs` | Qwen3.8-Flash-Next UD-IQ4_XS on Strata v0.1.39, layer split, 262K |
| `strata-q4kxl` | Qwen3.8-Flash-Next UD-Q4_K_XL on Strata, same settings |
| `thinkingcap-dualfast` | ThinkingCap-Qwen3.8-27B, `sgl/thinkingcap38-27b-dual-fast`, RAM KV tier 64 GB, 2 concurrent |
| `glm-avar6` | GLM-5.3-Flash avar6 Q2_K-Q3_K, llama.cpp moe-cache slug (the club's fast GLM slug) |
| `glm-iq4xs` | GLM-5.3-Flash UD-IQ4_XS, llama.cpp moe-cache, ub 1024 / admit 32 |

Results from this round: [`../results/2026-10-2x5090/`](../results/2026-10-2x5090/) (findings, CSVs, reports, every run's `result.json` and patch).

ThinkingCap runs boot from a club-3090 checkout dated 2026-10-04, before #1603 added server-side reasoning budgets per effort (low = 4,096 on the Qwen3.8 / ThinkingCap vLLM and SGLang composes). Its thinking was capped only by the client's 32,768 tokens, the same as the other configs. A re-run on a current compose would cap it at 4,096. The omp arm runs the same 20 tasks through omp (`run_omp.py`); omp gets its print-mode tools minus web search, GitHub, ask and the memory tools.

