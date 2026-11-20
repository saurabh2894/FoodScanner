# Out-of-sample challenge set re-run with the peel-label guard (claude/peel-label-guard-1)

Same 32 cached labels (sha256 verified), BEFORE = 6cf9a99~1, AFTER = guarded build, separate fresh processes. Targeted challenge set for the staged terms, not a coverage estimate.

| | committed results (main, 5ce13fa) | with guard |
|---|---|---|
| mentions recognised / NOT recognised / inside another item | 40 / 24 / 2 | 38 / 26 / 2 |
| labels with changed group, status, drivers or reason vs the pre-batch build | S01, S06, S07, S10, S11, S19, S29 | S01, S06, S07, S10, S11, S29 |
| labels with newly unassessed items | S19 | none |

Every difference is in S19 (the other 31 labels are identical in every stored field):
- the two "paprika" mentions go from recognised to NOT recognised (the item "PAPRIKA POWDER FLAKE(0.6%): ROASTED SESAME" stays whole and unassessed, as before the batch);
- status goes complete -> uncertain, equal to the pre-batch build (the suspect-section reason persists, honestly);
- ingredient items 27 -> 26, newly recognised items lose the paprika flake item, newly unassessed items: none (`ROASTED SESAME` is again part of the whole item).
Group stays 4 throughout.
