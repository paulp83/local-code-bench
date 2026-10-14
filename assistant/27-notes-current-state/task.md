# Answer eight questions about the team's current state

`/workspace/notes/` holds 400 meeting notes from 2026-04-01 to 2026-09-30, one per file. The file names carry no date order: each note's date is its `date:` line.
Answer as of **2026-09-30**.

How to read the notes:
- A later-dated note overrides an earlier one on the same fact. Relative changes ("raised by 12000", "pushed back one week") apply to the value in force on that date.
- Only decisions count. Ideas, evaluations and "no decision" remarks change nothing.
- A change with an end date stops applying after it; a change with a future effective date does not apply yet.
- Contractors are not headcount. Everyone else on a team roster counts, including people on leave.

Write `/workspace/answers.json` with these keys:

- `q1`: Platform standup weekday, full English name (e.g. `Monday`).
- `q2`: full name of the person holding on-call on 2026-09-30.
- `q3`: current budget in USD (integer) of the team that Marta Voss leads.
- `q4`: which staging host is in use on 2026-09-30, as a single word.
- `q5`: number of people on the Web team (integer).
- `q6`: date of the team offsite, `YYYY-MM-DD`.
- `q7`: sum of the current budgets of Platform, Data and Web, integer USD.
- `q8`: the team (`Platform`, `Data` or `Web`) Joel Ames is on.
