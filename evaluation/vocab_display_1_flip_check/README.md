# Vocabulary and Display Data Expansion 1: Flip-Check on Frozen Paste Inputs

## Summary of Changes
1. **Package 1 (`synonyms.csv`)**:
   - `iodized salt` -> `iodised salt` (US spelling variant seen on labels F07, M15, N12, Q14)
   - `cotton seed oil` -> `cottonseed oil` (open-compound spelling seen on label F15)
   - `refined palmolein oil` -> `palmolein` (variant phrasing seen on labels F09, N05, R2)
   - `lodised salt` -> `iodised salt` (Indian OCR variant with capital I read as lowercase l; seen on F08, F10, F13, M07, N04, N15, Q03)
   - `lodized salt` -> `iodised salt` (Indian OCR variant lowercase l + US spelling z; seen on F02, M10, R2)

2. **Package 2 (`ins_names.csv`)**:
   - Added display names for 12 INS codes: 202, 260, 339(ii), 407, 412, 415, 466, 476, 500(i), 501(i), 551, 1422.
   - Sourced directly from online JECFA specification monographs published by FAO (Monographs 1, 5, 11, 16, 20). No Codex tables or republished Codex data used. Cleaned display names with single spacing (e.g. "Silicon Dioxide, Amorphous" without double space, "Acetylated Distarch Adipate" without tentative suffix).

3. **Package 3 (`declared_roles.csv`)**:
   - Added `sequestrant` and `dough conditioner`. (Removed compound role `thickening & stabilizing agents`).
   - Verified against FAO 2019 (Monteiro et al., `ca5644en.pdf`), marked `not_named`. Clarified source note for `dough conditioner` (not a standalone role on M09 due to "malt extract and", but covers the pure role phrase when declared).

4. **Package 4 (`lexicon.csv`)**:
   - Zero modifications. Candidate additions held back.

## Evaluation Inputs
The 66 untouched pasted inputs across 5 frozen evaluation batches:
- `fresh_batch_1`: 16 inputs
- `fresh_batch_2`: 15 inputs
- `fresh_batch_3`: 14 inputs
- `negation_addendum`: 6 inputs
- `dev_regression_15`: 15 inputs

True baseline: commit `8a4e2e7` (origin/main), evaluated in a separate git worktree and process to eliminate caching or shared state.

## Results & Itemised Diff Attribution
- **Changed counts**:
  - `group`: **1 of 66 changed** (`b3/Q03` None -> 3)
  - `drivers`: **1 of 66 changed** (`b3/Q03` `[]` -> `['recognised whole food', 'recognised culinary']`)
  - `status`: **0 of 66 changed**
  - `reason`: **3 of 66 changed** (`b3/Q03`, `neg/R2`, `dev/F09`)
  - `warnings`: **0 of 66 changed**
  - `ingredients`: **0 of 66 changed**
  - `unassessed`: **17 of 66 changed**
  - `additive_display`: **22 of 66 changed**

### Detailed Field Attributions
1. **NOVA-Group & Driver Flip (`b3/Q03`)**:
   - `b3/Q03` (Katraj buttermilk: `Water, Curd, lodised Salt CONTAINS MILK`) flipped from `None` (unrecognised ingredient abstention) to `3` (processed food).
   - Drivers changed from `[]` to `['recognised whole food', 'recognised culinary']`.
   - Reason changed from unrecognised ingredient text to `None`.
   - Responsible change: Package 1 alias `lodised salt` -> `iodised salt`. This flip is expected and correct: Katraj buttermilk is Curd, Water, and culinary salt, properly classified as NOVA 3 once the OCR typo is mapped.
2. **Reason-Text Changes (`neg/R2`, `dev/F09`)**:
   - `neg/R2`: Reason text dropped `lodized salt` from the unrecognised ingredient list (due to Package 1 `lodized salt` -> `iodised salt`).
   - `dev/F09`: Reason text dropped `Refined Palmolein Oil` from the unrecognised ingredient list (leaving only `Ajwain`, due to Package 1 `refined palmolein oil` -> `palmolein`).
3. **Unassessed-List Changes (17 inputs)**:
   - 17 labels dropped newly recognised synonyms (`lodised salt`, `lodized salt`, `iodized salt`, `cotton seed oil`, `refined palmolein oil`) from their unassessed ingredient lists: `b1/N04`, `b1/N05`, `b1/N12`, `b1/N15`, `b2/M07`, `b2/M10`, `b2/M15`, `b3/Q03`, `b3/Q14`, `neg/R2`, `dev/F02`, `dev/F07`, `dev/F08`, `dev/F09`, `dev/F10`, `dev/F13`, `dev/F15`.
   - Responsible change: Package 1 synonym aliases.
4. **Display-Only Enrichments (22 inputs)**:
   - 22 labels had JECFA display names and/or declared role `sequestrant` populated in `ins_mappings`: `b1/N05`, `b1/N06`, `b1/N11`, `b1/N12`, `b1/N13`, `b2/M04`, `b2/M05`, `b2/M10`, `b2/M11`, `b2/M12`, `b2/M14`, `b2/M15`, `b3/Q11`, `b3/Q12`, `b3/Q14`, `neg/R5`, `dev/F06`, `dev/F07`, `dev/F08`, `dev/F13`, `dev/F14`, `dev/F15`.
   - Responsible change: Package 2 `ins_names.csv` and Package 3 `declared_roles.csv`. Purely additive display text with zero impact on NOVA classification or rules.

## Generalization Disclaimer
These 66 inputs are an evidence sample from historical frozen evaluation batches, not an assertion that no other label in the world flips. While zero unintended flips occurred across this sample and the single Q03 flip is intentional and verified, this test suite cannot guarantee identical classification outcomes across the infinite distribution of unseen packaged-food labels.
