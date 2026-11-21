# Gate report: tier1-demand-bulk-1

**Verdict: READY_FOR_REVIEW**

Nothing was merged. `lexicon_candidate_rows.csv` holds the ready rows in lexicon.csv layout and `synonyms_candidate_rows.csv` the synonym candidates in synonyms.csv layout, for review.

| Check | Result |
|---|---|
| staged rows | 2 |
| schema errors | 0 |
| provenance errors | 0 |
| duplicates (exact, synonym, already recognised) | 0 |
| variants of an existing term (informational) | 0 |
| parked in the ambiguity queue | 0 (Counter()) |
| ready rows (new lexicon rows) | 2 |
| synonym candidates (variant policy None) | 0 |
| policy errors | 0 |
| verbatim clause vs FAO text | NOT CHECKED (no --fao-text) |
| harness proof (separate processes) | lexicon rows 135 -> 137; all 2 staged terms recognised after; 0 already recognised before |
| flip check (66 frozen inputs, before and after in separate fresh processes) | group 0, drivers 0, status 0, reason 0, warnings 0, ingredients 0, unassessed 1, ins_mappings 0 |
| group/status/driver flips | 0  |
| unexplained changes | 0 |

## Ready rows (new lexicon rows)

- `beans`
- `cabbage`

## Synonym candidates (variant policy: same ingredient, plant part and form)


## Duplicates (excluded: already covered)


## Variants of existing terms (kept; informational)


## Ambiguity queue (parked, never included)


## Unassessed drops attributed to ready rows

- dev/F07: ['beans (9.5%)', 'cabbage (3.8%)'] -> rows ['beans', 'cabbage']
