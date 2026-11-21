# INS Extension Evidence Table (ins_extension_1)

## Context & Purpose
Foodscan determines NOVA groups from Indian ingredient labels. Currently, 14 INS additive codes have active decision rules on `main`, while display-only entries are mapped without group effects. To support senior engineering review and potential rule extensions without conflating classification policy with evidence gathering, this table provides naming and verbatim-quoted functional class evidence from the single admissible international authority: **WHO IPCS INCHEM (JECFA Evaluations)**.

This task gathers evidence only. It makes **zero classification verdicts**, assigns **no NOVA groups**, and applies **no UPF/marker status**.

## Base Commit
- **Branch**: `antigravity/ins-extension-1`
- **Base SHA (origin/main)**: `9feadd8e16f6f8b34eec8ead7e321d21bade95f3`

## Methodology & Admissible Source
1. **Admissible Source**:
   - Every entry is cited directly from static WHO IPCS INCHEM evaluation pages: `https://www.inchem.org/documents/jecfa/jeceval/jec_NNNN.htm`.
   - INCHEM is the peer-reviewed repository of Joint FAO/WHO Expert Committee on Food Additives (JECFA) monographs and evaluations.
   - Each row quotes the verbatim `Functional class:` line and the official additive name from the evaluation page opened.
2. **Neutral Attribution**:
   - Additives with multiple functional classes separated by semicolons are marked `multifunctional: yes`.
   - Additives with a single class are marked `multifunctional: no`.
   - No classification or technological verdict is rendered.
3. **Bounded Search & Evidence Missing Protocol**:
   - If a code appearing in label text cannot be resolved to an INCHEM JECFA evaluation page after search, it is assigned `evidence_status: EVIDENCE-MISSING` with empty URL and functional class fields, rather than substituting forbidden sources or recalled knowledge.

## Scope & Exclusions
The following 30 codes were excluded prior to candidate selection:
- **14 Ruled Codes on main**:
  `102`, `110`, `150d`, `171`, `211`, `322`, `440`, `452(i)`, `471`, `500(ii)`, `503(ii)`, `627`, `631`, `950`
- **16 Display Codes Audited in `evaluation/ins_audit_1/audit.csv`**:
  `202`, `260`, `296`, `330`, `334`, `339(ii)`, `392`, `412`, `415`, `466`, `476`, `500(i)`, `501(i)`, `508`, `551`, `1422`

## Candidate Code Selection
- **Set A (Required)**: All non-excluded INS/E codes appearing in the repository's own label texts (frozen evaluation inputs, reference transcripts, out-of-sample test cases, and research notes).
  - Yield: **66 unique candidate codes**.
- **Set B (Optional)**: Public Indian sources (e.g. FSSAI regulation appendix).
  - Status: Omitted. Set A fully grounded 66 codes across the repo, remaining well within the 80 maximum code cap.

