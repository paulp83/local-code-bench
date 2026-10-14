# Archive naming contract

Result docs live in `archive/results/`. File name: `<YYYY-MM-DD>_<slug>_<kind>.md`.

- `<YYYY-MM-DD>`: the doc's `date` front-matter field.
- `<slug>`: the `model` field and the `quant` field joined with `-`, lowercased, every `.` and `_` and space replaced with `-`.
- `<kind>`: the `type` field (`rig`, `quality` or `bench`).

`archive/INDEX.md` has one `## YYYY-MM` section per month, newest month last. Each section holds a table
`| date | slug | kind | file | verdict |`. Rows are sorted by date ascending (ties: keep existing order, new row after).
The `verdict` cell is the text after `Verdict:` on the doc's Verdict line.
