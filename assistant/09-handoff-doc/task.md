# Write a handoff for the next session

`/workspace/tasks.json`, `/workspace/progress.md`, `/workspace/last-run.log` and `/workspace/tree.txt` describe where a multi-step job stands.
Write `/workspace/HANDOFF.md` for someone who starts cold. Use exactly these four `##` headings, in this order: `Done`, `In progress`, `Blockers`, `Next`.

- Every task goes under the heading that matches its status (`done` -> Done, `in_progress` -> In progress, `blocked` -> Blockers; `todo` tasks are mentioned only under Next). Refer to tasks by id (`T1`).
- Blockers must quote the exact failing command from the log in backticks and the exit status number.
- In progress must say which config finished and which has not started.
- Next must name the script path to run for the unfinished bench.
- At most 250 words in total.
