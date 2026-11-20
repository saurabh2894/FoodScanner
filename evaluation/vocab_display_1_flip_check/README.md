# Vocabulary and Display Data Expansion 1: Flip-Check on the Existing Frozen Paste Inputs

## Summary of Changes
1. **Package 1 (`synonyms.csv`)**:
   - `iodized salt` -> `iodised salt` (US spelling variant seen on labels F07, M15, N12, Q14)
   - `cotton seed oil` -> `cottonseed oil` (open-compound spelling seen on label F15)
   - `refined palmolein oil` -> `palmolein` (variant phrasing seen on labels F09, N05, R2)
   - Note: `lodised salt` / `lodized salt` dropped because resolving the OCR typo flips Katraj buttermilk Q03 (`Water, Curd, lodised Salt CONTAINS MILK`) from an unrecognised-ingredient abstention to answered Group 3. Under the strict freeze condition that no existing input may flip group, typo-normalisation for `lodised` is held back. `com meal` -> `corn meal` blocked because no base `corn meal` row exists in `lexicon.csv`.
2. **Package 2 (`ins_names.csv`)**:
   - Added display names for 12 INS codes: 202, 260, 339(ii), 407, 412, 415, 466, 476, 500(i), 501(i), 551, 1422.
   - Sourced directly from online JECFA specification monographs published by FAO (Monographs 1, 5, 11, 16, 20). No Codex tables or republished Codex data used.
3. **Package 3 (`declared_roles.csv`)**:
   - Added `sequestrant`, `dough conditioner`, and compound role `thickening & stabilizing agents`.
   - Verified against FAO 2019 (Monteiro et al., `ca5644en.pdf`), marked `not_named`. Truncated label text `PAST STABILIZER` (R1) blocked.
4. **Package 4 (`lexicon.csv`)**:
   - Audited against FAO 2019 Table 1 Group 1 (p. 11). Unbacked terms, group phrases without single-ingredient methods, and processed-form candidates (pulps, flakes, purees) dropped for lack of definitive NOVA Group 1 settling citations.

## Evaluation Inputs
The 66 untouched pasted inputs across 5 frozen evaluation batches:
- `fresh_batch_1`: 16 inputs
- `fresh_batch_2`: 15 inputs
- `fresh_batch_3`: 14 inputs
- `negation_addendum`: 6 inputs
- `dev_regression_15`: 15 inputs

Baseline: commit `8a4e2e7` (origin/main).

## Results
- **Changed counts**:
  - `group`: **0 of 66 changed**
  - `drivers`: **0 of 66 changed**
  - `status`: **0 of 66 changed**
  - `reason`: **0 of 66 changed**
  - `warnings`: **0 of 66 changed**

Zero inputs changed classification, driver lists, completeness status, or reason/warning text. 22 inputs were enriched with additive display metadata (JECFA names and declared roles) with zero classification effects.

## Generalization Disclaimer
These 66 inputs are frozen historical evaluation artifacts. Zero flips across this suite proves non-regression on known test vectors, but cannot prove generalization across the full distribution of unseen Indian packaged-food labels.
