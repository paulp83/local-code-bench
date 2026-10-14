# club-3090 agent tasks (20 of 20 usable, 67 validated)

## #1172 (2026-09-05, area lib, 107 lines, text from issue #1171)
Hidden tests: scripts/tests/test-vram-breakdown.sh

```
bench.sh VRAM breakdown: drafter overwrites `model=`, and recurrent/drafter buffers fall into `unaccounted` (84% of the gap)

## Summary

`scripts/lib/vram_breakdown.py` reports the **drafter's** weights as `model=` on any
slug that pins a drafter to a GPU, because `_per_dev()` defaults to *last match wins*
and the drafter emits the same log line shape as the target model. Two further
buffers are never matched at all. The result is that `unaccounted` absorbs several
GiB of perfectly identifiable memory, which is exactly the figure #1118 wants to put
in front of users.

Measured on `glm53-flash-dual-iq3xxs-moecache` (GLM-5.3-Flash + DFlash2 drafter on CUDA1).

## Evidence

The boot log emits, in this order:

```
load_tensors:   CUDA1 model buffer size   = 3313.42 MiB   <- target model
...
load_tensors:   CUDA1 model buffer size   =  655.73 MiB   <- DFlash2 drafter
llama_kv_cache: CUDA1 KV buffer size      =   80.00 MiB   <- drafter KV
sched_reserve:  CUDA1 compute buffer size = 1606.48 MiB   <- drafter compute
```

The parser prints:

```
CUDA1: model=656  kv=1361  compute=5240  pool=9653  total=22992/24576MiB(94%)  unaccounted=6082
```

`model=656` is the drafter. The target model's **3,313 MiB is silently gone**.

## Three defects

| # | defect | location |
|---|---|---|
| 1 | `model` uses `agg=False` → last-wins → drafter **overwrites** target | `vram_breakdown.py:41` |
| 2 | `llama_memory_recurrent: … RS buffer size` matched by nothing. The `state` regex targets `_comp_state:` (DeepSeek), so GLM's recurrent state is dropped | `vram_breakdown.py:44` |
| 3 | drafter's **compute** buffer is dropped — `compute` is also `agg=False`, and the target re-reserves *after* the drafter loads, so the drafter's reservation is overwritten | `vram_breakdown.py:42` |

`kv` is correct — it already passes `agg=True`.

## Impact

CUDA1, same boot, `used=22,992 MiB`:

| accounting | `unaccounted` |
|---|---:|
| as reported today | **6,082** |
| + `model` summed (target + drafter) | 2,768 |
| + recurrent state counted | 2,563 |
| + drafter compute counted | **956** |

**84% of `unaccounted` is under-attribution, not genuine overhead.** The asymmetry that
made this visible — CUDA1 `unaccounted` 6,082 vs CUDA0 1,136 — is not routing entropy;
it is the drafter living on CUDA1 and being partly counted, partly not.

## Note for the fix — defect 3 is not a one-liner

Flipping `model` to `agg=True` is straightforward: two models, two buffers, they add.

`compute` is harder. The CUDA1 reservations are `5208.35` (target), `1606.48` (drafter),
then `5240.16` (target **re**-reserve, after the drafter loaded). The first and third are
the *same* buffer re-reserved and must not be summed; the second is additive. The log does
not label which context a `sched_reserve` line belongs to, so a purely positional rule
("lines after the drafter's `load_tensors` are the drafter's") is wrong here. Options worth
weighing: label the reservation in the engine log, or track re-reservations per device and
treat a strictly-smaller interleaved value as a distinct context.

Suggest fixing 1 and 2 first (unambiguous, ~3.5 GiB of the gap) and treating 3 separately.

## Repro

```
docker logs <serving-container> > boot.log
python3 scripts/lib/vram_breakdown.py boot.log
```
Compare `model=` against the **first** `load_tensors: CUDA<n> model buffer size` line.
Any slug with `-devd CUDA<n>` and a drafter reproduces it; a no-drafter boot does not.

## Related

Blocks the per-GPU drill-down in #1118 — the panel would render the drafter's weights as
the model's, and the target's weights as "other".

Work in /testbed (the club-3090 repository). Make the change in the source files. The repository's test suite for this behaviour will be checked after you submit; you may add or run tests, but your test edits are not graded.
```

## #1174 (2026-09-05, area lib/profiles, 110 lines, text from issue #1132)
Hidden tests: scripts/tests/test-pull-download-ladder.sh

```
[bug] hf_fetch.py CLI swallows rung-1 failure detail (bare exit 1); missing `hf` binary never falls through to rung 3

### What happened?

On a rig without the `hf` CLI installed, `hf_fetch.py` prints its starting announcement and then exits 1 with no diagnostics at all — no failure token, no detail, nothing on stderr. Two separate problems: (1) `_main()` discards `LadderResult.failure`/`detail` on the non-ok path and returns a bare 1, which contradicts the module's own #804/#812 contract ("every rung announces which rung ran", "logs are auditable") exactly at the moment it matters most; (2) `escalate()` (rungs 2/3) only engages when `is_xet_refusal(blob)` matches, so a rung-1 failure of the "tool unavailable" kind (`hf` missing, rc=127) kills the ladder — even though rung 3 (raw resolve + curl + sha256 gate) has no dependency on `hf` and would have served the pull fine. Expected: failure token + detail printed to stderr before exit, and command-not-found treated as fallback-eligible. Workaround: `pipx install "huggingface_hub[cli]"` → rung 1 completes normally ("DONE via rung 1 (classic LFS)").

### Steps to reproduce

```bash
On a host where `hf` is not in PATH (stdlib-only python3):

    python3 scripts/lib/profiles/hf_fetch.py unsloth/Qwen3.6-27B-MTP-GGUF \
      --local-dir /models/gguf/qwen3.6-27b-gguf/unsloth-mtp-q4km \
      --include "Qwen3.6-27B-Q4_K_M.gguf"; echo "EXIT=$?"

