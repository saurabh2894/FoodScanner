# Gate report: held-decisions-1

**Verdict: READY_FOR_REVIEW**

Nothing was merged.

| Check | Result |
|---|---|
| open demand terms decided | 6 |
| by disposition | {'PARK': 3, 'ACCEPT_ROW': 3} |
| paste-input mentions by disposition (a term can occur in several inputs) | {'PARK': 3, 'ACCEPT_ROW': 3} |
| candidate lexicon rows | 3 |
| candidate synonyms | 0 |
| flip check (66 frozen inputs, separate fresh processes) | group 0, drivers 0, status 0, reason 0, warnings 0, ingredients 0, unassessed 0, ins_mappings 0 |
| harness proof | lexicon rows 139 -> 142; synonym rows 0; all 3 terms recognised after |

## Candidate rows

- `banana powder` (food_powder) for demand term `banana powder`
- `strawberry powder` (food_powder) for demand term `strawberry powder`
- `beetroot powder` (food_powder) for demand term `beetroot powder`

## Marker proposals (classification-bearing: owner decision, not staged)


## Label-bound (conditioned clause, never staged)


## Parked

- #1 `sprouted ragi & jowar` (1 inputs): source_not_found: two grains joined by '&' (an extraction convention) and a sprouted form: no source read names sprouting or germination (FAO Table 1 and the Group 1 definition, Monteiro 2018 and 2019, NUPENS pages: 0 mentions); only the open clause 'other methods that do not add salt, sugar, oils or fats or other food substances' could cover it, which is an inference; recognition-only needs the unplaced kind (owner decision)
- #2 `rice & oat` (1 inputs): extraction_not_vocabulary: two recognised foods joined by '&' inside a bracket and kept as one item: an extraction convention, not a vocabulary gap
- #5 `vitamins and minerals` (1 inputs): fortification_purpose: FAO Table 1 Group 1: 'foods with vitamins and minerals added generally to replace nutrients lost during processing' is purpose-conditioned and Group 4 lists 'powdered or fortified meal and dish substitutes'; the label cannot show the purpose, so it stays unplaced and the list abstains; recognition-only needs the unplaced kind (owner decision)
