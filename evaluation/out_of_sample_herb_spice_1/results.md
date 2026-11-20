# Targeted out-of-sample challenge set: results for herb_spice_bulk_1

**This is a targeted out-of-sample challenge set for the staged terms. It is not a coverage estimate** (the draw searches for the new terms), and no figure here is a percentage of Indian foods or labels.

Retrieved 2026-11-20; 32 labels; before/after builds run in separate fresh processes; texts live in a gitignored cache (see README). Detail strings (full unassessed lists) are in the cache report, not committed.

Mentions of staged terms: 66; after-build status: {'recognised': 40, 'NOT recognised': 24, 'inside another item': 2}

## NOT recognised (abstention or gap on a staged term): first-class results

- S02 (0677937725636): `basil` (target `basil`): **NOT recognised**
- S03 (06172282): `celery seed` (target `celery seed`): **NOT recognised**
- S03 (06172282): `paprika` (target `paprika`): **NOT recognised**
- S05 (0769807238367): `coriander leaves` (target `coriander leaf`): **NOT recognised**
- S05 (0769807238367): `cumin seeds` (target `cumin seed`): **NOT recognised**
- S06 (0846203004878): `coriander leaves` (target `coriander leaf`): **NOT recognised**
- S06 (0846203004878): `coriander leaf` (target `coriander leaf`): **NOT recognised**
- S07 (00002899): `cumin seeds` (target `cumin seed`): **NOT recognised**
- S07 (00002899): `fenugreek seeds` (target `fenugreek seed`): **NOT recognised**
- S09 (8906186410010): `dill seeds` (target `dill seed`): **NOT recognised**
- S11 (4007273656565): `basil` (target `basil`): **NOT recognised**
- S11 (4007273656565): `parsley` (target `parsley`): **NOT recognised**
- S13 (3948537078321): `coriander leaves` (target `coriander leaf`): **NOT recognised**
- S13 (3948537078321): `paprika` (target `paprika`): **NOT recognised**
- S13 (3948537078321): `parsley` (target `parsley`): **inside another item**
- S14 (12345678): `parsley` (target `parsley`): **inside another item**
- S16 (4012824401075): `peppermint` (target `peppermint`): **NOT recognised**
- S23 (0801541001439): `spearmint` (target `spearmint`): **NOT recognised**
- S23 (0801541001439): `cumin seed` (target `cumin seed`): **NOT recognised**
- S26 (8906098831286): `rosemary` (target `rosemary`): **NOT recognised**
- S26 (8906098831286): `thyme` (target `thyme`): **NOT recognised**
- S27 (8901552023450): `coriander leaves` (target `coriander leaf`): **NOT recognised**
- S27 (8901552023450): `caraway seeds` (target `caraway seed`): **NOT recognised**
- S30 (0850015415975): `cumin seeds` (target `cumin seed`): **NOT recognised**
- S30 (0850015415975): `fenugreek seeds` (target `fenugreek seed`): **NOT recognised**
- S32 (8901192215116): `fenugreek seeds` (target `fenugreek seed`): **NOT recognised**

## Per staged target (mentions across all drawn labels, after build)

| target | eligible pool | labels drawn | mentions recognised | NOT recognised | inside another item |
|---|---|---|---|---|---|
| allspice | 0 | 0 (**no label drawn**) | 0 | 0 | 0 |
| basil | 30 | 2 | 2 | 2 | 0 |
| celery seed | 3 | 2 | 1 | 1 | 0 |
| chervil | 0 | 0 (**no label drawn**) | 0 | 0 | 0 |
| coriander leaf | 37 | 2 | 0 | 5 | 0 |
| coriander seed | 41 | 2 | 6 | 0 | 0 |
| dill weed | 0 | 0 (**no label drawn**) | 0 | 0 | 0 |
| dill seed | 1 | 1 | 0 | 1 | 0 |
| marjoram | 0 | 0 (**no label drawn**) | 0 | 0 | 0 |
| oregano | 56 | 2 | 4 | 0 | 0 |
| paprika | 29 | 2 | 5 | 2 | 0 |
| parsley | 72 | 2 | 3 | 1 | 2 |
| peppermint | 7 | 2 | 1 | 1 | 0 |
| rosemary | 15 | 2 | 3 | 1 | 0 |
| saffron | 32 | 2 | 4 | 0 | 0 |
| sage | 1 | 1 | 1 | 0 | 0 |
| savory | 0 | 0 (**no label drawn**) | 0 | 0 | 0 |
| spearmint | 18 | 2 | 1 | 1 | 0 |
| tarragon | 1 | 0 (**no label drawn**) | 1 | 0 | 0 |
| thyme | 12 | 2 | 5 | 1 | 0 |
| anise seed | 0 | 0 (**no label drawn**) | 0 | 0 | 0 |
| caraway seed | 4 | 2 | 1 | 1 | 0 |
| cumin seed | 51 | 2 | 2 | 4 | 0 |
| fenugreek seed | 26 | 2 | 0 | 3 | 0 |

## Changes of group, status, drivers or reason between before and after

- S01: ['reason'] (group None -> None, status complete -> complete)
- S06: ['reason'] (group None -> None, status complete -> complete)
- S07: ['reason'] (group None -> None, status complete -> complete)
- S10: ['reason'] (group None -> None, status uncertain -> uncertain)
- S11: ['reason'] (group None -> None, status complete -> complete)
- S19: ['status'] (group 4 -> 4, status uncertain -> complete)
- S29: ['reason'] (group None -> None, status complete -> complete)