Output — the entirety of it:

    [hf-fetch] starting: unsloth/Qwen3.6-27B-MTP-GGUF -> /models/gguf/qwen3.6-27b-gguf/unsloth-mtp-q4km (1 file(s) to fetch)
    EXIT=1

The same invocation after `pipx install "huggingface_hub[cli]"` downloads and verifies fine via rung 1.
```

### Rig report — paste contents of `bash scripts/report.sh [--verify | --soak | --bench | --studio | --full]`

```markdown
Not applicable — pre-boot model-fetch path, no container started and no GPU on this host yet; see "Anything else?".
```

### Anything else?

HEAD 8abac569 (2026-09-01), Debian 13 (Proxmox VE 9), python3 3.13. No rig report: this is the model-fetch path, pre-boot — no container involved; host is being staged before its GPU arrives, so `report.sh` isn't runnable here. Related: the setup.sh `WEIGHT_SIZE_GB=variable` crash is filed as #1131 — we hit this one while working around that one.

Work in /testbed (the club-3090 repository). Make the change in the source files. The repository's test suite for this behaviour will be checked after you submit; you may add or run tests, but your test edits are not graded.
```

## #1203 (2026-09-07, area lib/profiles, 354 lines, text from PR problem section)
Hidden tests: scripts/tests/test-compose-facts-shared.sh

```
refactor(profiles): lift derive_compose_facts out of the cockpit into shared profiles (#1202 P1)

`derive_compose_facts` lived inside `club3090_cockpit.data`, and nothing outside the cockpit could import it. That is *why* the local model layer was write-only from the UI (#1153): **the UI owned the only implementation** of compose→spec derivation, so a user with an existing working compose had a door in c3 and no door at all from the CLI. Everything else in #1202 depends on this being shared.

`ComposeFacts`, `_ENGINE_BY_IMAGE` and `derive_compose_facts` move to `scripts/lib/profiles/compose_facts.py` (stdlib-only, matching `serve_override_defaults`, which must stay importable on the launcher's no-PyYAML path). `club3090_cockpit.data` delegates and re-exports `ComposeFacts` via module `__getattr__`, so **every existing caller and test is unchanged** — the 25 pinning tests in `test_compose_facts.py` / `test_compose_viewer.py` passed without edits.

Pure relocation. No behaviour change.

Work in /testbed (the club-3090 repository). Make the change in the source files. The repository's test suite for this behaviour will be checked after you submit; you may add or run tests, but your test edits are not graded.
```

## #1204 (2026-09-07, area lib/profiles, 131 lines, text from PR problem section)
Hidden tests: scripts/tests/test-registry-origin-field.sh

```
feat(profiles): make catalog provenance a first-class `origin` field; core wins (#1202 P2)

Publishing later must flip a value and leave the slug alone. That isn't speculative: **`export_pr.py` already renames on publish today**:

```python
core_slug = f"{ns}/{str(entry['slug'])[len(_LOCAL_SLUG_PREFIX):]}"
```

It strips `local/` and prefixes the engine namespace derived from the compose path — producing exactly the `<engine>/<name>` shape P3 gives local slugs. **After the hard-cut that arithmetic collapses to identity and publish stops being a rename**, so a user's scripts, notes and compose pins survive it. (It's also a fourth prefix-dependent consumer for P3, alongside `promote.py`, `demote.py` and the cockpit.)

Work in /testbed (the club-3090 repository). Make the change in the source files. The repository's test suite for this behaviour will be checked after you submit; you may add or run tests, but your test edits are not graded.
```

## #1209 (2026-09-07, area docs, 392 lines, text from PR problem section + interface)
Hidden tests: scripts/tests/test-catalog-amend.sh

```
feat(catalog): rename + update for local entries — the shadowing remedy we owed (#1202 P7)

The local layer was **create-and-delete only**: `promote.py` refuses every "already exists" case, `demote.py` only removes. Changing one field meant demoting and re-promoting.

That mattered more than ergonomics. #1204 decided a local slug colliding with a newly-shipped curated one is **shadowed** — kept and *marked* "so the user can rename it" — and no rename existed. **We advertised a remedy that could not be reached.**

## Interface (what the checks call and expect)

Add two subcommands to `scripts/catalog.sh`. Both change the LOCAL layer only (`scripts/lib/profiles-local/registry.local.json` under `--root DIR`) and accept `--root DIR` and `--dry-run`:
- `scripts/catalog.sh rename --slug OLD --to NEW`
- `scripts/catalog.sh update --slug SLUG --set KEY=VALUE`

Exit 0 on success. Refuse (non-zero exit) when the slug is a curated (core) slug, when renaming ONTO a curated slug, for `--set origin=...` (origin is not editable), and when NEW's engine namespace (the part before `/`) is not a known engine. `--dry-run` exits 0 and leaves the registry unchanged. After an amend, every entry's `engine` field equals its slug's namespace, the layer still loads through `scripts.lib.profiles.compose_registry.load_local_registry` with `origin: local` kept, and no file under `scripts/lib/profiles/` (the curated catalog) changes.

Work in /testbed (the club-3090 repository). Make the change in the source files. The repository's test suite for this behaviour will be checked after you submit; you may add or run tests, but your test edits are not graded.
```

## #1307 (2026-09-13, area preflight, 77 lines, text from issue #1306)
Hidden tests: scripts/tests/test-preflight-model-path-extract.sh

```
[bug] preflight refuses every gemma external-drafter slug: the path extractor captures a trailing backslash from escaped JSON

### The defect

`preflight.sh` refuses to boot **every gemma slug that uses an external assistant
drafter**, reporting a model file as missing when it is present on disk.

```
[preflight] ERROR: compose '.../gemma-4-26b-a4b/vllm/compose/single/awq/int8.yml'
            expects model files that aren't on host.
[preflight]   missing: /mnt/models/huggingface/gemma-4-26b-a4b-it-assistant\/config.json (HF model)
```

Note `assistant\/config.json`. The file exists:

```
-rw-rw-r-- 1 ... 2315 /mnt/models/huggingface/gemma-4-26b-a4b-it-assistant/config.json
```

Preflight exits 1, so the boot never starts. There is no way for a user to
satisfy this check, because the path it wants cannot exist.

### Mechanism

The in-container path extractor (`preflight.sh`, the vLLM branch feeding
`_preflight_compose_vllm_subdir`):

```
command grep -oE '/root/\.cache/huggingface/[^"'\''[:space:],]+'
```

The character class excludes `"`, `'`, whitespace and `,` — **but not backslash**.
These composes write the drafter path inside escaped JSON:

