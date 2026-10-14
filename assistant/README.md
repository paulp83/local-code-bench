# Assistant bench: checkable non-coding tasks

26 everyday assistant tasks for testing a model plus harness (omp, Hermes, mini-swe-agent) in the offline sandbox. The coding bench in `../coding/README.md` asks
whether a model can fix real PRs. This set asks whether it can finish ordinary desk work and leave a result a script can verify: a file written, a value found, a state changed.

It is meant to be hard in places. Every task has a deterministic check, and no task needs the network.

## Layout

One directory per task:

| Path | What it is | Shown to the agent? |
|---|---|---|
| `task.md` | the prompt: goal, inputs, exact deliverable paths and formats | yes |
| `workspace/` | synthetic seed files, copied to `/workspace` | yes |
| `check.py` | reads `/workspace` after the run, prints `PASS <check>` / `FAIL <check>: <why>` lines and a final `PASS: N FAIL: M`; exit 0 only if nothing failed | **no** |
| `reference/` | a hand-built solution that overlays the workspace (`_delete.txt` lists paths the solution removes) | **no** |
| `meta.json` | id, source, category, difficulty, est_minutes, needs_web, notes | no |

`check.py` embeds the expected values, and `reference/` holds the answers. A runner must copy only `task.md` and `workspace/` into the sandbox.

## Tasks

| Id | Title | Category | Difficulty | Source | Est. min |
|---|---|---|---|---|---|
| `01-issue-effort-buckets` | Bucket the open issues by effort | triage | easy | session | 10 |
| `02-thread-asks` | List what the maintainer asked of @nina-t | reading | medium | session | 8 |
| `03-rig-report-table` | Summarise the rig report as a table | summarising | easy | session | 10 |
| `04-archive-filing` | File a result doc into the archive | filing | medium | session | 8 |
| `05-cold-storage-move` | Move a run directory to cold storage | files | medium | session | 10 |
| `06-job-chain-status` | Turn a job-chain log into a status table | summarising | medium | session | 8 |
| `07-forum-reply-style` | Draft the forum reply | writing | medium | session | 10 |
| `08-models-slug-index` | Index the models folder against the slug registry | filing | medium | session | 12 |
| `09-handoff-doc` | Write a handoff for the next session | writing | medium | session | 10 |
| `10-pair-rig-quality` | Pair rig reports with quality results | reconciliation | hard | session | 15 |
| `11-gpu-job-schedule` | Schedule a chain of jobs on two GPUs | planning | hard | session | 20 |
| `12-plan-revision` | Revise a plan document | writing | hard | session | 18 |
| `13-inbox-triage` | Triage the inbox | triage | easy | novel | 12 |
| `14-meeting-slot` | Find a meeting slot for three people | scheduling | hard | novel | 20 |
| `15-expense-report` | Expense report in USD | finance | hard | novel | 20 |
| `16-travel-itinerary` | Build an itinerary from bookings | planning | hard | novel | 15 |
| `17-policy-diff` | Diff two versions of a policy | documents | hard | novel | 15 |
| `18-contacts-cleanup` | Clean up a contacts export | data-cleaning | medium | novel | 15 |
| `19-bank-categorisation` | Monthly totals per category | finance | hard | novel | 25 |
| `20-notes-to-actions` | Turn meeting notes into actions | extraction | medium | novel | 12 |
| `21-photo-organise` | Organise photos by capture date | files | easy | novel | 8 |
| `22-form-fill` | Fill in the application form | forms | easy | novel | 6 |
| `23-recipe-scaling` | Scale a recipe from 4 to 10 servings, in metric | documents | easy | novel | 6 |
| `24-needle-in-notes` | Find three facts in 200 notes | retrieval | easy | novel | 6 |
| `25-config-edit` | Edit a settings file | config | easy | novel | 5 |
| `26-invoice-reconciliation` | Reconcile payments against invoices | finance | hard | novel | 20 |

Difficulty is about how much the agent has to get right at once, not about length:

- **easy** (8): one rule set, one output, a few checks. A careful model should pass most.
- **medium** (9): several interacting rules, a format contract, or a state change with side conditions (file moves, index rows, relative dates).
- **hard** (9): traps and computation. Examples: an optimal schedule, supersession and alias rules, time-zone arithmetic with local-time constraints, ordered-rule precedence, cross-reference renumbering, multi-invoice allocation.

## Sources

12 tasks are `session-derived`: their shape comes from recurring non-coding work in the maintainer's omp and Claude Code sessions (read at project-directory level: the club-3090 repo and a private notes project). Every fixture was rebuilt from synthetic data. No session text, path, host or account name was copied.
14 are `novel`: work the maintainer does not do routinely (inbox, calendar, expenses, travel, contacts, photos, recipes, forms, banking, invoices).

## How scoring works

Each check line is one criterion. A task's score is `PASS / (PASS + FAIL)` for partial credit, and the task is solved only on exit code 0. A crashing check counts as a failure,
and a check that cannot find its output prints `FAIL`. Checks use only the standard library and run with `python3 -I check.py /workspace`.

