# Batch 1 re-run as REGRESSION against the fix-round build (code commit 9c00962)

This batch was used to find the failures, then the fixes were written against it. This re-run therefore shows what changed, it is NOT validation, and the
numbers are not comparable to an independent check. Same inputs, same references (written before the first run), same denominators: 15 labels, 121
reference items, 13 judged. Adjudication of OCR-garbled items is approximate. Outputs: `regression_9c00962/`. The earlier frozen outputs: `frozen_results_12e7226/`.

## Extraction (reference items)
| Mode | Own item | Merged | Split | Omitted | Additions | List found in the right place |
|---|---|---|---|---|---|---|
| Paste, before (12e7226) | 92 | 17 | 2 | 10 | 0 | 15/15 |
| Paste, after (9c00962) | 106 | 15 | 0 | 0 | 0 | 15/15 |
| Photo, before | 18 | 10 | 0 | 93 | 8 | 7/15 (1 wrong block, 7 no list) |
| Photo, after | 28 | 10 | 0 | 83 | 5 | 9/15 (no wrong block, 6 no list) |

## Classification (13 judged; abstentions are their own outcome)
| Mode | Correct confident | Wrong confident | Abstained |
|---|---|---|---|
| Paste, before | 8 | 0 | 5 |
| Paste, after | 10 | 0 | 3 (N08 probiotic culture, N09 composition text glued to buffalo milk, N11 weak/unlisted only) |
| Photo, before | 2 | 0 | 11 |
| Photo, after | 2 | 0 | 11 |

## Per-label delta
| Label | Paste | Photo |
|---|---|---|
| N02 | items 11 to 12: flavouring and `dough conditioner (223)` now two items | unchanged (no list) |
| N03 | abstain to Group 4; items 4 to 14; both sections `Noodles 88.5%` and `Seasoning 11.5%`; completeness complete | no list to a list found (inferred block, 4 items, flagged uncertain, abstains); the second section is warned as unread |
| N12 | abstain to Group 4 ("emulsifying & stabilizing agent" is the emulsifier class) | unchanged (list cut off, abstains) |
| N13 | items 12 to 11: `thickeners - E1442, E1450` is one item | the marketing line is no longer taken for the heading: the real list is found through the second reading (6 items, warnings, abstains); before: a wrong block reported "complete" |
| N14 | items 9 to 8: `Dry Fruits, Nuts & Seeds (22%) {...}` is one group | unchanged (no list) |
| N15 | completeness complete to uncertain: "a comma may be missing" after `(91%)`; group unchanged | unchanged (no list) |
| N07, N08, N09 | unchanged | completeness complete to uncertain (new warnings on garbled text) |
| N05, N06, N11, N12 | unchanged group | one more warning: the two readings disagree on additive codes (e.g. N05: INS 262 against INS 160c, 262i, 551): a review hint, nothing chosen |
| N01, N10, N15, N16 | unchanged | unchanged (OCR unusable or damaged heading) |
No label got worse: no group changed from correct to wrong, and no list that was found before was lost.
