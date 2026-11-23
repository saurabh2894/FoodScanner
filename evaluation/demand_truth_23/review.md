# Current demand, 23 November 2026

Tool-only correction. No application, classifier, data-table, source, OCR or deployment configuration changes.

## Demonstrated defect and bounded fix

Historical unassessed terms were tested against vocabulary alone. Seven already-supported simple strong-marker terms were falsely still ranked open: wheat gluten, whey powder, hydrolysed vegetable protein, lemon juice concentrate, apple juice concentrate, fructose and whey solids. Each has zero current live-unassessed inputs. Recognition now includes the full pipeline's simple-term strong-marker route, requiring drivers and no unresolved names or unplaced items. Compound or bracketed forms are excluded from this closure route. Existing vocabulary behavior is preserved.

The first negative test exposed why a Group 4 answer and empty unassessed list alone are insufficient: bracketed unknown content on a decisive concentrate marker can be ignored by current classification. The tooling now conservatively leaves all compound/bracketed marker-only phrases open. No classifier change or new placement claim was made.

## Result

232 terms remain. Open paste-demand terms: 80 -> 73. Recognised: 73 -> 80. Photo-only: 77 unchanged. Of 73 open terms, 67 occur in current live unassessed output and six only in historical paste evidence. Historical source counts and photo-only exclusions remain separate. These are development-corpus counts, never population coverage or accuracy estimates.

The current 66-input census has 38 Group 4, eight Group 1, two Group 3 and 18 abstentions. Thirty-two answered inputs still include unresolved names/forms. This is not proof those unresolved items would change their already-supported Group 4 result.

## Remaining blockers and next milestone

The strongest unmet product need is reliable ingredient preservation from actual photos, not another small naming release. The existing millet fixture loses the Puff section in its first reading; its second reading recovers sections but reads code 296 as 295. Group agreement and higher yield do not settle either error. The held OCR selection change must not ship. Current correction/comparison workflow is functional in tested controls.

Practical next milestone: a reader candidate must preserve every ingredient section and numeric code on all available original, rights-cleared labels, explicitly recording both readings and selecting neither as verified truth when they disagree. Score section preservation, complete ingredients, exact codes, and false additions separately before any group comparison. Require all current text/parity/browser gates and no new photo regression. Use only existing local originals; no private-photo disclosure, paid service, new collection request, held integration, source-pool retry or holdout tuning. If no candidate meets this gate, ship no OCR selection change and retain correction as the safe path.

Coverage work stays evidence-gated. Leading real unresolved demand remains liquid glucose, cocoa solids, and spices & condiments (five distinct inputs each), then yeast extract/cocoa powder and fruit pulp forms. Prior source investigations did not justify placement; repeated frequency is not evidence. Source, licence and product-name-prefix gaps remain held. No renewed exhausted-source search is justified by this corrected count.

## Checks

20 miner tests include historical closure, stream preservation, and strong-marker-plus-unknown/compound negative controls. Focused miner plus boundary tests: 37 pass. Full test execution initially lacked Playwright in the new worktree. The first browser rerun also lacked built assets. After restoring the existing pinned installation and reviewed dist, the separate acceptance/provenance/miner checks passed 26/26. Split broad checks: 10921 pass, five xfail, one known millet failure. The combined run exceeded its execution timeout and is not counted as pass. The known millet fixture failure remains; this release does not claim a whole-suite pass. Runtime bytes unchanged by design.
