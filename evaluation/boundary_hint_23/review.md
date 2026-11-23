# Adjacent-bracket ingredient-boundary diagnostic
23 November 2026. Candidate on reliability/boundary-hint-23, based on 60cfc429. Not yet committed/pushed.

## Demonstrated problem
Existing real pasted development input b2/M12 contains MIXED SPICES (CLOVE, CINNAMON, CHILLI) PRESERVATIVE (INS 211) without a separator. Current parser keeps one item and reports complete text accounting. Keeping words is correct; claiming item-boundary certainty is not supported.

## Narrow change
Detect a closing top-level food bracket immediately followed by an additive-class phrase and another bracket. Emit a possible-boundary warning naming the unchanged item; mark completeness uncertain with a reason explicitly distinguishing accounted-for words from uncertain item boundaries. No split or comma invented. No direct classifier/marker/code mapping change, classification gating change or rule/source admission.

Exclude nested wording, an already additive-class item, explicit comma/and separators, simple percentage brackets and nonclass role text. Spelling normalization of initial stabilizer/emulsifying/thickening phrases is used only to avoid false-positive diagnostics on existing additive declarations.

## Authority recovery
Repository reviewer attribution is not authority. Authenticated channel search located a Nov20 forwarded report describing M12 and complete status, not a user hold. No direct user restriction on future boundary diagnostics found. Main requested this bounded review under established technical autonomy. Historical source/OCR holds remain untouched.

## Verification
- 17 dedicated controls, 62 focused parser/pipeline/native-web tests pass.
- 16455/16455 Python/JS source-mode comparisons, including new positive/negative patterns.
- Fresh-process 66-input comparison: only M12 completeness status/warnings change. No group, driver, item list, code mapping or classification reason changes.
- Dependency-enabled broad suite excluding acceptance: 10908 passed, 5 xfailed, one existing millet section failure. Acceptance file separately 5/5 passed. Not a clean full-suite claim.
- Browser 390/1280 and native 390 screenshots inspected. Warning names unchanged item, Group 4 still supported by existing independent evidence, completeness reason visible. Synthetic controls are not new photo/OCR accuracy.

## Caution
Completeness is also an input to existing OCR early-stop logic. This signal applies only when a bracketed additive declaration exists, hence a code/class-bearing item normally already forces the bounded second reading. Nevertheless no claim of identical behavior on unseen photographs is made. No OCR selection tie-break was changed. Do not use this diagnostic to infer a correct split or choose a code/reading.

## Backlog reconciliation
Current probes confirm old entries resolved: US Stabilizer code extraction, combined class code extraction, Contains-line declaration code display, explanatory INS note separation, M08 milk-solids/sugar split. BACKLOG.md now separates current verified status from historical attribution. Product-name prefix remains unresolved: only synthetic reproduction recovered, no safe original source for arbitrary capitalized-line stripping. M04 boundary correctness is not claimed from complete word accounting. Other sourcing, milk, family-code and OCR holds unchanged.

## Files
Code: parser.py diagnostic, pipeline.py/JS mirrored warning and completeness reason; no template change. Tests: test_boundary_hint_23.py, parity controls. Evidence private under /tmp/deep-research/foodscan-boundary-hint-23. BACKLOG.md reconciliation is documentation, not new authority. No new external source or private-photo handling.
