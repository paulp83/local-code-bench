# Handoff

## Done
- T1 fetch weights
- T2 write quant recipe

## In progress
- T4 bench two configs: tp2-fp8 finished (out/bench-fp8.json), tp2-awq not started.

## Blockers
- T3 run quality gate: `bash scripts/run_quality.sh --slug glm53 --port 8000` exits 3, port 8000 already in use by pid 4411.

## Next
- Free port 8000, then rerun the quality gate.
- Run `scripts/run_bench.sh` for tp2-awq.
- T5 and T6 wait on the above.