## Per label

| id | barcode | target | staged-term mentions (after status) | newly recognised items | newly unassessed | unassessed before -> after | group before -> after |
|---|---|---|---|---|---|---|---|
| S01 | 00850001 | basil | basil: recognised | 1 | 0 | 33 -> 32 | None -> None |
| S02 | 0677937725636 | basil | basil: NOT recognised | 0 | 0 | 1 -> 1 | None -> None |
| S03 | 06172282 | celery seed | celery seed: NOT recognised; paprika: NOT recognised | 0 | 0 | 6 -> 6 | 4 -> 4 |
| S04 | 8886467122422 | celery seed | celery seed: recognised; paprika: recognised | 0 | 0 | 1 -> 1 | 4 -> 4 |
| S05 | 0769807238367 | coriander leaf | coriander leaves: NOT recognised; cumin seeds: NOT recognised | 0 | 0 | 7 -> 7 | None -> None |
| S06 | 0846203004878 | coriander leaf | coriander leaves: NOT recognised; coriander leaf: NOT recognised; coriander seed: recognised; cumin seed: recognised | 2 | 0 | 9 -> 7 | None -> None |
| S07 | 00002899 | coriander seed | coriander seeds: recognised; cumin seeds: NOT recognised; fenugreek seeds: NOT recognised | 1 | 0 | 8 -> 7 | None -> None |
| S08 | 00857462 | coriander seed | coriander seeds: recognised | 1 | 0 | 3 -> 2 | None -> None |
| S09 | 8906186410010 | dill seed | dill seeds: NOT recognised | 0 | 0 | 7 -> 7 | 4 -> 4 |
| S10 | 0797059265244 | oregano | oregano: recognised; paprika: recognised; thyme: recognised | 3 | 0 | 4 -> 1 | None -> None |
| S11 | 4007273656565 | oregano | basil: NOT recognised; oregano: recognised; parsley: NOT recognised | 1 | 0 | 8 -> 7 | None -> None |
| S12 | 0670087143015 | paprika | paprika: recognised | 1 | 0 | 6 -> 5 | 4 -> 4 |
| S13 | 3948537078321 | paprika | coriander leaves: NOT recognised; coriander seed: recognised; paprika: NOT recognised; parsley: inside another item | 1 | 0 | 9 -> 8 | 4 -> 4 |
| S14 | 12345678 | parsley | parsley: inside another item | 0 | 0 | 0 -> 0 | 4 -> 4 |
| S15 | 19015958 | parsley | parsley: recognised | 1 | 0 | 9 -> 8 | 4 -> 4 |
| S16 | 4012824401075 | peppermint | peppermint: NOT recognised | 0 | 0 | 10 -> 10 | None -> None |
| S17 | 4796001651513 | peppermint | peppermint: recognised | 1 | 0 | 5 -> 4 | 4 -> 4 |
| S18 | 5056517311714 | rosemary | rosemary: recognised; tarragon: recognised; thyme: recognised | 3 | 0 | 23 -> 20 | 4 -> 4 |
| S19 | 8801073142428 | rosemary | paprika: recognised; paprika: recognised; rosemary: recognised | 2 | 1 | 9 -> 8 | 4 -> 4 |
| S20 | 0876094106740 | saffron | saffron: recognised; saffron: recognised | 0 | 0 | 6 -> 6 | 4 -> 4 |
| S21 | 8901242204503 | saffron | saffron: recognised; saffron: recognised | 1 | 0 | 1 -> 0 | 4 -> 4 |
| S22 | 8908009059383 | sage | oregano: recognised; rosemary: recognised; sage: recognised; thyme: recognised | 4 | 0 | 9 -> 5 | 4 -> 4 |
| S23 | 0801541001439 | spearmint | spearmint: NOT recognised; cumin seed: NOT recognised | 0 | 0 | 10 -> 10 | 4 -> 4 |
| S24 | 6281036028877 | spearmint | parsley: recognised; spearmint: recognised; thyme: recognised | 3 | 0 | 11 -> 8 | 4 -> 4 |
| S25 | 8836473163230 | thyme | basil: recognised; oregano: recognised; thyme: recognised | 3 | 0 | 4 -> 1 | None -> None |
| S26 | 8906098831286 | thyme | parsley: recognised; rosemary: NOT recognised; thyme: NOT recognised | 1 | 0 | 7 -> 6 | 4 -> 4 |
| S27 | 8901552023450 | caraway seed | coriander leaves: NOT recognised; caraway seeds: NOT recognised | 0 | 0 | 12 -> 12 | None -> None |
| S28 | 8906076133289 | caraway seed | caraway seed: recognised | 1 | 0 | 6 -> 5 | 4 -> 4 |
| S29 | 0694642813311 | cumin seed | cumin seed: recognised | 1 | 0 | 6 -> 5 | None -> None |
| S30 | 0850015415975 | cumin seed | coriander seeds: recognised; coriander seeds: recognised; cumin seeds: NOT recognised; fenugreek seeds: NOT recognised | 2 | 0 | 19 -> 17 | 4 -> 4 |
| S31 | 00009891 | fenugreek seed | none found by pattern | 0 | 0 | 22 -> 22 | None -> None |
| S32 | 8901192215116 | fenugreek seed | fenugreek seeds: NOT recognised | 0 | 0 | 9 -> 9 | None -> None |
