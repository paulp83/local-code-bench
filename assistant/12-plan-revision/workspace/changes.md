# Requested changes

1. Delete the step "Convert legacy format" entirely. Remove any line in another step that only refers to it.
2. Insert a new step "Warm-up run" right after "Fetch weights", with exactly these lines:
   - Run one throwaway request.
   - Discard its timing.
   - AC-<step>.1: server answers 200 on /health
3. Merge "Bench" and "Verify quality" into one step titled "Bench and verify": its lines are the instruction lines of Bench, then the instruction lines of Verify quality
   (drop the "Compare against ..." line, it no longer applies), then all acceptance criteria in their original order, renumbered.
4. Rename "Cleanup" to "Teardown".
5. Renumber every step, the Contents list, every `AC-<step>.<n>` id, and every "Step <number>" reference so everything is consistent. A reference to a merged step points at the merged step.
