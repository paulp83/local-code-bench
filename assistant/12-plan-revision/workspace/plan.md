# Plan

Contents:
1. Prepare the rig
2. Fetch weights
3. Convert legacy format
4. Quantize
5. Bench
6. Verify quality
7. Write results
8. Cleanup

### Step 1: Prepare the rig
- Stop the dev server.
- Confirm both GPUs are idle.
- (see Step 8) for the stop procedure.

### Step 2: Fetch weights
- Download the checkpoint.
- AC-2.1: checksums match the manifest

### Step 3: Convert legacy format
- Run the converter.
- AC-3.1: converted files load
- Skipped when 4 uses the new format.

### Step 4: Quantize
- Run the fp8 recipe.
- Needs the output of Step 2.
- AC-4.1: fp8 files exist

### Step 5: Bench
- Run the 5-run bench.
- AC-5.1: median decode recorded in out/bench.json

### Step 6: Verify quality
- Run the quality gate.
- Compare against the Step 5 numbers.
- AC-6.1: score within 1 point of baseline

### Step 7: Write results
- Fill the results template.
- Cite the Step 5 numbers and the Step 6 score.

### Step 8: Cleanup
- Remove temp files.
- Restart the dev server.
