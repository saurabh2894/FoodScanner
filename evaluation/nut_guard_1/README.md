# nut_guard_1: canned/brine/unrecognised-bracket guards for kind nut_seed (PROPOSAL; merge stops with the owner)

Branch claude/nut-guard-1 off main 46ad81c. Decision reference: owner decision 2026-11-21 (extend the existing guards to `nut_seed` as a separate small engine batch after the class-bulk-5 merge).

## 1. Change
`classify.py` (mirrored in `foodscan.js`): new `_GUARDED_KINDS = _BRINE_KINDS + ("nut_seed",)`, used in the three places that carry the legume/vegetable/fruit guards: (1) the unrecognised-bracket abstention, (2) salt/sugar/brine/culinary-substance-in-bracket -> Group 3, (3) canned/bottled/preserved without stated salt, sugar or brine -> abstain. No lexicon, synonym, marker, descriptor or powder change; reason texts are unchanged (they still say 'legume, vegetable or fruit'; unchanged so existing text checks and parity hold).
Source: no new source. FAO 2019 Table 1 Group 3 definition "Products made by adding salt, oil, sugar or other group 2 ingredients to group 1 foods, using preservation methods such as canning and bottling" and the example "salted or sugared nuts and seeds" (already quoted in evaluation/per_form_2a/README.md, Q3 and Q6). Inference level: class-instance of the rule already applied to the other kinds; same item-level reading (the item's own name and bracket).

## 2. Measurement: all 23 nut_seed rows (3 existing: almonds, pumpkin seeds, flax seeds; 20 from class-bulk-5), before (main) -> after; identical for every row
| form | before -> after | form | before -> after |
|---|---|---|---|
| X, roasted X, X (raw/whole/dried/peeled/cooked/no added salt) | 1 -> 1 | X (canned) / (bottled) / (preserved) | 1 -> abstain |
| salted X, X (salted), X, salt, X (sugar) | 3 -> 3 | X (XQ9) | 1 -> abstain |
| X (brine), X (in brine) | 1 -> 3 | X (skin removed) | 1 -> abstain |
| X (sunflower oil) | 1 -> 3 | | |

Controls on other kinds (`kidney beans (canned)`, `rice (XQ9)`, `mango (preserved)`) abstain before and after.

## 3. Gates (committed tree vs main 46ad81c; separate fresh processes)
| check | result |
|---|---|
| lexicon / synonyms / markers / descriptors | 406 -> 406, no row changed; synonyms.csv and markers.csv byte-identical |
| frozen 66 / out-of-sample 32 | changed 0 / 0; unexplained 0; abstain->4 0 |
| drift (556 terms/synonyms) | 0 differences |
| salted (147) / descriptor (812, includes the 20 nut rows) / powder (558) surfaces | 0 changed |
| suite | 1745 passed, 5 xfailed |
| parity | 750/750 identical (additions-only, +12 inputs) |

## 4. Consequences and decisions for the owner
1. `X (sunflower oil)` (a recognised culinary substance in the item's own bracket) now takes Group 3, as for the other kinds (Group 3 definition: adding oil to a group 1 food). The alternative is an abstain for nuts; one condition in `legume_added_salt_sugar_or_brine` decides it.
2. `X (skin removed)` now abstains: 'removed' is not a recognised bracket word (the same for 'almonds (blanched)'-style notes on legumes and vegetables). Skin or shell removal is an FAO-listed minimal process; adding 'removed', 'shelled', 'skinned' to the benign bracket words would need a source-cited decision and is not done here.
3. Observed, not changed: `X powder` for nut_seed rows (e.g. `chia seeds powder`, `almonds powder`) answers Group 1 because `nut_seed` is not in `_POWDER_ROUTED`, unlike whole_food, legume, vegetable and fruit under the powder standard. This predates the class-bulk-5 batch (it holds for almonds on main) but now covers 23 rows. Decision: route nut_seed powders under the same standard (abstain unless the item states '100%' or 'whole').

## 5. Exact diff vs main 46ad81c
`data/ingest/nut_guard_1.json`, `evaluation/nut_guard_1/{README.md,applied_gate/applied_gate.json}`, `scripts/parity_check.py` (+12 inputs), `src/foodscan/classify.py`, `tests/test_nut_guard_1.py` (new), `web_preview/foodscan.js`.