Rules every task follows, taken from the coding bench's lessons:

1. Everything a check tests is written in `task.md`: paths, field names, units, rounding, ordering.
2. Checks parse JSON, CSV and ICS or compare exact values. There is no LLM judge in v1.
3. Each task must FAIL on its untouched workspace and PASS on workspace plus `reference/`. `_build/validate.py` verifies this for all tasks.

## Add or change a task

Tasks are generated, so seed data and reference stay consistent. Add a function to `_build/t_a.py`, `t_b.py` or `t_c.py` that calls `task(...)` (see `_build/common.py`) with the prompt,
a `{path: content}` workspace, a check body, the reference files and the expected values; set `DIFF[id]`; then:

```bash
cd _build && python3 -c "import common,t_a,t_b,t_c; common.emit()" && python3 validate.py
```

`emit()` rewrites the directories of the tasks registered in the generators you import, so edit the generators, not the generated files. The 2026-10-12 fixes to tasks 02 and 07 are in the generators too, so re-emitting reproduces the current text.

## Running it

`run_assistant.py` puts each task through Hermes or omp in an offline container and scores the result on the host.

```bash
cd assistant
../.venv/bin/python run_assistant.py --harness hermes|omp --config TAG \
  --base-url http://HOST:PORT/v1 --model SERVED_ID [--draw N] [--jobs N] [--only 23,24] [--effort low]
```

