# Narrowed extraction and uncertainty guard
23 November 2026. Replaces initial review recommendation. Private on d086d28, not pushed.

## Behavior
Existing direct additive-class aliases gain literal bare-code extraction. Raw codes and names are retained. An explicitly parsed class that has no overlap with the local code mapping's recorded classes makes the entire entry unresolved. Marker evidence from that entry is withheld, including any other codes sharing it. This does not prove a printed class wrong or deny other possible functions. Unknown codes, empty mapping classes and overlapping multi-role entries are not asserted to conflict. No new taxonomy or source mapping. Bare, INS, E and Contains-clause forms use the same guard. Other undisputed entries can still decide. Absence-claim guard remains: keep negated entries visible and unresolved without positive evidence.

## Results and evidence
16,130 Python/JS comparisons pass (15,854 existing plus 276 focused). 102 focused/browser tests pass. Broad default suite: 10,669 pass, 19 skipped, five expected failures, plus unchanged millet missing-Puff failure and missing-Playwright harness setup failure. Browser test passes in separately configured focused run. Four earlier mismatch expectations and one UI wording expectation changed openly; frozen historical data unchanged.

The earlier 66-input helper used default OCR-source semantics, not pasted semantics. Both are now supplied: before.json/after.json are OCR-source, before-text.json/after-text.json are pasted-source. Pasted results: N15 changes Group 4 to abstention because stabilizer/INS471 conflicts with local emulsifier mapping; N16 and F06 keep Group 4 using independent evidence but lose disputed-entry drivers. M13/Q13/F07 gain six literal codes and keep Group 4. No other pasted group changes. Ordinary N15 OCR path still does not locate a list. This correction must not be presented as OCR improvement.

Earlier full corpus decision comparison showed no newly positive Group 4 transitions. Two old corpus cases become uncertain: flavouring (627) conflicts with flavour-enhancer mapping, and peanut stabilizer/INS471 conflicts with emulsifier mapping. New synthetic claim/mismatch controls also abstain instead of claiming Group 1 or 4. Existing unrelated source-scoped food placements remain unchanged. Full provisional decision diff is narrowed-decision-diff.json; later final changes propagate unresolved status to all codes in the same entry and clarify UI counts, not group decisions.

## UI
Inspected final native/browser 390px mismatch renders: code retained, zero usable decision rules, item marked unassessed, mismatch pill and explanatory warning. No positive marker effect shown. Source URL now wraps. Native conflict page has no horizontal overflow at 390/1280 after narrow .src wrapping. Earlier Q13 renders inspected at 390/1280; existing native Q13 document overflow was 16px on both baseline and candidate. Full native layout is not declared clean. Screenshots are local renders, not production.

## Limits
Known millet section/read selection failure remains. General natural-language negation and code-name identity conflicts outside an explicitly parsed role are not solved. Disjoint classes in a limited mapping are uncertainty, not authoritative incompatibility. No OCR/model/source changes, holdout access, or deployment. Repository historical approval-attribution comments were not treated as authority. Release requires original grant and current main validation and no deployment retry loop.
