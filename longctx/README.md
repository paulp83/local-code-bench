# Long-context state probes

Two teacher-forced probes that answer one question: **does changing a serving setting change what the model does with
a very long context?** You run each probe against two servers that differ in one setting (a recurrent-state dtype, a
KV-cache dtype, a quant), then compare the two outputs. Because the model is never asked to generate, there is no
sampling noise: two reruns of `logprob.py` on the same server matched to four decimals, so a difference you see between servers is the setting, not run-to-run luck.

| Probe | Measures | Cost per server |
|---|---|---|
| `logprob.py` | log-prob of the real next token on the last 256 tokens of 8K to 250K-token prefixes | about 20 minutes |
| `recall.py` | whether the model returns a fact planted early, and whether it prefers a later correction over the stale value | about 20 minutes |

Use `logprob.py` to see if error **accumulates with position** (the gap between servers grows with length). Use
`recall.py` for **far-back recall**, which ordinary text hardly tests: next-token prediction leans on recent tokens, so a
degraded memory can still score the same on it.

The agent benches in this repo score whole tasks with a few draws, and a task with a noisy pass rate can't separate two
configs. These probes are the cheaper, deterministic check to run first.

## Requirements

- Two servers (or one server booted twice) exposing **SGLang's native API**: `POST /generate` with `input_ids`,
  `return_logprob`, `logprob_start_len`, `top_logprobs_num` and `token_ids_logprob`, and `POST /flush_cache`. Other
  engines name these differently and are not supported.
- `pip install tokenizers` and the served model's `tokenizer.json`. The probes send token ids, so both servers must
  use the same tokenizer.
- A markdown corpus for the filler text. `corpus.py` builds it from a clone of
  [club-3090](https://github.com/noonghunna/club-3090).
- A context window of at least 250K tokens, or pass shorter `--lengths`.

## Run it

```bash
cd longctx
# 1. filler: 8 shuffled orderings of the repo's docs, 250K tokens each -> corpus/docA.json ... docH.json
python3 corpus.py --repo ~/club-3090 --tokenizer /path/to/tokenizer.json --out corpus

# 2. boot server A (baseline), then score it
python3 logprob.py --arm bf16 --out logprob_bf16.json --base-url http://localhost:8173
python3 recall.py  --arm bf16 --out recall_bf16.json  --base-url http://localhost:8173 --tokenizer /path/to/tokenizer.json

# 3. boot server B (one setting changed), score it the same way
python3 logprob.py --arm fp32 --out logprob_fp32.json --base-url http://localhost:8173
python3 recall.py  --arm fp32 --out recall_fp32.json  --base-url http://localhost:8173 --tokenizer /path/to/tokenizer.json

# 4. compare
python3 logprob_report.py logprob_bf16.json logprob_fp32.json
python3 recall_report.py  recall_bf16.json  recall_fp32.json
```

Flags that matter: `--docs ABCDEFGH` (how many filler documents, more means tighter intervals), `--lengths
8192,32768,131072,250000`, `--window 256` (`logprob.py`: tokens scored per prompt). A smoke test is `--docs A
--lengths 8192`. Both scripts write results after every prompt, and `recall.py` resumes from an existing `--out`.

## Reading the output

`logprob_report.py` prints, per prefix length: mean NLL for each server, the paired NLL difference with a bootstrap 95%
CI over documents, the mean absolute log-prob difference, and top-1 agreement. A setting that damages long-range state
shows as a difference and a disagreement that **grow with L**. A flat mean absolute difference is the numerical jitter
between the two settings, not damage.

`recall_report.py` prints per fact kind and length: the mean **margin** for each server (log-prob of the correct name minus
the alternative, positive means the right name wins), the paired difference with a CI, and the share of queries the model
gets right. Each prompt carries 4 `plant` facts (a name stated once, early) and 4 `update` facts (a name stated early, then
corrected near the midpoint). For plants the alternative is a name that never appears. For updates it is the stale name.
Update margins sit near zero when the model can't tell a correction from the original.

Compare a difference to the **size of the margins**, not to zero: a 0.06 gap against a margin of 11 is nothing, against a
margin of 0.4 it needs a look at the CI.

## Gotchas

- Boot both servers from the same build, with the same flags except the one under test. The tools assert that both
  servers scored identical token ids and refuse to compare otherwise.
- `logprob.py --window` above about 256 ran an SGLang slug at `mem_fraction_static 0.95` out of memory (the logits for
  the window are allocated at once). Lower the window before raising memory.
- `/flush_cache` returns 400 while a request drains, and `common.py` retries it. Between prompts it empties the prefix
  cache so each prompt is prefilled from scratch. The eight queries of one `recall.py` prompt share its prefix on
  purpose.
- Plan for one hour per server. The longest prompt (250K tokens) prefills in about 100 seconds on 2× RTX 5090.
- The `corpus.py` header line names each file relative to the repo, so results depend on the club-3090 revision you
  point it at. The results below used revision `a39ec710`.

## Result: SSM-state dtype on ThinkingCap-Qwen3.8-27B (2026-10-24)

[`results-2026-10-ssm-dtype/`](results-2026-10-ssm-dtype/) holds the raw outputs and the two reports. Question from
[club-3090 discussion #1690](https://github.com/noonghunna/club-3090/discussions/1690): does the `bfloat16` recurrent
(GatedDeltaNet) state in `sgl/thinkingcap38-27b-dual-fast` lose information that SGLang's default `float32` keeps?
Same slug and build (club-3090 `a39ec710`), 2× RTX 5090, one boot per arm:

```bash
bash scripts/switch.sh --force sgl/thinkingcap38-27b-dual-fast                         # bf16, the slug default
MAMBA_SSM_DTYPE=float32 bash scripts/switch.sh --force sgl/thinkingcap38-27b-dual-fast # fp32
```

`logprob.py`, 8 documents (NLL gap is bf16 minus fp32):

| Prefix | Mean abs log-prob diff | Top-1 agreement | NLL gap, 95% CI |
|---|---|---|---|
| 8K | 0.027 | 98.5% | +0.0023 [+0.0003, +0.0042] |
| 32K | 0.023 | 98.6% | +0.0003 [-0.0026, +0.0032] |
| 131K | 0.023 | 98.9% | -0.0009 [-0.0037, +0.0018] |
| 250K | 0.023 | 98.7% | -0.0001 [-0.0021, +0.0018] |

`recall.py`, 8 documents, 256 paired queries:

| Fact | Prefix | Margin bf16 | Margin fp32 | Correct, bf16 / fp32 |
|---|---|---|---|---|
| planted once | 8K | 11.56 | 11.56 | 100% / 100% |
| planted once | 32K | 10.71 | 10.71 | 100% / 100% |
| planted once | 131K | 11.00 | 11.00 | 100% / 100% |
| planted once | 250K | 10.05 | 10.04 | 100% / 100% |
| corrected later | 8K | 1.01 | 1.02 | 72% / 72% |
| corrected later | 32K | 0.34 | 0.32 | 53% / 50% |
| corrected later | 131K | 0.49 | 0.44 | 56% / 66% |
| corrected later | 250K | 1.91 | 1.89 | 84% / 84% |

Reading: the state dtype does not change next-token prediction (flat in position) or recall (largest paired gap 0.06
nats). A fact stated once is recalled perfectly to 250K tokens in both arms; a corrected fact is handled poorly in both,
so that weakness belongs to the model, not the dtype. Limits: one prompt format, 8 filler documents, 32 queries per
cell, one model. The raw files were produced before the corpus header was made repo-relative, so a rerun reproduces the
shape of these numbers, not their last digit. Within one setup the probes are exactly repeatable.