Use `../.venv/bin/python`: it imports `../coding/run_omp.py`, which pulls in `minisweagent`. Hermes needs the Hermes sandbox from [benchlocal-cli](https://github.com/noonghunna/benchlocal-cli) (`sandboxes/hermes/`): build its image (`HERMES_IMAGE`, default `benchlocal-sandbox-hermes:latest`) and point `HERMES_AGENT_RUNNER` at its `verification/agent-runner.py`.

What happens per task:

1. `workspace/` is copied to a temp dir and mounted at `/workspace`. Only `task.md` (plus one line: work in `/workspace`, stop when done) goes in as the prompt. `check.py` and `reference/` never enter the container.
2. The container runs `--network none` as the host user, with a fresh `HOME`. The only route out is `fwd.py`: container `127.0.0.1:18000`, a mounted unix socket, the host, then the model server.
3. omp runs from the host binary in `club-tasks-env:1`, with the same `models.yml` and tool list as `../coding/run_omp.py`.
4. Hermes runs in `benchlocal-sandbox-hermes:latest` (entrypoint overridden). The runner writes `config.yaml` and a `request.json` for benchlocal's own `agent-runner.py` and calls it with the image's venv. Toolsets: `file`, `terminal`, `code_execution`. Web and browser tools are off. Defaults: 90 turns, 16384 max tokens per call, approvals auto-accepted.
5. After the agent exits (wall cap `--wall-s`, default 1200), `python3 -I check.py <workspace copy>` runs on the host. The `PASS: N FAIL: M` line gives `checks_passed`, `checks_total` and `partial`; a task is solved only on exit code 0.

Effort: `--effort` goes to omp as `--thinking` and to Hermes as `reasoning_effort` plus `chat_template_kwargs.enable_thinking: true` (drop that with `--no-thinking-kwarg` for servers that reject it). GLM's top rung is `max`, Qwen3.8's is `xhigh`; for omp pass the model's ladder with `--efforts`.

Output: `runs/<config>/<harness>/draw<N>/<task>/{result.json,agent.log,check.out,workspace_after/}` and `summary.json` per draw. `result.json` holds task, config, harness, draw, passed, checks_passed, checks_total, partial, agent_s, tool_calls, exit_status. Hermes also writes `final.txt` (its last message) and its raw run record (tool events, messages) as `agent.result.json`.

### Smoke tests (2026-10-11)

Model: ThinkingCap-27B (`thinkingcap38-27b`, SGLang :8173), effort low, task `23-recipe-scaling`.

| Harness | Result | Agent time | Tool calls | Window (EDT) |
|---|---|---|---|---|
| Hermes | PASS 10/10 | 10 s | 2 | 16:21:11 to 16:21:21, re-run 16:21:49 to 16:21:58 |
| omp | PASS 10/10 | 9.5 s | 2 | 16:21:39 to 16:21:49 |

Each is a few seconds of one short request beside whatever the eval chain was running on :8173, so flag any chain task overlapping those windows. A container started the same way cannot resolve `github.com` (curl and urllib both fail).

### Proposed run plan (not queued)

- Configs: Strata Flash Next UD-IQ4_XS, ThinkingCap-27B, optionally the better GLM config.
- Both harnesses, draws 1 to 3, `--effort low`, `--jobs 1`.
- Cost: the smoke task took 10 s, but the hard tasks (11, 14, 15, 19, 26) will run to the 20-minute cap in the worst case. Guess 3 to 6 minutes per task on average, so about 1.5 to 2.5 GPU hours per model, harness and draw. Two models, two harnesses, three draws is 12 sweeps, about 18 to 30 GPU hours serial. `--jobs 2` roughly halves wall time if the server has batch headroom. Run one draw of each first (about 6 to 10 hours), check for harness faults, then add draws.
- Start after the coding chains finish (about Tuesday 2026-10-13). Never run beside a measurement run.

## hard-v1: 12 tasks that separate models (27 to 38)

The first 26 tasks hit a ceiling: ThinkingCap solved 24/26 on both harnesses (both misses were bench bugs), usually in under a minute with about five tool calls. Each task was one transformation of
small, fully specified inputs. hard-v1 keeps the layout and the check contract and changes what is being tested: two tasks per axis, each a skill the first set never exercises.
Tasks 27 to 38 are `set: hard-v1` in `meta.json`, all `difficulty: hard`, with the extra field `axis`.

| Axis | Skill | Tasks |
|---|---|---|
| A | long inputs, paraphrased and superseded facts | `27-notes-current-state` (400 notes, 8 questions as of a date), `28-ledger-amendments` (3000 rows + 60 amendment emails) |
| B | long jobs with compounding state | `29-library-filing` (45 documents, collisions, supersession, 3 indexes), `30-room-booking-queue` (25 dependent requests) |
| C | conflicting or incomplete sources | `31-vendor-price-merge` (3 price lists, units, SKU normalisation), `32-event-plan-issues` (exact issue set, decoys) |
| D | recovering from errors | `33-flaky-fetch` (transient failures + one silent truncation), `34-messy-orders-rejects` (BOM, mixed dates, six rejects) |
| E | instructions planted in data | `35-inbox-planted-instructions`, `36-doc-summary-hidden-instruction` |
| F | changed requirements | `37-report-revised-request`, `38-trip-plan-revised` |

### New rules for these tasks

1. **Spec map.** `meta.json` has `spec_map`: every check name maps to a verbatim quote from `task.md`. `_build/validate.py` fails a task if a check printed by the reference run has no entry or the quote is not in `task.md`.
   For tasks 01 to 26 the same map exists only as a report: `spec-map-report-01-26.md` (heuristic) and `spec-map-review-01-26.md` (hand review: one real gap in 07, two borderline cases).
2. **Validation goes through the runner's copy**: the workspace is copied with `symlinks=True` into a temp dir, `reference/` is overlaid (honouring `_delete.txt`), then `check.py` runs. Nothing is validated in place.
3. **Naive solutions.** For axes A, C and E there is a `_build/naive/<id>/` overlay (what a one-liner or an obedient agent produces). `validate.py` requires it to fail at least one check. Axis B and D tasks rely on per-item checks instead.
   `notes` in `meta.json` says why the obvious solution is wrong.

### What the obvious solution gets wrong

| Task | Obvious solution | Why it fails |
|---|---|---|
| 27 | grep a keyword, take the first or last hit | files are not in date order; filler lines reuse the keywords; a temporary on-call swap is still active on the as-of date; a migration slipped, so the *old* host is current; budgets change by relative amounts. Naive (first mention) fails 7 of 8 questions |
| 28 | `groupby account` on `ledger.csv` | ignores the amendments: 12 of 12 balances wrong, no `ignored_emails.json`. Applying emails in file order, or trusting unapproved senders, breaks the set+move chains and the disregard emails |
| 29 | move files by type | slug rules, `-2` collisions in the inbox, four conflicts with the library (later date, then higher version), exact index formats. Per-file checks give partial credit |
| 30 | execute the requests as a script of commands | every request reads state left by the earlier ones; 12 of 25 are rejections with a defined precedence of reason codes |
| 31 | concat and compare raw prices | `ax-107`, `AX-107` and `AX107` are one SKU; Birch quotes per case; one SKU looks equal in raw numbers but differs per unit. Fails 7 checks |
| 32 | flag everything that looks odd | eight rule codes, five hold; decoys: standing capacity, `maybe` RSVPs, UTC and CET pairs that agree, a holiday list that misses the date. Fails 7 checks |
| 33 | trust exit codes | three items fail with exit 75, one returns half a body with exit 0; only the manifest hash catches it. `retried` has to name all four |
| 34 | skip bad rows | `rejects.csv` has to name each record and the first applicable reason |
| 35, 36 | do what the text says | check the outbox, the inbox hashes, `status.txt`, and canary strings in every written file. Obedient runs fail 3 to 5 checks |
| 37, 38 | build to the first message | the follow-up changes quarter, regions, ranking and hotel rating; look-alike and third-party senders are not the requester |

### Multi-turn is simulated

The runners send one prompt, so a changed requirement arrives as a later-dated message inside the workspace (37, 38). A true second turn needs runner support: after the first completion, send a scripted follow-up
message into the same session (omp with `--session`, or Hermes `--resume`), then score the final workspace. That changes `run_assistant.py` and the harness wrappers; it is not built.
Run a pilot with `python3 run_assistant.py ... --only 27,28,29,30,31,32,33,34,35,36,37,38`.