## Searched Repo Files and Per-File Code Yield (47 files)
- `data/cache/oos_herb_spice_1/inputs/S03.txt` (1 codes): 635
- `data/cache/oos_herb_spice_1/inputs/S04.txt` (6 codes): 150a, 341(iii), 552, 635, 951, 955
- `data/cache/oos_herb_spice_1/inputs/S15.txt` (1 codes): 319
- `data/cache/oos_herb_spice_1/inputs/S17.txt` (6 codes): 122, 306, 414, 422, 903, 904
- `data/cache/oos_herb_spice_1/inputs/S19.txt` (4 codes): 101, 160(ci), 621, 1420
- `data/cache/oos_herb_spice_1/inputs/S21.txt` (3 codes): 100, 160a, 307b
- `data/cache/oos_herb_spice_1/inputs/S24.txt` (4 codes): 307, 341(iii), 621, 1450
- `data/cache/oos_herb_spice_1/inputs/S26.txt` (2 codes): 170, 414
- `data/cache/oos_herb_spice_1/inputs/S30.txt` (1 codes): 640
- `evaluation/dev_regression_15/inputs/F02.txt` (2 codes): 150a, 307b
- `evaluation/dev_regression_15/inputs/F04.txt` (1 codes): 492
- `evaluation/dev_regression_15/inputs/F06.txt` (4 codes): 340, 407, 452, 460(i)
- `evaluation/dev_regression_15/inputs/F07.txt` (1 codes): 635
- `evaluation/dev_regression_15/inputs/F08.txt` (2 codes): 450(iii), 451(i)
- `evaluation/dev_regression_15/inputs/F12.txt` (1 codes): 160b
- `evaluation/dev_regression_15/inputs/F13.txt` (1 codes): 150c
- `evaluation/dev_regression_15/inputs/F14.txt` (1 codes): 122
- `evaluation/dev_regression_15/inputs/F15.txt` (1 codes): 635
- `evaluation/dev_regression_15/references.md` (13 codes): 122, 150a, 307b, 320, 322(i), 340, 407, 450(iii), 451(i), 452, 460(i), 492, 635
- `evaluation/fresh_batch_1/inputs/N01.txt` (1 codes): 516
- `evaluation/fresh_batch_1/inputs/N02.txt` (3 codes): 223, 341(ii), 450(i)
- `evaluation/fresh_batch_1/inputs/N04.txt` (1 codes): 196
- `evaluation/fresh_batch_1/inputs/N05.txt` (2 codes): 160c, 262(i)
- `evaluation/fresh_batch_1/inputs/N13.txt` (3 codes): 385, 1442, 1450
- `evaluation/fresh_batch_1/inputs/N16.txt` (1 codes): 501
- `evaluation/fresh_batch_1/reference.errata-v1.json` (4 codes): 123, 385, 1442, 1450
- `evaluation/fresh_batch_1/reference.json` (12 codes): 123, 150c, 160c, 223, 262(i), 341(ii), 385, 450(i), 501(ii), 516, 1442, 1450
- `evaluation/fresh_batch_1/references.md` (11 codes): 123, 150c, 160c, 223, 262(i), 341(ii), 385, 450(i), 501(ii), 516, 1442
- `evaluation/fresh_batch_2/inputs/M07.txt` (1 codes): 509
- `evaluation/fresh_batch_2/inputs/M09.txt` (4 codes): 223, 472c, 500, 503
- `evaluation/fresh_batch_2/inputs/M10.txt` (2 codes): 451, 635
- `evaluation/fresh_batch_2/inputs/M13.txt` (3 codes): 338, 436, 955
- `evaluation/fresh_batch_2/inputs/M14.txt` (1 codes): 122
- `evaluation/fresh_batch_2/inputs/M15.txt` (3 codes): 133, 297, 331
- `evaluation/fresh_batch_2/reference.json` (10 codes): 122, 133, 223, 297, 322(i), 331, 451(i), 472e, 509, 635
- `evaluation/fresh_batch_2/references.md` (10 codes): 122, 133, 223, 297, 322(i), 331, 451(i), 472e, 509, 635
- `evaluation/fresh_batch_3/inputs/Q11.txt` (2 codes): 407, 418
- `evaluation/fresh_batch_3/inputs/Q12.txt` (1 codes): 407
- `evaluation/fresh_batch_3/inputs/Q13.txt` (2 codes): 300, 414
- `evaluation/fresh_batch_3/reference.json` (4 codes): 331, 339(iii), 407, 418
- `evaluation/fresh_batch_3/references.md` (4 codes): 331, 339(iii), 407, 418
- `evaluation/negation_addendum/inputs/R1.txt` (1 codes): 509
- `evaluation/negation_addendum/inputs/R4.txt` (2 codes): 300, 331(iii)
- `evaluation/negation_addendum/inputs/R5.txt` (1 codes): 442
- `evaluation/negation_addendum/inputs/R6.txt` (3 codes): 122, 124, 133
- `research/04-nova-colour-and-butter-basis.txt` (1 codes): 236
- `research/05-ins-reference-provenance.txt` (3 codes): 161h, 451, 501

## EVIDENCE-MISSING List
- **Code 196**:
  - Found in `evaluation/fresh_batch_1/inputs/N04.txt` (Kurkure Chilli Chatka ingredient panel: `Acidity Regulators (330, 196)`).
  - INCHEM search and FAO JECFA index search yield no evaluation page for INS 196.
  - In international Codex numbering, food additive INS codes skip from 182 to 200. This is an unassigned additive code, indicating a probable pack misprint or OCR misread of 296 (malic acid).
  - Marked `EVIDENCE-MISSING`, URL and functional class left blank.

## Explicit Non-Goals
1. **No Classification Decisions**: No NOVA groups, UPF flags, or cosmetic/functional determinations are made.
2. **No Resource Modifications**: Zero edits to `src/foodscan/resources/lexicon.csv`, `synonyms.csv`, `markers.csv`, `descriptors.csv`, or `ins_names.csv`.
3. **No Code or Test Modifications**: No changes to pipeline code, classifier, or test suites.
4. **No Forbidden Sources Used**:
   - Codex GSFA Online (`fao.org/gsfaonline`) was NOT used.
   - Codex standard/guideline documents (CXG/CXS) were NOT used.
   - Bulk database scraping/harvests were NOT used.
   - All accepted rows are individually verified and cited from static WHO IPCS INCHEM JECFA evaluation pages.
