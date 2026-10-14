# Diff two versions of a policy

`/workspace/policy-v1.md` and `/workspace/policy-v2.md` are two versions. Each clause is a `### <id> <Title>` heading followed by its text. A clause's identity is its **title** (titles are unique within a version).

Write `/workspace/changes.json`:

- `added`: ids (as in v2) of clauses whose title is only in v2.
- `removed`: ids (as in v1) of clauses whose title is only in v1.
- `changed`: ids (as in v2) of clauses with the same title in both versions whose text differs.
- `renumbered`: objects `{"title": ..., "from": <v1 id>, "to": <v2 id>}` for clauses with the same title whose id differs. A clause may be both `changed` and `renumbered`.

All four keys must be present; each list is sorted by the id (for `renumbered`, by `from`).
