# Pick a tool for a request, or abstain

`plexus pick` reads a plain-language request and returns a probability for each tool in the mesh, scored against what each tool's manifest says it emits and consumes. When no tool matches, or the top probability is under a threshold, it abstains, so the request goes to a person or a larger model in place of a guessed tool. `plexus route` still answers the wiring question, how one tool's output reaches another.

## Bar, set before the run

This bar was committed before the picker was written and before its author saw the labelled set.

**Labels.** 100 requests written by a separate labeller who saw only tool names, their capability titles and a one-line purpose, never code, each with one gold tool (`tests/fixtures/plexus_pick_labels.json`). The local routing-accuracy records hold 2 records, too few to use.

**Split.** Items are split in half by a seeded hash of their id. The threshold is chosen on the dev half only: the lowest threshold whose dev abstain rate is at least 10%. All bar numbers come from the test half.

**Baseline.** Plexus had no request picker. The baseline is the majority tool on the dev half, always picked.

- **P1, accuracy.** Top-1 accuracy is at least the baseline's plus 0.20.
- **P2, abstain rate.** Under 15% of test items abstain.
- **P3, abstain carries error.** The top-1 error rate on abstained items is at least twice the error rate on decided items.
- **Control.** With the gold labels shuffled, P3 must fail.
- **Ship rule.** The picker ships as a new command whatever the result, with the numbers below.

## Results

Pending the run.