```
SPEC_ARGS=(--speculative-config "{\"model\":\"/root/.cache/huggingface/gemma-4-26b-a4b-it-assistant\",\"num_speculative_tokens\":$$_spec_n}")
```

so the match runs past the directory name, consumes the trailing `\`, and stops
at the `"`. The captured subdir is `gemma-4-26b-a4b-it-assistant\`, and the
existence check becomes `${model_dir}/gemma-4-26b-a4b-it-assistant\/config.json`.

The comment directly above that line explains why the class was deliberately
narrowed — to stop `${MODEL_SUBDIR:-default}` being truncated before the
`:-default` resolver ran. That fix is correct; the backslash simply was not
considered at the same time.

### Scope — 8 composes, all gemma

Every compose whose cache path is immediately followed by a backslash:

| model | composes |
|---|---|
| gemma-4-12b | `single/qat-w4a16/mtp.yml`, `single/autoround-int8/mtp.yml` |
| gemma-4-26b-a4b | `single/awq/int8.yml` |
| gemma-4-31b | `multi4/google-qat-w4a16/base.yml`, `single/autoround-int4/fp8-mtp.yml`, `dual/qat-w4a16/int8.yml`, `dual/autoround-int4/int8.yml`, `dual/autoround-int4/bf16-mtp.yml` |

**qwen3.8-27b is unaffected** — its MTP drafter is built-in, so no external model
path appears in the speculative config. Verified by booting
`vllm/qwen38-27b-dual-fast` successfully on the same rig the same day.

The 12b composes capture `${SPEC_MODEL_SUBDIR:-gemma-4-12b-it-assistant}\`, which
resolves to `gemma-4-12b-it-assistant\` — this is why a Discord report of a
missing **12b** assistant appeared while the user believed they were launching the
26b slug.

### Fix, and proof

Add `\\` to the exclusion class:

```diff
-  command grep -oE '/root/\.cache/huggingface/[^"'\''[:space:],]+'
+  command grep -oE '/root/\.cache/huggingface/[^"'\''\\[:space:],]+'
```

Captured paths before / after, on the 26b compose:

```
before:  /root/.cache/huggingface/gemma-4-26b-a4b-it-assistant\      <- unusable
after:   /root/.cache/huggingface/gemma-4-26b-a4b-awq-4bit
         /root/.cache/huggingface/gemma-4-26b-a4b-it-assistant
