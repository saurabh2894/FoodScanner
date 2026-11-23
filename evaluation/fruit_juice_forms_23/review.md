# Conditioned fruit-juice coverage candidate
23 November 2026. Base ff0e3a7, private candidate, not published.

Four new independently named food forms: apple juice, grape juice, orange juice and pineapple juice. USDA NALT supplies naming and fruit-juice category only, under its current CC BY4.0 notice. Existing FAO2019 Table1 positively places fresh or pasteurized fruit juices with no added sugar, sweeteners or flavours. These exact fruit-specific juices are class instances, not literally named by FAO.

Bare juice stays uncertain. The new kind fruit_juice cannot inherit a fruit/whole-food answer from descriptor removal. Only a sole exact named juice with its own explicitly100% fresh/pasteurized wording takes Group1. No lower-group classification of bare juice, reconstituted juice, concentrate, nectar, powder, recipe, bracket or mixed-item list is introduced. Independent existing strong markers still decide Group4. Unresolved named juices remain visibly unplaced, including on Group4 results, and not counted as fully assessed. Native/browser terminology follows that distinction.

The initially investigated cranberry/tamarind additions were removed before review. Their historical plain-versus-sweetened dried and raw-fruit-versus-pulp/paste holds remain. Old repository owner-approval labels were not used as permission. No held PMC/GSFA/Codex/IFCT/OFF or alternative-OCR work reopened. No spending.

## Impact and verification
- 66 real pasted label groups unchanged. M14/F14 each move four juice names from unknown vocabulary to recognized-but-unplaced, not to classified. Pulp entries remain unknown.
- 16,304 Python/JS source-mode comparisons pass before final packaging.
- 154 focused new controls plus browser provenance's22checks pass in a configured run (155 pytest cases combined).
- All global descriptor words audited on all four juices. Only the explicitly100% fresh/pasteurized patterns open the new positive path. Other condition/bracket/nested controls abstain or retain an independent existing marker.
- Pre-packaging broad run:10827passed,19skipped,5xfail,2fail. Existing millet missingPuff and unconfigured Playwright harness failures; the browser provenance test passes separately with its existing installed dependency path. Final-tree verification will be recorded separately.
- Local390/1280browser and native pixels inspected. These are synthetic pasted controls, not new OCR/photo accuracy evidence. Known millet/N15OCR limits remain.

## Test changes
Historical juice assertions are updated explicitly from no-row/no-recognition to fruit_juice recognition plus continued bare-form abstention. Concentrate markers unchanged. No historical fruit holds or frozen label references changed.

## Sources
See sources.md for exact observed URLs and scope. Naming evidence is not placement evidence. License/attribution notice added to NOTICE. No external source approval claims relied on.

## Final staged-tree check
After canonicalizing evidence IDs and packaging the review artifacts:10835passed,19skipped,5xfail,2fail in45s under the standard environment. Failures remain existing millet missingPuff and missing Playwright module setup.279focused ingestion/juice/historical-hold tests pass. The browser provenance test passes separately configured,155cases with juice controls. A broad configured-Playwright attempt was also run: it enables previously skipped tests that then fail because their expected browser download is absent; those harness errors do not establish behavior correctness and are not reported as passing. No whole-suite pass claim.

The demand miner succeeds on the actual packaged tree with no unknown evidence IDs. It reports81open/72recognized/77photoonly, previously85/68/77. That four-name recognition change is not four newly classified ingredients. Current M14/F14 juices remain unplaced.
