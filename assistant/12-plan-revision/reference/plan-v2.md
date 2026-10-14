# Plan

Contents:
1. Prepare the rig
2. Fetch weights
3. Warm-up run
4. Quantize
5. Bench and verify
6. Write results
7. Teardown

### Step 1: Prepare the rig
- Stop the dev server.
- Confirm both GPUs are idle.
- (see Step 7) for the stop procedure.

### Step 2: Fetch weights
- Download the checkpoint.
- AC-2.1: checksums match the manifest

### Step 3: Warm-up run
- Run one throwaway request.
- Discard its timing.
- AC-3.1: server answers 200 on /health

### Step 4: Quantize
- Run the fp8 recipe.
- Needs the output of Step 2.
- AC-4.1: fp8 files exist

### Step 5: Bench and verify
- Run the 5-run bench.
- Run the quality gate.
- AC-5.1: median decode recorded in out/bench.json
- AC-5.2: score within 1 point of baseline

### Step 6: Write results
- Fill the results template.
- Cite the Step 5 numbers and the Step 5 score.

### Step 7: Teardown
- Remove temp files.
- Restart the dev server.
