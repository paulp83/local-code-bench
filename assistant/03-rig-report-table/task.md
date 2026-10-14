# Summarise the rig report as a table

`/workspace/rig-report.md` has one section per config plus a corrections section.

Write `/workspace/summary.md` containing a markdown table with exactly this header row:

`| config | decode_tps | prefill_tps | peak_vram_gib |`

One row per config, in the order the report lists them, config names without backticks. Rules:

- Use the corrected value where the report corrects one.
- `decode_tps`: one decimal place. `prefill_tps`: integer, no thousands separators.
- `peak_vram_gib`: GiB with one decimal place (1 GiB = 1024 MiB; round half up on the exact value).
- A config with no numbers gets `n/a` in all three value columns.
