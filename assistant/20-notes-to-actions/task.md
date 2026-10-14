# Turn meeting notes into actions

`/workspace/notes.md` are notes from a meeting held on **Wednesday 2026-10-07** (that is "today"). Write `/workspace/actions.json`: a JSON array, in note order, of
`{"owner": <first name>, "task": <text>, "due": "YYYY-MM-DD"}`, one per line that assigns a named person a task with a deadline (`<Name> to ...` or `<Name> will ...`).

- `task` is the text between `to`/`will` and the deadline phrase, e.g. `send the vendor quote`.
- Deadline phrases: `tomorrow` = 2026-10-08; `by <weekday>` = the next such weekday strictly after today; `next <weekday>` = that weekday in the **following** calendar week (weeks run Monday to Sunday);
  `in N weeks` = today + 7N days; `by end of month` = the last day of the month; `on <date>` = that date.
- Ignore decisions, FYIs, ideas, and lines with no owner.
