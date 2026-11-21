# Indian Label Alias Candidate Table (alias_1)

## Summary & Base
- **Task**: Label-driven Indian ingredient alias candidate table pointing to existing canonical rows on `main`.
- **Base Commit**: `827cdcbf99010b22a94dcbb01bcd924ed9c9ff50` (cut from origin/main).
- **Scope**: Additions-only under `evaluation/alias_1/`. Zero edits to `src/`, `lexicon.csv`, `synonyms.csv`, `markers.csv`, `descriptors.csv`, `tests/`, or any existing file.

## Method & Execution
1. **Unrecognised Span Extraction**:
   - Analyser executed using `foodscan.pipeline.analyse_text(text, source='text')` across all 98 input label files in the repository:
     - Frozen evaluation inputs:
       - `evaluation/dev_regression_15/inputs/` (15 files: F01-F15)
       - `evaluation/fresh_batch_1/inputs/` (16 files: N01-N16)
       - `evaluation/fresh_batch_2/inputs/` (15 files: M01-M15)
       - `evaluation/fresh_batch_3/inputs/` (14 files: Q01-Q14)
       - `evaluation/negation_addendum/inputs/` (6 files: R1-R6)
     - Out-of-sample herb/spice inputs:
       - `data/cache/oos_herb_spice_1/inputs/` (32 files: S01-S32)
   - Executed in an external scratch environment with `sys.dont_write_bytecode = True` (`python -B`) to ensure zero `__pycache__`, temporary files, or cache pollution in the repository checkout.
   - Total unassessed ingredient occurrences extracted: **276**.
   - Total unique unrecognised spans: **254**.

2. **Grounding & Evidence Requirements**:
   - **Demand Evidence**: Verified file and line reference in repository label texts (or `'none - FDC-sourced'` for supply-side FDC candidates).
   - **Equivalence Evidence**: Independent admissible naming evidence linking alias to canonical target:
     - FDC foundation or SR Legacy food attribute record ID citing Common Name (type 1000) or Additional Description (type 1001).
     - Authoritative lexical, statutory, or standards citations (e.g., FSSAI Food Safety Standards Regulations, Merriam-Webster, Oxford English Dictionary, Spices Board India, Molesworth Marathi Dictionary) with exact quoted text.
     - Label-only occurrences without independent equivalence evidence are marked `NEEDS_EQUIVALENCE_EVIDENCE` with `equivalence_evidence = 'NONE'`.
     - Ambiguous terms are marked `AMBIGUOUS` with candidate targets listed.

3. **FDC Mining**:
   - Mined USDA FoodData Central bulk datasets cached in repo (`data/cache/fdc/`):
     - Foundation Foods: `FoodData_Central_foundation_food_csv_2026-10-29.zip`
     - SR Legacy Foods: `FoodData_Central_sr_legacy_food_csv_2018-04.zip`
   - Extracted common names and alternate names for commodities matching existing canonical rows in `lexicon.csv` on `main`.

## Counts
- **Total Unique Unrecognised Spans Found**: 254
- **Alias Candidate Table Rows (`alias_candidates.csv`)**: 37
  - **PROPOSED**: 33 (10 label-demand, 23 FDC-sourced)
  - **AMBIGUOUS**: 2 (1 label-demand: `refined palmolien oil` -> `palmolein / palm oil`; 1 FDC-sourced: `pak choi` -> `bok choy cabbage / chinese cabbage`)
  - **NEEDS_EQUIVALENCE_EVIDENCE**: 2 (2 label-demand: `cassia`, `cassia whole` -> `cinnamon`, equivalence: `NONE`)
- **No-Target Spans (`no_target_spans.csv`)**: 239 (100% of remaining unrecognised spans accounted for with literal guess-free descriptions)

## Form Fidelity
Aliases preserve strict form fidelity. Qualifiers indicating different processing, cut, grade, or state (e.g. `powder`, `extract`, `puree`, `pulp`, `paste`, `flakes`, `roasted`, `fried`, `cooked`, `salted`, `brine`, `juice`) never disappear through an alias mapping. Unrecognised spans with such qualifiers are routed to `no_target_spans.csv` rather than mapping to plain commodity rows.

## Held / Parked Term Exclusion List
In accordance with task instructions, the following held/parked terms are strictly off-limits and no aliases were proposed that route to or resurrect them:
- `cranberries` / `cranberry`
- `cocoa powder`
- `dry fruits` / `dry fruit`
- `glucose syrup`
- `liquid glucose`
- `texturized soy protein`
- `beets` / `beet`
- `celery` / `celery powder`
- `arrowroot`

All occurrences of these terms in the label corpus have been recorded in `no_target_spans.csv` with explicit exclusion notes.

## Non-Goals
- **No classification content**: Zero NOVA groups, marker languages, or placement opinions. All entries represent pure naming/lexical claims.
- **No staging or code modifications**: No changes to `src/foodscan/resources/lexicon.csv`, `synonyms.csv`, parser, classifier, or test files.
- **No speculative mappings**: Spans without verifiable equivalence remain `NEEDS_EQUIVALENCE_EVIDENCE` with equivalence `NONE` or are logged in `no_target_spans.csv`.
