# Schedule a chain of jobs on two GPUs

`/workspace/jobs.json` lists jobs with `duration_min`, `gpus` (0, 1 or 2 of the 2 GPUs the job holds while it runs), `after` (jobs that must have **finished** before it starts)
and `not_before_min` (it may not start earlier than this minute). Time starts at minute 0. Jobs cannot be interrupted. Several jobs may run at once as long as their `gpus` sum to at most 2 at every moment.

Write `/workspace/schedule.json`: a JSON object mapping every job name to its integer start minute. The schedule must be valid and its makespan
(latest finish minus 0) must be the **smallest possible**.
