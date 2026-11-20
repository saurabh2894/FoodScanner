# Errata to references.md / reference.json (version 1)

references.md and reference.json are NOT edited: batch 1's original scores (build 12e7226) keep their 121-item denominator. Any re-run from the fix round on
states the corrected denominator below.

## Erratum 1 (v1): N13, `nature identical and natural flavouring substances` is ONE item
The original reference counted it as two items (Nature identical flavouring substances; Natural flavouring substances). It is one declared phrase (two modifiers,
one head noun), and keeping it whole loses nothing. N13's reference therefore has **11** items instead of 12 and the batch has **120** instead of 121.
`reference.errata-v1.json` holds the corrected N13 entry.

## What changes in the re-run table (REGRESSION.md, build 9c00962), recomputed on 120
| Mode | Own item | Merged | Split | Omitted | Total |
|---|---|---|---|---|---|
| Paste, before (12e7226), on 120 | 93 | 15 | 2 | 10 | 120 |
| Paste, after (9c00962), on 120 | 107 | 13 | 0 | 0 | 120 |
| Photo, before, on 120 | 18 | 10 | 0 | 92 | 120 |
| Photo, after, on 120 | 28 | 10 | 0 | 82 | 120 |
(The original 121 figures stay valid for the original run. The classification counts do not change: 13 judged labels either way.)
