# Hand review of the flagged checks in tasks 01-26

Report only: tasks 01-26 were not changed. `spec-map-report-01-26.md` is the heuristic output (best matching `task.md` line per check, 67 flagged with overlap below 0.5).
Most flags are not gaps. The heuristic matches check names against `task.md` text, and per-row checks (`row-<config>`, `section-<step>`, `row-<n>`) name data values that the
task text deliberately leaves to the data, while the *rule* that decides them is written in `task.md` (for example "Use the corrected value where the report corrects one").

## Checks that trace to a stated rule (flag is a naming artefact)

All `row-*`, `section-*`, `ids-*`, `headings-match`, `four-rows`, `header`, `email`, `degree-BSc`, `parses`, `file-named-correctly`, `old-rows-kept`, `manifest-exact`, `hot-dir-gone`,
`dependencies-respected`, `gpu-capacity-never-exceeded`, `schedule-complete-ints`, `photos-dir-empty`, `sidecars-moved`, `starts-with-mention`, `max-150-words`, `no-dashes`, `no-exclamation`,
`no-banned-phrases`, `A1..A4-*`, `is-list-of-expected-length`, `ids-complete-sorted`, `no-stale-refs`, `all-cells-correct`, `index-matches-expected`.
Each is a direct consequence of a sentence in the task (format, order, a stated rule, or the data the rule is applied to).

## Checks that test something `task.md` does not state

| Task | Check | Gap | Verdict |
|---|---|---|---|
| 01 | `buckets-at-least-14-correct` | partial-credit threshold, not a requirement | by design (extra gradient); harmless, `buckets-all-correct` carries the requirement |
| 07 | `no-wrong-values` | fails a reply that mentions another row's number (84.9, 51.6, 98304, 32768, 29.7, 27.3) | **real gap**: `task.md` says "answer ... with the exact values from the CSV", not "mention no other values". A reply that adds context about another config fails. Fix by stating it, or drop the check |
| 11 | `makespan-within-10-percent` | gradient check | by design; `makespan-optimal` carries the requirement |
| 13 | `column-*-at-least-27` | gradient checks | by design |
| 19 | `at-least-90pct-cells` | gradient check | by design |
| 25 | `only-expected-lines-changed` | compares the first nine non-blank lines to the reference, so an edit that drops the inline comment `; inline note stays` on the port line fails | borderline: `task.md` says everything else "must stay exactly as it is", which covers it, but a stricter sentence ("keep inline comments") would remove doubt |
| 12 | `no-stale-refs` | fails if the word `legacy` appears anywhere | borderline: implied by "delete the step ... remove any line in another step that only refers to it", but a legitimate sentence containing `legacy` would fail |

Everything else maps. Recommendation: fix 07's `no-wrong-values` text before a re-run, and consider a sentence for 25. Both are small edits to `task.md`, and the existing results stay comparable if the change only states what the check already tests.
