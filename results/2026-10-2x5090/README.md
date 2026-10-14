# club-tasks results: task lists and per-task runs

Rig: 2× RTX 5090, TR PRO 3975WX, 256 GB RAM. Runs from 2026-10-10 to 2026-10-14.

| File | Rows | What it is |
|---|---|---|
| `coding-tasks.csv` | 20 | the coding tasks: club-3090 PRs merged after 2026-08-26, with the hidden test each one is graded by |
| `coding-results.csv` | 400 | one row per task × config × draw |
| `assistant-tasks.csv` | 38 | the non-coding tasks: 26 base, 12 hard-v1 (axis A long inputs, B long jobs with state, C conflicting sources, D error recovery, E instructions planted in the data, F changed requirements) |
| `assistant-results.csv` | 152 | one row per task × model × harness |

## Columns

**coding-results.csv**
- `harness`: `mini-swe-agent` (bash only, SWE-bench prompts) or `omp` v18.6.0.
- `effort`: `low`, or the model's top rung (`xhigh` for the Qwen3.8 models, `max` for GLM-5.3-Flash).
- `task_text`: `final` for every scored run. `original` rows are the 8 tasks whose first text left out something the hidden test checks, run before they got an `## Interface` section. They're kept for comparison and aren't in the post's totals.
- `solved`: 1 if the PR's hidden tests pass on the agent's working tree.
- `partial`: the hidden test's checks, scaled so the code before the PR = 0 and the PR = 1.
- `right_files`: share of the files the agent edited that the PR also edited.
- `regressions`: nearby existing tests that broke.
- `minutes`, `steps`: agent wall time and tool calls. Limits: 60 minutes and 100 steps (`TimeExceeded`, `LimitsExceeded`; `omp-rc-1` is omp's own time-out).

**assistant-results.csv**
- `harness`: `hermes` or `omp`. Effort low throughout.
- `checks_passed` / `checks_total`: deterministic checks on the files the agent left; `solved` = all passed.

## Notes

- Two omp cells at the top rung (Flash Next and GLM, `omp` + `xhigh`/`max`) come from the first omp pass. That pass sent no `reasoning_effort`, so those servers fell back to their defaults: xhigh for Qwen3.8 and max for GLM. Later omp runs send the effort explicitly.
- Assistant tasks 02 and 05 were fixed after the first runs: 02's text gained a rule its check already tested, and the runner's workspace copy now keeps symlinks. The rows here are the re-runs on the fixed tasks.
- Strata IQ4_XS draw 1 overlapped a duplicate copy of itself for a while, so its draw-1 minutes run high.
