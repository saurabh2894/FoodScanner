# Foodscan naming slice 8

Local candidate only. Based on main 1513332f3d63462b85da98499ca2dc2133c7b564. No branch, commit, push or deployment for this slice.

Six plain-food heads and 29 same-food aliases bring the candidate to 524 heads and 278 aliases. The new heads are sweetcorn, red mombins, yellow mombins, atemoyas, acai berries and bilberries. Placement is class-instance under the cited NOVA fruit/vegetable class, not a claim that these six foods are individually named in that source. USDA NALT supplies identity and food category, not NOVA placement. No classifier, browser runtime or strong-marker change.

Existing tomato provenance is corrected to the current fruit/vegetable class clause and NALT tomato identity. No other existing non-provenance behavior changes in the 767-name comparison.

## Validation

- Suite: 8,023 passed, 2 known baseline failures, 2 skipped, 1 restricted-reference test deselected, 5 expected failures. Not fully green.
- Known failures: millet-puff photo section extraction and historical mining evidence missing fenugreek. Neither was changed or claimed fixed.
- Build and standard parity: 12,833/12,833 full-field analyses agree, including 6,799 OCR-text-path and 6,034 paste-path inputs. These are text-path checks, not new photo-capture validation.
- Wider full-field parity: 57,007 inputs, no mismatch.
- Alias-parent checks: 45,588 comparisons, no mismatch.
- All 767 old names retain non-provenance fields. Only tomato's analysis citation differs.
- Frozen 66: no differences.
- Original photo/OOS-32 assets were not newly validated.
- Local rendered results inspected: sweetcorn Group 1, salted sweetcorn Group 3, Portobello Mushrooms Group 1, explicit red-mombin whole powder abstains.

## Limits retained

Red-mombin powder has an existing conservative color-parsing abstention, even with explicit whole-food composition. It is disclosed, not treated as a successful powder route. Explicit same-food powders with culinary sugar otherwise follow existing Group 3 handling. Unqualified sugared names and unsupported derivatives remain negative controls. Portabello Mushrooms and Portobella Mushrooms were not added: the current identity page names Portobello Mushrooms. Summer squash was already supported and is preserved, not counted as new coverage.

## Release status

An atomic web-editor dry run was not byte-preserving. The trial edits were discarded. Final visual inspection showed an empty source-change list and main at 1513332. Nothing was committed. A safe atomic staging method, complete remote diff and pinned-byte verification remain release gates.

Production was last checked separately at PR9, 517 heads/189 aliases. PR10 is on main but its live publication is blocked by the confirmed deployment cap. No exact account reset time is known. No retry, upgrade, recovery-code use or service-account setting change was made. The read-only dashboard check awaits an authenticator code.