```

**Boot-verified on 2x3090.** With the fix applied, `vllm/gemma-26ba4b-single`
reaches `Application startup complete` in 180 s, engages the drafter, and serves:

```
[spec] drafter ON - draft-model gemma-4-26b-a4b-it-assistant n=4
[speculative.py:882] Overriding draft model max model len from 262144 to 176000
request -> "Paris"   (20 prompt / 2 completion tokens)
```

### Suggested guard

A test that runs the extractor against every compose and asserts no captured
subdir contains a character that cannot appear in a directory name (backslash,
quote, brace). That is the general form of this bug, and it would also have caught
the `${MODEL_SUBDIR` truncation the current comment describes.

### Related

Found while reproducing a Discord report. The same user also hits #1303 (setup
downloads a variant no slug uses) and #1304 (the drafter is opt-in behind an
undocumented flag). This issue is the third of three, and it would block them even
after the other two are solved.

Work in /testbed (the club-3090 repository). Make the change in the source files. The repository's test suite for this behaviour will be checked after you submit; you may add or run tests, but your test edits are not graded.
```

## #1464 (2026-09-28, area switch, 135 lines, text from PR problem section)
Hidden tests: scripts/tests/test-switch-refuse-before-teardown.sh

```
fix(switch): refuse a launch before tearing down the running slug

`switch.sh` brought the running slug down **first** and only then ran the checks that can refuse a launch. So a refused launch left the rig serving nothing. We hit it twice on the reference rig in one day:
- an experimental slug run without `--force`;
- a worktree whose model files weren't on the host (no `MODEL_DIR`).

A mistyped slug did the same.

Work in /testbed (the club-3090 repository). Make the change in the source files. The repository's test suite for this behaviour will be checked after you submit; you may add or run tests, but your test edits are not graded.
```

## #1470 (2026-09-28, area lib, 46 lines, text from PR problem section)
Hidden tests: scripts/tests/test-p2p-state.sh

```
fix(p2p): score SGLang's V1 custom all-reduce as on (PCIe rigs)

On a PCIe rig, a live SGLang custom all-reduce scores **`unknown`** in `report.sh` and on the bench card ("no P2P engagement signal"). It can never score `on`.

- SGLang admits `CustomAllReduceV2` only on full NVLink (`can_use_custom_all_reduce_v2` → `full_nvlink is True`), so every PCIe rig runs the **V1** `CustomAllreduce`.
- V1 logs nothing when it initializes. Its only success signal is `Registering N cuda graph addresses` after CUDA-graph capture, on rank 0.
- The classifier knew only V2's success line, `All Reduce config:`.


I found this while testing SGLang custom all-reduce as an opt-in on our P2P rig (follow-up to #1462). That boot registered its graph buffers (4352 → 258/68/18/6) and passed verify-full and a continuous soak. `report.sh` and the bench card still called it unknown.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Work in /testbed (the club-3090 repository). Make the change in the source files. The repository's test suite for this behaviour will be checked after you submit; you may add or run tests, but your test edits are not graded.
```

## #1510 (2026-10-01, area concurrency-probe, 199 lines, text from issue #1502)
Hidden tests: scripts/tests/test-concurrency-probe.sh

```
[bug] concurency-probe

### What happened?

Issue 1: concurrency-probe.sh --sweep crashes at the first skipped cell

A --sweep run exits with rc=1 as soon as it reaches a cell it decides to skip. A cell is skipped when it doesn't fit the KV pool, when the wall budget is exhausted, or on early-stop. Measured cells before that point print fine. The run never writes the concurrency card, the === recommend === block, or the results/concurrency-*.md/json files. On small cards some cell almost always overflows the pool, so in practice the sweep never finishes there.

- Root cause (scripts/concurrency-probe.sh:462): emit_row runs python3 - <<'PY'. python3 - reads its program from stdin, and the heredoc is stdin. So the JSON row the caller pipes in (printf … | emit_row) is replaced by the heredoc, sys.stdin.read() returns an empty string, and json.loads("") raises. Because the script uses set -e, that kills the sweep.
- Affected callers: all three skip paths go through emit_row — budget (:476), clipped (:481) and early-stop (:486). Measured cells are unaffected because they pass their data via argv.
- Repro: a standalone snippet that needs no GPU or server gives JSONDecodeError, rc=1, 0 bytes written.
- Suggested fix: pass the row as an argument (emit_row "$json", read with sys.argv[2]) instead of on stdin, and add a GPU-free regression test with a stubbed run_probe.
- Workaround: pick N_LIST/CTX_SWEEP so that no cell is skipped, e.g. run the 32K rung on its own.

Issue 2: VRAM and the GPU label are rig-wide, not the probed container's card(s)

On a multi-GPU rig, the probe reports memory and GPU names for the whole machine. It attributes both to the service under test.

- Evidence from our run: the container was pinned to the RTX 3060 only, and an unrelated SGLang service was running on GPUs 0–1. The probe reported 55319 MB and 4× GeForce RTX 3090. The real figure from nvidia-smi -i 3 was 10,381 MiB on 1× RTX 3060, flat for the whole run.
- Root causes:
  a. vram_used_mb() (scripts/lib/concurrency_probe.py:346) queries nvidia-smi without -i and sums memory.used across every GPU on the host.
  b. _gpu_fp() (scripts/concurrency-probe.sh:227) counts all GPUs and labels them all with GPU 0's name.
- Why it matters beyond cosmetics:
  - The VRAM-leak / 0-growth gate (vram_ok()) is judged on the rig-wide sum. Another service changing its memory use can fail a clean run, or hide a real leak.
  - The vram_peak_gb written to the envelope row and results JSON is wrong (54.0 GB for a 12 GB card).
- Suggested fix: resolve the GPUs behind CONTAINER (docker inspect → DeviceRequests or NVIDIA_VISIBLE_DEVICES). Scope both the VRAM query and the label to those cards, and record per-card peaks as the bench protocol requires. When no container can be resolved, fall back to rig-wide and say so.

### Steps to reproduce

```bash
-
```

### Rig report — paste contents of `bash scripts/report.sh [--verify | --soak | --bench | --studio | --full]`

```markdown
-
```

### Anything else?

_No response_

Work in /testbed (the club-3090 repository). Make the change in the source files. The repository's test suite for this behaviour will be checked after you submit; you may add or run tests, but your test edits are not graded.
```

## #1518 (2026-10-01, area lib, 65 lines, text from issue #1515 + interface)
Hidden tests: scripts/tests/test-switch-orphan-teardown.sh

```
[bug] switch.sh teardown fails since #1498: config_files label is comma-joined, passed as one -f

### What happened?

Since #1498 (`club3090.slug` label), every container that `switch.sh` / `launch.sh` / c3 starts is brought up with **two** compose files: the slug's compose plus the label override in `<data dir>/compose-labels/<container>.yml`. Docker Compose records both in the container label `com.docker.compose.project.config_files` as a **comma-joined** string.

`down_running()` in `scripts/switch.sh` passes that label to `-f` as a single path:

```bash
# scripts/switch.sh:1027-1031 (master @ 5cbb1db2)
lbl_file=$(docker inspect --format '{{ index .Config.Labels "com.docker.compose.project.config_files"}}' "$c" 2>/dev/null || true)
if [[ -n "$lbl_dir" && -n "$lbl_file" ]]; then
  (cd "$lbl_dir" && ${COMPOSE_BIN} -f "$lbl_file" down --remove-orphans) || docker stop "$c" >/dev/null
```

so every teardown now fails and quietly falls back to `docker stop`:

```
[switch] bringing down: vllm-qwen38-flash-next-multi3-mtp
compose file "~/club-3090/scripts/lib/profiles-local/composes/…/mtp.yml,~/.local/share/club-3090/compose-labels/vllm-qwen38-flash-next-multi3-int4mix-mtp.yml" is invalid: open ~/club-3090/…/mtp.yml,~/.local/share/club-3090/compose-labels/vllm-qwen38-flash-next-multi3-int4mix-mtp.yml: no such file or directory
```

(Seen on a local-layer slug here, but nothing in the path is local-specific: `slug_label.py` emits the override for every registry slug whose compose matches, so this should hit core slugs the same way.)

**Effect**

- `docker compose down --remove-orphans` never runs on a switch or on `switch.sh --down`. The old container is only **stopped, not removed**, and its compose network and any orphans stay behind. Switching between slugs leaves exited containers piling up.
- It doesn't show as a failure: relaunching the *same* slug still works because `up` recreates the stopped container, and a *different* slug comes up next to the stopped one. The only visible sign is the `compose file "…,…" is invalid` line in the middle of a switch, which reads like a broken compose.
- Same root cause, cosmetic only: `scripts/lib/bench-row-formatter.sh:403` passes the joined string to `rel()`, so a bench record's `compose` field holds `"/abs/a.yml,/abs/b.yml"` (not relativised, two paths) instead of the slug's compose.

The other readers of this label already split on `,`, so the fix is to do the same here:

| reader | handles the comma list? |
|---|---|
| `scripts/litellm-log.sh:62` | ✅ `IFS=',' read -ra cfgs` → one `-f` per file |
| `scripts/lib/resolved_config.py:449` | ✅ `raw.split(",")` |
| `tools/serve-cockpit/…/launch_settings_store.py` (`containers_for`) | ✅ `files.split(",")` |
| `scripts/switch.sh:1028` (`down_running`) | ❌ single `-f` |
| `scripts/lib/bench-row-formatter.sh:403` | ❌ whole string to `rel()` |

### Steps to reproduce

Read-only. It runs `config`, not `down`, so it doesn't touch the running container:

```bash
C=<any container started by switch.sh after #1498>
d=$(docker inspect -f '{{ index .Config.Labels "com.docker.compose.project.working_dir"}}' "$C")
l=$(docker inspect -f '{{ index .Config.Labels "com.docker.compose.project.config_files"}}' "$C")
echo "$l"                                          # two paths, comma-joined
(cd "$d" && docker compose -f "$l" config >/dev/null)   # -> "compose file … is invalid: … no such file or directory"

# Splitting it works:
(cd "$d" && IFS=',' read -ra a <<<"$l"; args=(); for x in "${a[@]}"; do args+=(-f "$x"); done
 f="$(bash scripts/settings.sh compose-env-file)"; docker compose --env-file "$f" "${args[@]}" config --services; rm -f "$f")
```

End-to-end: launch any slug with `bash scripts/switch.sh <slug>`, then run `bash scripts/switch.sh <slug>` again (or `--down`) and watch the `bringing down:` line.

### Suggested fix

In `down_running()`, mirror `litellm-log.sh`:

```bash
if [[ -n "$lbl_dir" && -n "$lbl_file" ]]; then
  local -a cfg_args=() _cfgs
  IFS=',' read -ra _cfgs <<< "$lbl_file"
  local f; for f in "${_cfgs[@]}"; do [[ -n "$f" ]] && cfg_args+=(-f "$f"); done
  (cd "$lbl_dir" && ${COMPOSE_BIN} "${cfg_args[@]}" down --remove-orphans) || docker stop "$c" >/dev/null
```

Two related points:

- The label override can be gone by teardown time (for example after the data dir moved). Dropping `-f` entries that no longer exist, or falling back to only the first file, would keep the `down` path working. The label file adds labels and nothing else, so `down` doesn't need it.
- `bench-row-formatter.sh:403` should take the first entry (`.split(",")[0]`) before `rel()`.

A regression guard could start a fake container with a two-file label (the docker shims `test-slug-label` already uses would do) and assert that `down_running` calls compose with two `-f` arguments.

### Environment

- master @ `5cbb1db2`, Docker Compose 5.5.1
- Introduced by e62eb703 (#1498)

## Interface (what the checks call and expect)

In `down_running()` (`scripts/switch.sh`): the container label `com.docker.compose.project.config_files` can hold several comma-joined paths. Pass each path as its own `-f`. Drop any listed file that no longer exists; if at least one remains, still run `<compose> -f <file> ... down --remove-orphans` with the remaining files; if none remains, fall back to `docker stop <container>` and don't call compose.

Work in /testbed (the club-3090 repository). Make the change in the source files. The repository's test suite for this behaviour will be checked after you submit; you may add or run tests, but your test edits are not graded.
```

## #1555 (2026-10-05, area concurrency-probe, 219 lines, text from PR problem section + interface)
Hidden tests: scripts/tests/test-concurrency-probe.sh

```
fix(concurrency-probe): card names the right container, GPUs and drafter (#1537)

The concurrency cards @xtj7 posted on #1537 were mislabelled, and both bugs reproduce on the reference rig:

- **vLLM said "spec off" with MTP n=4 running.** `_spec_fp` greps the container's `Cmd` for `--speculative-config`, but the Qwen3.8 vLLM composes build that flag inside their entrypoint script from `SPEC_N`, so it never appears in `Cmd`.
- **SGLang said "spec ?", listed every GPU on the host and measured VRAM rig-wide.** `CONTAINER` came from a `vllm-(qwen|gemma)` name heuristic, so an SGLang container was never found.

## Interface (what the checks call and expect)

In `scripts/lib/concurrency_probe.py`:
- `container_gpus(container)` treats one `HostConfig.DeviceRequests[].DeviceIDs` entry that contains commas (`["2,3"]`, which is what Compose produces from `device_ids: ["${ESTATE_GPUS}"]`) as GPUs 2 and 3, the same as `["2", "3"]`.
- New CLI flag `--container-for-url`: prints the name of the running container that publishes the port of `$URL` (from `docker ps`, any engine), or nothing if none does.
- New CLI flag `--spec-label`: prints the speculative-decoding label read from the engine. For vLLM (container `$CONTAINER`), read the `Initializing a V1 LLM engine ... with config: ... speculative_config=...` line at the HEAD of `docker logs` (not the tail): `SpeculativeConfig(method='mtp', ..., num_spec_tokens=4)` prints `MTP n=4`, `speculative_config=None` prints `spec off`. For SGLang, read `GET $URL/get_server_info` (`speculative_algorithm`, `speculative_num_steps`; EAGLE over the target's own checkpoint prints `MTP n=4`). Print nothing when neither source is readable.
- `scripts/concurrency-probe.sh` uses both flags (`--container-for-url` to resolve CONTAINER, `--spec-label` in `_spec_fp`).

Work in /testbed (the club-3090 repository). Make the change in the source files. The repository's test suite for this behaviour will be checked after you submit; you may add or run tests, but your test edits are not graded.
```

## #1556 (2026-10-05, area concurrency-probe, 124 lines, text from PR problem section)
Hidden tests: scripts/tests/test-concurrency-probe.sh

```
fix(concurrency-probe): card's KV pool, slot source and SGLang knob names (#1537)

Follow-up to #1555. Three more labels on @xtj7's #1537 cards were wrong:

- **"KV ?" on both engines.** `--detect-kv` only parsed vLLM's `GPU KV cache size` line, and only from the last 2,500 log lines. A container that has been serving for a while has scrolled past it.
- **`slots=4 (undetected)`, with the count right.** The source label skipped the two SGLang paths `_detect_slots` uses: `max-running-requests` in the container command, and `max_running_requests` on the server info.
- **The SGLang recommendation said `MAX_NUM_SEQS` / `MAX_MODEL_LEN`.** SGLang composes ignore both.

Work in /testbed (the club-3090 repository). Make the change in the source files. The repository's test suite for this behaviour will be checked after you submit; you may add or run tests, but your test edits are not graded.
```

## #1564 (2026-10-06, area catalog, 141 lines, text from PR problem section + interface)
Hidden tests: scripts/tests/test-catalog-cli.sh, scripts/tests/test_promote.py

```
fix(catalog): register --dry-run no longer writes the engine profile

`catalog.sh` wrote the engine profile itself, in its own Python, *before* handing the spec to `promote.py`, which owns the plan, the `--dry-run` exit and the confirm. Nothing downstream could stop a write that had already happened.

It also hid itself in the tests: `test-catalog-cli.sh` runs several `--dry-run` registers with the same engine before its real round trip. So the round trip's "engine profile written" check passed on the file the dry runs had leaked.

## Interface (what the checks call and expect)

`scripts/catalog.sh register ... --dry-run` writes nothing, including no `engines.d/<engine>.yml`. Move the engine-profile write out of `catalog.sh` into `scripts/lib/profiles/promote.py`, carried in the spec as `local_engine_profile`, so it goes through promote's plan, `--dry-run` exit and confirm with the rest. The printed plan lists it with the text `engines.d/<engine>.yml (new local ENGINE profile)`.

Work in /testbed (the club-3090 repository). Make the change in the source files. The repository's test suite for this behaviour will be checked after you submit; you may add or run tests, but your test edits are not graded.
```

## #1571 (2026-10-06, area lib, 166 lines, text from PR problem section + interface)
Hidden tests: scripts/tests/test-report-gpu-attribution.sh

```
fix(report): attribute each GPU's VRAM to the process that holds it (#1537)

`report.sh` → "Display / desktop state" found **one** running club container and credited it with **every** card that had more than 100 MiB in use. #1537's report said GPUs 0 and 2 were "held by running `sglang-cmp170hx`", but that container could only see GPU 1, and `nvidia-smi` showed another container's `VLLM::Worker_TP0/1` on GPUs 0 and 2.

## Interface (what the checks call and expect)

Add `gpu_vram_report_lines OUR_CONTAINER` to `scripts/lib/gpu-select.sh` (OUR_CONTAINER may be empty), and make `scripts/report.sh` call it as `gpu_vram_report_lines "$our_container"` in place of its own per-container line. It prints one line per GPU containing `**GPU <index> idle VRAM:**`, using `nvidia-smi --query-gpu=index,uuid,memory.used` and `nvidia-smi --query-compute-apps=gpu_uuid,pid,process_name`. Attribute each GPU to the process on it: map a pid to a container through `<proc>/<pid>/cgroup` (`.../docker-<id>.scope`; the proc root comes from `$GPU_ATTR_PROC`, default `/proc`) and `docker ps` (id to name). Line text the tests look for:
- our container: `held by running \`<ours>\``
- another container: `held by \`<other>\``, plus `not \`<ours>\`` when OUR_CONTAINER is set
- a process outside any container: `held by \`<process_name>\``
- when the host lists no compute processes, place ours from `docker exec <ours> nvidia-smi ...` (the container's own view); a card with memory in use and no owner reads `⚠ something is using this GPU` ... `not \`<ours>\``
- an idle card (a few MiB) ends with `<N> MiB ✓`.

Work in /testbed (the club-3090 repository). Make the change in the source files. The repository's test suite for this behaviour will be checked after you submit; you may add or run tests, but your test edits are not graded.
```

## #1573 (2026-10-07, area docs, 38 lines, text from PR problem section)
Hidden tests: scripts/tests/test-quality-thinking-budget.sh

```
fix(quality-test): read vLLM's boot log when the parser isn't in the container argv

`quality-test.sh --thinking-budget N` on vLLM checks that the server has a reasoning parser, because vLLM rejects `thinking_token_budget` per request without one. The check only looked at the container's argv (`docker inspect`).

An image that starts vLLM **through its own launcher** adds `--reasoning-parser` inside that script, so the argv shows none. The wrapper then refused with "booted WITHOUT --reasoning-parser", which counts as positive evidence and so can't be overridden with `THINKING_BUDGET_UNVERIFIED=1`.

Seen on bucko's official image. Its `qwen38-serve` adds `--reasoning-parser qwen3`, and the server's boot log shows `'reasoning_parser': 'qwen3'` in `non-default args`. Sending the budget directly worked: `thinking_token_budget: 200` cut reasoning from 1,343 to 548 characters, and the answer was still produced.

Work in /testbed (the club-3090 repository). Make the change in the source files. The repository's test suite for this behaviour will be checked after you submit; you may add or run tests, but your test edits are not graded.
```

## #1588 (2026-10-09, area AGENTS.md, 126 lines, text from PR problem section)
Hidden tests: scripts/tests/test-concurrency-probe.sh

```
fix(concurrency-probe): pick the container that serves the URL (#1584 follow-up)

`concurrency-probe.sh` picked its container in two ways, and both are wrong for a URL on another machine:

1. **Port-only match.** The Python `container_for_url` (#1537) compared the port and ignored the host, so `URL=http://<other host>:8020` bound the local container on :8020.
2. **Name fallback.** When nothing matched, the `vllm-(qwen|gemma)` heuristic bound one anyway.

That container supplies the slot count (`served-slots.sh` reads its `--max-num-seqs` first), the GPU label, the spec label and the KV pool. A remote run therefore reported the local server's values as its own. Reproduced: with a local vLLM on :8020 at `--max-num-seqs 4`, `URL=http://10.9.9.9:8020` announced `CONCURRENCY=4 (detected: container max-num-seqs)`.

Work in /testbed (the club-3090 repository). Make the change in the source files. The repository's test suite for this behaviour will be checked after you submit; you may add or run tests, but your test edits are not graded.
```

## #1608 (2026-10-10, area models, 5 lines, text from issue #1599)
Hidden tests: scripts/tests/test-compose-args-array-scope.sh

```
test-compose-args-array-scope: false failure on vllm single-fast — assignments inside case arms aren't seen

## What fails (on `master`, 6305d83a)

```
FAIL: models/qwen3.8-27b/vllm/compose/single/autoround-int4/mtp.yml: exec uses ${LM_ONLY_ARGS[@]} but it is never assigned
```

## Why it's the test, not the compose

`LM_ONLY_ARGS` is assigned on every path that reaches the `exec`. The `case` has an arm for each valid value, and its default arm exits:

```sh
case "$$VISION" in
  on) LM_ONLY_ARGS=() ;;
  off) LM_ONLY_ARGS=(--language-model-only) ;;
  *) echo "[size] VISION='$$VISION' must be on or off" >&2; exit 1 ;;
esac
```

(`models/qwen3.8-27b/vllm/compose/single/autoround-int4/mtp.yml` ~l.255–259, from #1540.) The guard has two blind spots here, in `scripts/tests/test-compose-args-array-scope.sh`:

1. It only counts an assignment at the start of a line: `re.match(rf'^\s*{arr}=\(', l)` (~l.84). `on) LM_ONLY_ARGS=() ;;` starts with the case pattern, so it reads "never assigned".
2. Its scope model treats `case`/`esac` as one nested scope and only `else`/`elif` as alternatives. So even a matched assignment inside an arm would not count as dominating the `exec`, though an exhaustive case (every arm assigns or exits) does dominate.

## Suggested fix

Pick one:
- **Compose (smallest):** initialise `LM_ONLY_ARGS=()` before the `case`. That's harmless and makes the dominance obvious to readers and to the guard.
- **Guard:** recognise `pattern) NAME=(` assignments, and treat a `case` whose every arm assigns `NAME` or exits as dominating. Add a fixture for both.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Work in /testbed (the club-3090 repository). Make the change in the source files. The repository's test suite for this behaviour will be checked after you submit; you may add or run tests, but your test edits are not graded.
```

## #1610 (2026-10-10, area lib/profiles, 112 lines, text from issue #1597 + interface)
Hidden tests: scripts/tests/test-patch-attribution.sh

```
patch_attribution.reaches(): the legacy fallback reports install-script patches as wired after their mount and invoke are removed

## What happens

For any `patches.yml` entry with `delivery.entrypoint_invoke: true`, `patch_attribution.reaches()` returns **True** even when the compose no longer mounts or invokes the patch. So `test-patch-attribution` (and every other consumer of `reaches()`) cannot detect an install-script patch that has been unwired from a compose.

## Repro

Strip a patch's mount and invoke lines from a copy of a compose that carries it, then ask `reaches()` and the sound check `_spec_wiring_present()`:

| patch | compose | `reaches()` on the real compose | `reaches()` with the patch's mount + invoke removed | `_spec_wiring_present()` on the stripped copy |
|---|---|---|---|---|
| `vllm-flashinfer-decode-pin` | `qwen3.8-27b/vllm/compose/dual/autoround-int4/mtp.yml` | True | **True** | False |
| `qwen38-sglang-autoround-w4a8-v0519` | `qwen3.8-27b/sglang/compose/dual/fp8/mtp.yml` | True | **True** | False |
| `vllm-effort-budget` * | `qwen3.8-27b/vllm/compose/dual/autoround-int4/mtp.yml` | True | **True** | False |
| `qwen38-sglang-effort-thinking-budget` * | `qwen3.8-27b/sglang/compose/dual/autoround-int4/mtp.yml` | True | **True** | False |

\* new entries on the upcoming effort-budget branch; the first two are on `master` today.

The stripped copies had no line left mentioning the patch in the service body; the sound path correctly says False, the fallback overrides it.

## Cause

`scripts/lib/profiles/patch_attribution.py`, the legacy `delivery:` fallback in `reaches()` (from `if delivery.get("entrypoint_invoke"):`, ~line 546):

```python
for rel in patch.get("files") or []:
    target = root / rel
    markers = [Path(rel).name]
    if target.is_dir():
        markers.append(Path(rel).parent.name)   # ← "patches"
    if any(marker in body for marker in markers):
        return True
```

- A **directory** entry adds its parent's name — always `patches` — as a marker, and every compose that mounts *any* `…/patches/…` dir contains that string.
- A **file** entry uses the bare filename — e.g. `install.sh` — which every compose that runs *any* install script contains.

So for these entries the fallback is effectively always True, and the sound `delivery_spec` check (`_spec_wiring_present`) never gets the final say.

## Suggested fix

- When an entry has a `delivery_spec` (all four above do), let `_spec_wiring_present()` decide and skip the legacy fallback.
- Where the fallback must stay (entries with only the `delivery:` block), drop the parent-dir marker and treat generic filenames (`install.sh`, `apply.py`, …) as non-identifying; match the patch dir's own name or its declared mount target instead.
- Add a negative control to `test-patch-attribution.sh`: a fixture compose with a patch's mount + invoke removed must report not-reached.

Found while wiring the effort-budget patches (vLLM + SGLang); the wiring there is verified separately by per-service `docker compose config` checks, not by this test.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Interface (what the checks call and expect)

`reaches(root, patch, compose)` in `scripts/lib/profiles/patch_attribution.py`, for install-script patches (`delivery.entrypoint_invoke: true`): return False when the compose no longer has the patch's mount and invoke (the legacy fallback must stop answering True), and return False for a compose that mounts a DIFFERENT patch at the same in-container target path. Match the mount's source to this patch, not just the target. A patch must still reach its own load-bearing compose.

Work in /testbed (the club-3090 repository). Make the change in the source files. The repository's test suite for this behaviour will be checked after you submit; you may add or run tests, but your test edits are not graded.
```

## #1612 (2026-10-10, area lib/profiles, 242 lines, text from issue #1611 + interface)
Hidden tests: scripts/tests/test-patch-attribution.sh

```
patch_attribution: chat-template patches 'reach' composes that use a different template (qwen38 109 vs 62, apex 91 vs 4, glm53 91 vs 0)

## What happens

`patch_attribution.reaches()` still over-reports for `delivery_mechanism: chat_template` patches. #1610 fixed the install-script class; chat templates go through their own branch (`compose_effective_text` + `_spec_wiring_present`) and weren't part of that change. Measured on `master` (9a72acf2), counting `models/*/*/compose/*/*/*.yml`:

| patch | reaches | load-bearing | composes it "reaches" without being declared for them |
|---|--:|--:|---|
| `qwen38-reasoning-effort-template` | **109** | 62 | 47: Gemma 4 (31B/26B/12B), qwen3.6-27b, qwen3.6-35b-a3b, tess-4, GLM-5.3 llama.cpp, plus 2 Qwen3.8 SGLang |
| `apex-qwen-chat-template` | **91** | 4 | 87: every vLLM compose that passes `--chat-template`, plus GLM / Inkling llama.cpp |
| `glm53-minja-numeric-index` | **91** | 0 | 91 |
| `gemma-google-canonical-chat-template` | 12 | 12 | 0 ✅ |
| `qwen-froggeric-chat-template` | 15 | 16 | 0 ✅ |

Example: `reaches(qwen38-reasoning-effort-template, models/gemma-4-31b/vllm/compose/dual/qat-awq-int4/base.yml)` → **True**.

So `test-patch-attribution` can't tell whether these templates are actually wired into their load-bearing composes. Any compose that mounts *some* template passes for all three.

## Causes (`scripts/lib/profiles/patch_attribution.py`)

1. **The bare `--chat-template` flag counts as an invoke marker.** For chat-template specs whose `invoke` mentions it, `_spec_wiring_markers` appends `"--chat-template"` and `mounted_at` as separate invoke markers, and `inv_ok` is an `any(...)`. The flag alone therefore satisfies the invoke check. It is also a substring of `--chat-template-file`. The code comment says the explicit style should "require BOTH tokens in the merged body"; the implementation requires either one.
2. **`wired_at: [volumes, command]` isn't a recognised combination.** apex and glm53 declare `command`, while the code only knows `volumes` / `entrypoint`. So they fall to the "unknown: any declared marker" branch, where the bare flag above decides alone.
3. **`qwen38-reasoning-effort-template` has `mounted_at: /chat_template.jinja`**, a suffix, because it's mounted over each model dir's own `chat_template.jinja`. Any compose that mounts any template over a model directory matches it.

## Suggested fix

- **Never use the bare `--chat-template` flag as a marker on its own.** For the explicit-flag style, require the flag *and* the mount path, as the comment intends: both present, or adjacent list items in the merged body.
- **Treat `command` like `entrypoint`** in `wired_at` (both are the launch-command insertion point), or normalise one to the other in `patches.yml`.
- **Make the chat-template volume marker source-aware**, the way #1610 did for install scripts: the vendored template's own directory or filename (`qwen38-reasoning-effort-template/…`, `apex-qwen-chat-template.jinja`, `glm53-minja-numeric-index/…`) must be on the same line as the mount target.
- **Add negative controls to `test-patch-attribution`:** the Qwen3.8 template must not reach a Gemma compose, and apex / glm53 must not reach a vLLM compose that only passes `--chat-template` for its own template. Like #1610's controls, they should fail on the current code.

Follow-up to #1597 / #1610.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Interface (what the checks call and expect)

`reaches(root, patch, compose)` in `scripts/lib/profiles/patch_attribution.py`, for `delivery_mechanism: chat_template` patches: True only when the compose both mounts THIS patch's template file (match the mount source to the patch) and passes `--chat-template` / `--chat-template-file` naming that mounted path. False when the mount is removed, when the flag is removed, when the flag names another file, or when the compose runs another patch's template. A bare `--chat-template` flag elsewhere doesn't count, and neither does `--chat-template` matched as a prefix of `--chat-template-file`. Each template must still reach its own load-bearing compose, including through Compose `extends`.

Work in /testbed (the club-3090 repository). Make the change in the source files. The repository's test suite for this behaviour will be checked after you submit; you may add or run tests, but your test edits are not graded.
```

## #1621 (2026-10-10, area docs, 148 lines, text from PR problem section + interface)
Hidden tests: scripts/tests/test-quality-server-budget.sh

```
fix(quality-test): read a llama.cpp server's reasoning budget back too

`quality-test.sh` reads the server's reasoning budget back, so it can size the client thinking cap and record the budget. It only understood the vLLM / SGLang `[effort-budget] v1` boot line. On a llama.cpp slug it reported **"server budget: unknown"**, so:

- **The answer could be cut off.** The thinking cap stayed at **16384** while the server's budget is **32768** (the qwen3.8 llama.cpp default since #1617). Reasoning past 16384 was cut by the client cap (`token_limit`) instead of the server closing it gracefully with room for the answer.
- **The budget went unrecorded.** The `Quality:` line and benchlocal's `server_thinking_budget` never recorded it.

## Interface (what the checks call and expect)

Messages the tests check on the wrapper's output, when no `[effort-budget]` readback line exists and the container is llama.cpp (read the boot command from `docker inspect`, resolving `${REASONING_BUDGET:-N}` as the shell would):
- found N: `server budget N reasoning tokens (llama.cpp --reasoning-budget, the same for every effort), read from <container>'s boot command — thinking cap raised to M` (M = N + the 4096 answer headroom when N is above the default cap); the `Quality:` line carries `, budget=server N, ` with no effort tag; benchlocal-cli gets `--server-thinking-budget N`.
- `-1` or no flag: `server budget: off (<container> boots llama.cpp with --reasoning-budget -1 or none: unrestricted)`, `budget=server off` on the Quality line, no number recorded.
- unresolvable: `server budget: unknown (llama.cpp --reasoning-budget unresolvable` and no `budget=` stamp.
- with `--thinking-budget B`, B is verified against the boot value and its own cap wins: `the --thinking-budget B this run verified; cap from --thinking-budget`, and no `--server-thinking-budget` is sent.

Work in /testbed (the club-3090 repository). Make the change in the source files. The repository's test suite for this behaviour will be checked after you submit; you may add or run tests, but your test edits are not graded.
```

