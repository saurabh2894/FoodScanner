# Combined conditioned juice and named-water candidate
23 November 2026. Base ff0e3a7. Staged review only, not committed, pushed or deployed.

## Scope
Five recognition names added in total: apple juice, grape juice, orange juice, pineapple juice and carbonated water. Four juices retain the previously accepted conditions. The only new positive water route is a sole item whose raw wording is exactly carbonated water or plain carbonated water, ignoring case and surrounding punctuation. The item cannot acquire Group 1 through descriptor stripping, percentage claims, brackets or category membership.

Khandpur et al. 2021, Table 3 names a combined plain-or-carbonated-water dietary item as Group 1. It has no sensitivity-analysis flag. Initial rater disagreement is reported, but this row is not among the unresolved sensitivity items. The implementation deliberately does less than the source: mixed lists and nested water remain unresolved unless an independent existing strong marker decides Group 4. No sparkling/seltzer/soda/tonic synonyms, water product categories, flavoured/sweetened drinks or other cohort rows are added.

## Reuse
Article https://pmc.ncbi.nlm.nih.gov/articles/PMC8453454/ displays CC BY 4.0. Current license deed https://creativecommons.org/licenses/by/4.0/ allows commercial sharing/adaptation with credit, license link and change indication. NOTICE credits all authors, title, journal, DOI, source and license; describes the selected row and narrower local adaptation; no endorsement implied. No bulk table copied.

## Verification
- 16,440/16,440 Python/JS source-mode analyses identical, including 30 new water form/context controls and 106 descriptor placements.
- 307 focused water/juice/historical demand tests passed before final browser wording adjustment. 195 configured water/juice/historical-source/browser-provenance cases passed on updated final source; includes the 22 browser provenance checks.
- Broad run before evidence packaging: 10,869 passed, 19 skipped, 5 xfailed, two failures. Existing millet photo misses Puff; ordinary environment lacks the Playwright module path for provenance test. Configured provenance passes separately. No whole-suite pass claim.
- Fresh-process baseline against published ff0e3a7 and candidate on 66 regression inputs: no group, driver, status or reason changes. Unassessed vocabulary shrinks on M13/Q13/R6 for carbonated water and M14/F14 for four juices. Those seven contextual occurrences are not seven newly classified ingredients. Named water in the three existing mixed labels remains unplaced despite existing independent Group 4 drivers.
- Demand miner on candidate: 232 distinct terms, 80 open, 73 recognized, 77 photo-only. Published baseline was 85 open/68 recognized/77 photo-only. Recognition is not placement or fresh accuracy.
- 390/1280 browser and native screenshots captured. Plain-water Group 1, mixed-water abstention and independent-marker Group 4 checked visually at 390; plain/mixed browser views checked at 1280. Native abstention uses a short h2 and the exact reason in a normal paragraph; corrected 390/1280 pixels inspected. No fresh OCR claim.

## Holds and limitations
Liquid glucose, cocoa solids, cocoa powder, milk forms, cranberry/tamarind and all other prior holds remain. Code comments in old tests that describe historical owner approvals were not authority for this work. Current parent assignment was research/implementation assessment only. No release.

The five-name combined batch is still small and does not solve the requested scale. The water rule is intentionally narrower than ordinary ingredient-level identity transfer. A later broader mixed-list rule would need its own source-scope review, not removal of this guard merely to raise coverage.

## Historical tests
Three old tests asserting no carbonated-water recognition now explicitly assert the new named_water kind or positive sole-item route plus continued mixed/treated-form abstention. Historical JSON decision records are unchanged. All unrelated hold assertions remain.

## Final presentation correction
Native template now separates the short abstention h2 from the complete reason paragraph for all abstentions. Source semantics and CLI headline are unchanged. Accessible heading/body structure is regression-tested; 11 native web tests pass. Corrected native screenshots at 390/1280 inspected. Final packaged test count is recorded in HANDOFF.md.
