# Flip check: demand_bulk_1

Harness: scripts/flip_dump.py executed across all 66 frozen paste inputs in separate fresh processes.
- Before: repo baseline (origin/main at d1bc5d5, 135 lexicon rows).
- After: repo baseline + 2 ready rows ('beans', 'cabbage' kind=whole_food, 137 lexicon rows).

## Results
- Total frozen inputs: 66
- group changes: 0
- status changes: 0
- drivers changes: 0
- reason changes: 0
- warnings changes: 0
- ingredients changes: 0
- ins_mappings changes: 0
- unassessed changes: 1 (dev/F07)

## Attributed Changes
- Input `dev/F07`:
  - unassessed before: includes `beans (9.5%)` and `cabbage (3.8%)`
  - unassessed after: `beans (9.5%)` and `cabbage (3.8%)` recognized as `whole_food` and removed from unassessed
  - group before: 4; group after: 4 (unchanged; driven by cosmetic additives and processed ingredients)
  - drivers before/after: unchanged

Flips: 0. Unexplained changes: 0.
