# nut_guard_1: canned/brine/unrecognised-bracket guards for kind nut_seed (PROPOSAL; merge stops with the owner)

Branch claude/nut-guard-1 off main 46ad81c. Decision reference: owner decision 2026-11-21 (extend the existing guards to `nut_seed` as a separate small engine batch after the class-bulk-5 merge).

## 1. Change
`classify.py` (mirrored in `foodscan.js`): new `_GUARDED_KINDS = _BRINE_KINDS + ("nut_seed",)`, used in the three places that carry the legume/vegetable/fruit guards: (1) the unrecognised-bracket abstention, (2) salt/sugar/brine/culinary-substance-in-bracket -> Group 3, (3) canned/bottled/preserved without stated salt, sugar or brine -> abstain. No lexicon, synonym, marker, descriptor or powder change; reason texts are corrected (owner review): see section 1a.
Source: no new source. FAO 2019 Table 1 Group 3 definition "Products made by adding salt, oil, sugar or other group 2 ingredients to group 1 foods, using preservation methods such as canning and bottling" and the example "salted or sugared nuts and seeds" (already quoted in evaluation/per_form_2a/README.md, Q3 and Q6). Inference level: class-instance of the rule already applied to the other kinds; same item-level reading (the item's own name and bracket).

## 1a. Reason texts (owner correction: a nut is not called a legume, vegetable or fruit)
| case | text |
|---|---|
| nut/seed items only, canned/bottled/preserved | "a canned, bottled or preserved nut or seed (...): the FAO Group 3 definition covers group 1 foods with salt, oil, sugar or other group 2 ingredients added, using preservation methods such as canning and bottling, but the item does not say that any such substance is added, so added substances are not established and neither Group 1 nor Group 3 is established" (the general definition; no example is cited, since no FAO example names a canned nut) |
| nut/seed items only, unrecognised bracket | "a bracket on a nut or seed item names content the vocabulary does not recognise (...), so neither Group 1 nor Group 3 is established while part of the item is unassessed" |
| a list mixing nut and other flagged items | kind-neutral: "a canned, bottled or preserved food (...)" / "a bracket on a food item names ..." with the same explanations |
| non-nut cases | the original text, byte-for-byte unchanged (pinned by a test against the pre-change string) |
Group 3 for brine, oil, salt and sugar keeps the existing drivers ('nut or seed with added salt or sugar'); the oil-in-bracket Group 3 rests on the general Group 1-plus-oil definition, class-instance only, no new source claim. Text changes are confined to nut cases: frozen 66 and out-of-sample 32 show no reason change.

## 1b. Group 3 drivers (owner review: name the observed substance)
| case | driver |
|---|---|
| salted X, X (salted), X (sugar), X, salt | "nut or seed with added salt or sugar (FAO Table 1 Group 3: 'salted or sugared nuts and seeds')" (the example fits; unchanged) |
| X (brine) | "nut or seed with added brine (FAO Table 1 Group 3 definition: 'Products made by adding salt, oil, sugar or other group 2 ingredients to group 1 foods'; class-instance of that rule, no FAO example names this form)" |
| X (sunflower oil) | same text with "added sunflower oil"; a recognised culinary substance in the item's own bracket is named as observed |
| X (honey), X (salt, sunflower oil) | observed substances listed ("added honey"; "added salt, sunflower oil") under the general definition |
Pinned by explicit driver assertions in `tests/test_nut_guard_1.py`; Python and JS mirror the same helper.

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
| suite | 1749 passed, 5 xfailed |
| parity | 760/760 identical (additions-only, +22 inputs; reason and driver text are compared) |

## 4. Consequences and decisions for the owner
1. `X (sunflower oil)` (a recognised culinary substance in the item's own bracket) now takes Group 3, as for the other kinds (Group 3 definition: adding oil to a group 1 food). The alternative is an abstain for nuts; one condition in `legume_added_salt_sugar_or_brine` decides it.
2. `X (skin removed)` now abstains: 'removed' is not a recognised bracket word (the same for 'almonds (blanched)'-style notes on legumes and vegetables). Skin or shell removal is an FAO-listed minimal process; adding 'removed', 'shelled', 'skinned' to the benign bracket words would need a source-cited decision and is not done here.
3. Observed, not changed: `X powder` for nut_seed rows (e.g. `chia seeds powder`, `almonds powder`) answers Group 1 because `nut_seed` is not in `_POWDER_ROUTED`, unlike whole_food, legume, vegetable and fruit under the powder standard. This predates the class-bulk-5 batch (it holds for almonds on main) but now covers 23 rows. Decision: route nut_seed powders under the same standard (abstain unless the item states '100%' or 'whole').

## 5. Exact diff vs main 46ad81c
`data/ingest/nut_guard_1.json`, `evaluation/nut_guard_1/{README.md,applied_gate/applied_gate.json}`, `scripts/parity_check.py` (+22 inputs), `src/foodscan/classify.py`, `tests/test_nut_guard_1.py` (new), `web_preview/foodscan.js`.
