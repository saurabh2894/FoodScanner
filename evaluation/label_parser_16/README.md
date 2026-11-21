# Task 16: Bounded Multigrain Parser Repair

## Context and Objective
Task 16 resolves two measured parser defects identified during the Task 15 multigrain label diagnostic run, without altering classification policies, NOVA evidence tables, lexicon entries, or synonyms:
1. **Footnote Handling**: Literal label has `Vitamins#` and `Minerals##`, while browser OCR reads `Vitamins”` and `Minerals**`. The parser previously failed to recognize these due to attached footnote symbols, dumping them into unassessed unknown text. Item-aware footnote normalization was added to resolve both to standard unplaced vocabulary entries (`vitamins`, `minerals`) while preserving raw tokens for audit.
2. **Bracketed Pair Connectors**: In `Multigrain Flour Blend (45.7%) [Sprouted Ragi & Jowar (23.4%), Rice & Oat (22.3%)]`, `_split_amp_pair` previously accepted only `&` and rejected `and`. Narrow support for `and` in two-item bracketed pairs was implemented, preserving all recognition, shared-modifier, enclosure, and shared-percentage conditions, while enforcing culinary blend guards (`_names_two_oils`), shared code list checks, and preserving connector fidelity in notes.

## Repository Provenance
- **Base commit**: `a6cacbc00fe3f8543a78f002b952a9a64375c4fd` (origin/main)
- **Final commit**: `cccb3e98fedd89994efc444540b98dd55fd15d70`
- **Branch**: `antigravity/label-parser-16`

## Files Changed
1. `src/foodscan/normalise.py`:
   - Added `_FOOTNOTE_RE` and `_FOOTNOTE_NO_QUOTE_RE` regexes targeting trailing footnote markers (`#`, `##`, `*`, `**`, `†` [U+2020], `‡` [U+2021], and OCR closing double quote `”` [U+201D]).
   - Added `strip_footnotes(text: str) -> str`, ensuring intentional quoted phrases (`"Natural Flavour"`, `“Natural Flavour”`) are preserved.
   - Integrated footnote stripping into `normalise_ingredient(raw: str)` before lookup.
2. `src/foodscan/pipeline.py`:
   - Updated `_split_amp_pair(raw: str)`:
     - Allowed connector to be either `&` or `and`.
     - Preserved connector fidelity in warnings (`"{mod}" was read as shared by both sides of "{left} {conn} {right}"`).
     - Added culinary blend guard `_names_two_oils([left, right_full])` to keep blends like `Corn and Canola Oil` whole.
     - Added `_shared_code_list` guard to keep code lists like `Emulsifiers and Stabilizers [INS 460(i), INS 471]` whole.
3. `web_preview/foodscan.js`:
   - Ported `stripFootnotes(text)` matching Python's regexes and logic.
   - Updated `normaliseIngredient(raw)` to strip footnotes before lookup.
   - Updated `splitAmpPair(raw)` matching Python's connector support, culinary blend guard, shared code list guard, and connector-faithful warnings.
4. `tests/test_ampersand_split_1.py`:
   - Updated `test_synthetic_negative_controls_stay_whole` parameter `"Rice and Oat"` to `"Rice or Oat"` to reflect that `and` is now an approved connector while `or` remains unsupported.
5. `tests/test_label_parser_16.py`:
   - 25 comprehensive unit and regression tests covering:
     - Footnote marks adjacent to spaces, commas, percentages, and brackets.
     - Quoted phrase preservation.
     - Raw text preservation for audit.
     - `_split_amp_pair` with `and` and `&`.
     - Culinary blend guard for `Corn and Canola Oil` (inside/outside brackets, with/without shared percentage).
     - Positive contrast for `Rice and Sunflower Oil`.
     - Synthetic guards (unknown second terms, unrecognised modifiers, >2 parts, shared code lists, negations, non-percentage details).
     - Acceptance agreement across Literal, OCR, and Normalized label texts.
6. `evaluation/label_parser_16/matrix_comparison.json.txt`:
   - Structured JSON array re-evaluating the 23 variants from Task 15.
   - Records exact intentional differences (2 variants) and unexpected differences (0 variants).
7. `evaluation/label_parser_16/STATUS.md`:
   - Gate status and pass metrics.

## Gate & Verification Metrics
- **Pytest Suite**: 2,061 passed, 6 skipped, 5 xfailed, 0 failed (2,072 total test items).
- **Parity Gate (`scripts/parity_check.py`)**: 859/859 identical analyses between Python and JavaScript (781 photo-path texts, 78 pasted-text texts).
- **Synthetic Matrix Re-run (23 variants)**:
  - 23/23 parity pass between Python and JavaScript (0 mismatches).
  - Intentional differences: 2
    - `VAR-01-BASELINE-LITERAL`: Footnote hash normalization (`#` and `##`) resolves `Vitamins#` and `Minerals##` to `unplaced` instead of dumping into `unassessed`.
    - `VAR-03-AMPERSAND-TO-AND`: Bracketed pair connector `and` now splits into recognized items instead of failing to split and dumping both items into `unassessed`.
  - Unexpected differences: 0 across all 23 variants.

## Acceptance Criteria Verification
- **Agreement**: Original literal, actual browser OCR text, and normalized diagnostic text agree on all recognized ingredients:
  - `Sprouted Ragi`, `Sprouted Jowar`, `Vitamins`, `Minerals` are all recognized as `unplaced`.
- **Honest Abstention**: All three runs abstain honestly with `group: None`. No forced NOVA group.
- **Reason**: All three runs consistently report:
  `only weak or unlisted markers present (Antioxidant (Natural Tocopherol) -> "antioxidant" (unlisted_additive)); not enough to call a group`
- **Shared Percentages**: Both `(23.4%)` and `(22.3%)` remain strictly pair context in warnings, never duplicated onto individual items.
- **Parent Group Name**: `Multigrain Flour Blend (45.7%) (group name; its contents were assessed separately)` is recorded as metadata in `unassessed`, never blocking analysis as an unknown ingredient.

## Explicit Limitations
- Parity match is engine agreement between Python and JavaScript, not proof of NOVA correctness.
- The multigrain label remains unclassified (abstaining). Sprouted grains and vitamins/minerals remain unplaced absent senior-reviewed classification evidence.
- Headline wording improvements and animal-form guards are reserved for senior review and integration.
