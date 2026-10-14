# Pair rig reports with quality results

`/workspace/rig/` has rig reports named `<date>_<slug>_run<N>.json`. `/workspace/quality/` has quality results named `q-<date>-<slug-as-written>.json`;
their slug may be a short alias, and `/workspace/aliases.json` maps aliases to the canonical slug (a slug with no alias entry is already canonical).

A quality result pairs with the rig report that has the same date and canonical slug. If several runs share a date and slug, only the highest run number counts;
the lower runs are *superseded*.

Write, all in `/workspace`:

1. `pairs.csv` with header `slug,date,rig_file,quality_file` (file names without directory), one row per pair, sorted by slug then date. `slug` is canonical.
2. `superseded.txt`: file names of superseded rig reports, one per line, sorted.
3. `unpaired_rig.txt`: rig report file names that are neither paired nor superseded, one per line, sorted.
4. `unpaired_quality.txt`: quality file names with no pair, one per line, sorted.

Empty lists mean an empty file. Date must match exactly (no nearest-date matching).
