# Turn a job-chain log into a status table

`/workspace/chain.log` is the log of a chain of stages. Write `/workspace/status.csv` with the header
`stage,attempts,start,end,result,duration_s` and one row per stage, ordered by the first log line that names the stage.

- `attempts`: how many times the stage started (a retry counts); 0 if it never started.
- `start`, `end`: timestamps exactly as logged, of the **last** attempt's `start` line and its `done` or `FAILED` line. Empty if the stage never started.
- `result`: `ok` if the last attempt logged `done`, `failed` if it logged `FAILED`, `skipped` if the stage was skipped.
- `duration_s`: whole seconds from `start` to `end`; empty for skipped stages.
- Lines that are not stage events (for example GPU memory lines) are noise.
