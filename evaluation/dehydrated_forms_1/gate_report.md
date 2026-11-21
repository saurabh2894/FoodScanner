# Gate report: dehydrated-policy-1

**Verdict: READY_FOR_REVIEW**

Nothing was merged. `synonyms_candidate_rows.csv` is in synonyms.csv layout.

| Check | Result |
|---|---|
| candidate synonyms | 3 |
| dropped (already covered) | 0 |
| terms probed before/after for drift (all lexicon terms and synonyms) | 303 |
| negative controls (identity, or unrecognised for processed forms) | 11 checked, 0 failing |
| flip check (66 frozen inputs, separate fresh processes) | group 0, drivers 0, status 0, reason 0, warnings 0, ingredients 0, unassessed 2, ins_mappings 0 |
| harness proof | synonym rows 3; all 3 terms recognised after; 0 before |

## Candidate synonyms

- `dehydrated onion` -> `onion` (dehydrated-term)
- `onions flakes` -> `onion` (flakes-term)
- `onion flakes` -> `onion` (flakes-term)

## Dropped


## Negative controls (must stay exactly as before the batch)

- `dehydrated vegetable`: before {'name': 'dehydrated vegetable', 'recognised': False} / after {'name': 'dehydrated vegetable', 'recognised': False}
- `dehydrated vegetables`: before {'name': 'dehydrated vegetables', 'recognised': False} / after {'name': 'dehydrated vegetables', 'recognised': False}
- `dehydrated potato flakes`: before {'name': 'dehydrated potato flakes', 'recognised': False} / after {'name': 'dehydrated potato flakes', 'recognised': False}
- `dehydrated garlic`: before {'name': 'dehydrated garlic', 'recognised': False} / after {'name': 'dehydrated garlic', 'recognised': False}
- `dehydrated milk`: before {'name': 'dehydrated milk', 'recognised': False} / after {'name': 'dehydrated milk', 'recognised': False}
- `dehydrated mango`: before {'name': 'dehydrated mango', 'recognised': False} / after {'name': 'dehydrated mango', 'recognised': False}
- `corn flakes`: before {'name': 'corn flakes', 'recognised': False} / after {'name': 'corn flakes', 'recognised': False}
- `rice flakes`: before {'name': 'rice flakes', 'recognised': False} / after {'name': 'rice flakes', 'recognised': False}
- `chilli flakes`: before {'name': 'chilli flakes', 'recognised': True} / after {'name': 'chilli flakes', 'recognised': True}
- `fried onion flakes`: before {'name': 'fried onion flakes', 'recognised': False} / after {'name': 'fried onion', 'recognised': False}
- `fried dehydrated onion`: before {'name': 'fried dehydrated onion', 'recognised': False} / after {'name': 'fried onion', 'recognised': False}
