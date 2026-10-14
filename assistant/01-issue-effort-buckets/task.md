# Bucket the open issues by effort

`/workspace/issues/` holds one JSON file per open issue: `number`, `title`, `labels`, `files_touched` (estimated),
`has_repro` (bool), `needs_gpu` (bool).

Give every issue an effort score:

- +2 if `files_touched` is greater than 3
- +1 if `has_repro` is false
- +2 if `needs_gpu` is true
- +2 if the labels include `design`
- -2 if the labels include `good first issue`

Bucket: score <= 0 is `small`, 1 to 2 is `medium`, 3 or more is `large`.

Deliverables:

1. `/workspace/buckets.json`: a JSON object mapping each issue number (as a string key) to its bucket string.
2. `/workspace/junior.json`: a JSON array of the issue numbers (integers, ascending) that are `small` and do not need a GPU.
