# local-code-bench

Two agent benches for locally served models, a pair of long-context state probes, and the first round of results.

- **Coding** ([`coding/`](coding/)): 20 bug fixes mined from [club-3090](https://github.com/noonghunna/club-3090)'s own pull requests, all merged after the models under test were released, so no model has seen the fix. An agent gets the issue text and a clean checkout in an offline container; the PR's own tests, hidden from the agent, grade the result.
- **Assistant** ([`assistant/`](assistant/)): 38 non-coding desk tasks with deterministic checks. 26 base tasks (inbox triage, scheduling, expenses, file moves, style-guided replies) and 12 harder ones (hard-v1) built around long inputs, long jobs with state, conflicting sources, error recovery, instructions planted in the data, and changed requirements. All data is synthetic.

- **Long-context probes** ([`longctx/`](longctx/)): two deterministic, teacher-forced tests that compare two servers differing in one setting (a state dtype, a KV dtype, a quant): log-probs on 8K to 250K-token prefixes, and recall of facts planted early and corrected later. No agent, no sampling noise, about an hour per server. SGLang only.

The two agent benches run the agent in Docker with `--network none`. The only route out is a unix-socket forwarder to your model endpoint. Harnesses: [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) 2.4.6 (bash only), omp 18.6.0, and Hermes (through the [benchlocal-cli](https://github.com/noonghunna/benchlocal-cli) sandbox). Any OpenAI-compatible endpoint works.

## First results (2026-10, 2× RTX 5090)

Coding tasks solved, bare mini-swe-agent at effort low:

| Model | Served as | Solved | Solved per agent-hour |
|---|---|---|---|
| Qwen3.8-Flash-Next UD-IQ4_XS | Strata | 31/40 (78%) | 4.3 |
| GLM-5.3-Flash avar6 Q2_K-Q3_K | llama.cpp moe-cache | 13/20 (65%) | 2.5 |
| Qwen3.8-Flash-Next UD-Q4_K_XL | Strata | 25/40 (62%) | 3.5 |
| GLM-5.3-Flash UD-IQ4_XS | llama.cpp moe-cache | 12/20 (60%) | 2.3 |
| ThinkingCap-Qwen3.8-27B | SGLang dual-fast | 23/40 (57%) | **7.0** |

The top effort rung (xhigh or max) added two solves at most on any model and cost 1.6 to 4 times the time. omp beat the bare agent for ThinkingCap-27B and lost to it for the two MoE models. On the assistant tasks both Qwen models scored 25 or 26 of 26, and only the long-input hard-v1 task separated them.

Write-up: [`results/2026-10-2x5090/FINDINGS.md`](results/2026-10-2x5090/FINDINGS.md). Every run's `result.json` and patch, plus CSVs of all 400 coding and 152 assistant runs, sit in the same folder.

## Layout

| Path | What it is |
|---|---|
| `coding/` | task build pipeline (PR export → candidates → validation → tasks), the agent drivers (`run_agent.py`, `run_omp.py`), scoring, `report.py` |
| `coding/tasks.json` | the 20 tasks: PR, base and merge commits, hidden tests, problem text |
| `assistant/` | one directory per task (`task.md`, `workspace/`, `check.py`, `reference/`, `meta.json`), generators in `_build/`, `run_assistant.py` |
| `longctx/` | the long-context state probes: `corpus.py`, `logprob.py`, `recall.py`, two report scripts, and the 2026-10 SSM-dtype results ([README](longctx/README.md)) |
| `results/2026-10-2x5090/` | findings, CSVs, reports, per-run results |

## Quick start

Requirements: Docker, Python 3.12+, [uv](https://github.com/astral-sh/uv), an OpenAI-compatible endpoint. Coding tasks also need a clone of club-3090.

```bash
uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt
git clone https://github.com/noonghunna/club-3090 && export CLUB3090_REPO=$PWD/club-3090
docker build -t club-tasks-env:1 coding/env/

# coding: one config, one draw, then the comparison table
cd coding
../.venv/bin/python run_agent.py --config my-model --base-url http://HOST:PORT/v1 --model SERVED_ID --draw 1
../.venv/bin/python report.py my-model > report.md

# assistant tasks through omp (omp on PATH, or set OMP_BIN)
cd ../assistant
../.venv/bin/python run_assistant.py --harness omp --config my-model --base-url http://HOST:PORT/v1 --model SERVED_ID
```

```bash
# long-context probes: compare two servers that differ in one setting (needs SGLang and `tokenizers`; see longctx/README.md)
cd ../longctx
python3 corpus.py --repo $CLUB3090_REPO --tokenizer /path/to/tokenizer.json
python3 logprob.py --arm A --out logprob_A.json && python3 recall.py --arm A --out recall_A.json --tokenizer /path/to/tokenizer.json
# boot the other server, repeat with --arm B, then: logprob_report.py logprob_A.json logprob_B.json (and recall_report.py)
```

Use the Docker bridge address (`172.17.0.1` on Linux) for `HOST` when the server runs on the same machine: the containers can't reach `127.0.0.1` on the host. [`coding/README.md`](coding/README.md) and [`assistant/README.md`](assistant/README.md) cover flags, effort settings, scoring, and how to rebuild the tasks.

## Things to know before you compare numbers

- **Check what your harness sends.** If a request names no `reasoning_effort`, GLM-5.3-Flash's template thinks at max and Qwen3.8's at xhigh. omp's `qwen-chat-template` thinking format drops the effort; this repo's omp config uses `thinkingFormat: openai` with `enable_thinking` in `extraBody`.
- **20 pass/fail tasks are coarse.** One draw can't separate configs closer than about 4 tasks. Run two draws and use the paired comparison in `report.py`.
- **The answers are public.** `check.py` embeds expected values and `reference/` holds solutions. A model trained after this repo went public may have seen them; mine fresh PRs for new rounds.

## Using it on another repo

The coding pipeline works on any repo whose PRs land with tests: export merged PRs after your cutoff date with `gh`, filter by size and test files, keep the ones whose tests fail before the PR and pass after it in the offline image, then read the failures and add an `## Interface` section wherever a hidden test checks something the issue text never states. `coding/make_candidates.py`, `validate.py` and `build_tasks.py` assume club-3090's layout (tests in `scripts/tests/`); adjust those filters for yours.

## Credits

Tasks come from the club-3090 maintainer's and contributors' pull requests. The Hermes runner uses benchlocal-cli's sandbox. Harnesses by the mini-swe-agent, omp and Hermes authors.

## License

MIT, see [`LICENSE`](LICENSE). The coding tasks' problem text and tests come from club-3090 pull requests and stay under that repository's license (Apache-2.0).
