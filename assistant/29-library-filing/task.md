# File 45 documents into the library

`/workspace/inbox/` holds 45 documents, each with a front matter block (`title`, `type`, `date`, `author`, `version`). `/workspace/library/` is the archive, with three index files:
`INDEX-by-area.md`, `INDEX-by-date.md`, `INDEX-by-author.md`. File every inbox document and bring the indexes up to date.

**Path.** `library/<area>/<year>/<slug>.md`, content unchanged.
- `area` from `type`: `rig-report` -> `reports/rig`, `quality-result` -> `reports/quality`, `plan` -> `planning`, `handoff` -> `handoffs`, `minutes` -> `meetings`, any other type -> `misc`.
- `year`: the first four characters of `date`.
- `slug` from `title`: lowercase, every run of characters other than `a-z0-9` becomes one `-`, strip leading and trailing `-`, cut to 40 characters, then strip a trailing `-` again.

**Collisions inside the inbox.** If several inbox documents get the same `<area>/<year>/<slug>`, the one with the earliest `date` (ties: lower inbox file name) keeps the plain slug, and the next ones get `-2`, `-3`, ... appended to the slug, in date order.

**Conflicts with the library.** If the final path already exists in `library/`, the document with the later `date` stays at that path; on equal dates the higher `version` stays; if both are equal the existing one stays.
The loser is moved to `library/_superseded/<area>/<year>/<slug>--v<version>.md` (its own area, year, slug and version, content unchanged). Superseded documents are not in the indexes.

**Indexes.** Rebuild all three so they list exactly the live documents, using exactly these formats (every file ends with a newline, no other text):
- `INDEX-by-area.md`: `# Index by area`, then for each area in alphabetical order a blank line, `## <area>`, a blank line, the table header `| date | slug | title |`, `|---|---|---|`, and one row `| <date> | <slug> | <title> |` per document sorted by date then slug.
- `INDEX-by-date.md`: `# Index by date`, a blank line, `| date | area | slug |`, `|---|---|---|`, and one row per document, sorted by date descending then slug descending.
- `INDEX-by-author.md`: `# Index by author`, then for each author in alphabetical order a blank line, `## <author>`, a blank line, and one line `- <date> <area>/<year>/<slug>` per document sorted by date then slug.
The `slug` in an index is the final slug (with any `-2` suffix). The inbox must end up empty.
