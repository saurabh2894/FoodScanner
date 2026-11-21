# synonyms_2: synonyms application from the reviewed alias-1 set (PROPOSAL; ready for review, NOT merged)

Branch claude/synonyms-2 off main d27faee. Additions-only to `src/foodscan/resources/synonyms.csv`; lexicon.csv, markers.csv, the classifier and the JS port are untouched. Application is recognition routing to the canonical row only. Inputs (committed, with sha256 in the commit): `inputs/alias_candidates.csv` (antigravity/alias-1) and `inputs/03_alias_review_status.csv` (senior review, claude/junior-reviews-1). Builder: `scripts/alias_apply.py`; gate: `scripts/applied_gate.py --synonym-rows`.

## 1. Applied rows (23): one row-level table

| alias | target (canonical row) | target kind | pinpoint evidence (cached file + row) | alias == target in 12 forms | frozen 66 | out-of-sample 32 |
|---|---|---|---|---|---|---|
| sucrose | sugar | culinary | FoodData_Central_foundation_food_csv_2026-10-29.zip food_attribute.csv row 5581 (fdc_id 334247, Common Name 'sucrose') | 12/12 | 0 changes | OOS S24: group 4->4, status unchanged, unassessed item recognised |
| mandarin oranges | tangerines | fruit | FoodData_Central_sr_legacy_food_csv_2018-04.zip food.csv fdc_id 169105 description bracket | 12/12 | 0 changes | OOS S01: group None->None, status unchanged, unassessed item recognised |
| chinese gooseberry | kiwifruit | fruit | FoodData_Central_foundation_food_csv_2026-10-29.zip food_attribute.csv row 5579 (fdc_id 327046, Common Name 'Chinese gooseberry') | 12/12 | 0 changes | 0 changes |
| broccoli rabe | broccoli raab | vegetable | FoodData_Central_sr_legacy_food_csv_2018-04.zip food_attribute.csv row 2501 (fdc_id 170381, Common Name 'Broccoli rabe, Rapini') | 12/12 | 0 changes | 0 changes |
| rapini | broccoli raab | vegetable | FoodData_Central_sr_legacy_food_csv_2018-04.zip food_attribute.csv row 2501 (fdc_id 170381, Common Name 'Broccoli rabe, Rapini') | 12/12 | 0 changes | 0 changes |
| sunchokes | jerusalem-artichokes | vegetable | FoodData_Central_sr_legacy_food_csv_2018-04.zip food_attribute.csv row 2302 (fdc_id 169236, Common Name 'Sunchokes') | 12/12 | 0 changes | 0 changes |
| water spinach | water convolvulus | vegetable | FoodData_Central_sr_legacy_food_csv_2018-04.zip food_attribute.csv row 2305 (fdc_id 169301, Common Name 'kangkong, water spinach') | 12/12 | 0 changes | 0 changes |
| kangkong | water convolvulus | vegetable | FoodData_Central_sr_legacy_food_csv_2018-04.zip food_attribute.csv row 2305 (fdc_id 169301, Common Name 'kangkong, water spinach') | 12/12 | 0 changes | 0 changes |
| christophine | chayote | vegetable | FoodData_Central_sr_legacy_food_csv_2018-04.zip food_attribute.csv row 2505 (fdc_id 170402, Common Name 'christophine') | 12/12 | 0 changes | 0 changes |
| moth bean | mothbeans | legume | FoodData_Central_sr_legacy_food_csv_2018-04.zip food_attribute.csv row 2812 (fdc_id 172425, Common Name 'mat bean, moth bean') | 12/12 | 0 changes | 0 changes |
| mat bean | mothbeans | legume | FoodData_Central_sr_legacy_food_csv_2018-04.zip food_attribute.csv row 2812 (fdc_id 172425, Common Name 'mat bean, moth bean') | 12/12 | 0 changes | 0 changes |
| lychee | litchis | fruit | FoodData_Central_sr_legacy_food_csv_2018-04.zip food_attribute.csv row 2296 (fdc_id 169086, Common Name 'lychee') | 12/12 | 0 changes | 0 changes |
| horseradish tree pods | drumstick pods | vegetable | FoodData_Central_sr_legacy_food_csv_2018-04.zip food_attribute.csv row 2508 (fdc_id 170483, Common Name 'Horseradish tree pods') | 12/12 | 0 changes | 0 changes |
| sweetpotato leaves | sweet potato leaves | vegetable | FoodData_Central_sr_legacy_food_csv_2018-04.zip food_attribute.csv row 2307 (fdc_id 169303, Common Name 'Sweetpotato leaves') | 12/12 | 0 changes | 0 changes |
| portobello | portabella mushrooms | vegetable | FoodData_Central_sr_legacy_food_csv_2018-04.zip food_attribute.csv row 2303 (fdc_id 169243, Common Name 'Portobello') | 12/12 | 0 changes | 0 changes |
| portabello | portabella mushrooms | vegetable | FoodData_Central_sr_legacy_food_csv_2018-04.zip food_attribute.csv row 2304 (fdc_id 169255, Common Name 'Portabello') | 12/12 | 0 changes | 0 changes |
| portobella | portabella mushrooms | vegetable | FoodData_Central_sr_legacy_food_csv_2018-04.zip food_attribute.csv row 2313 (fdc_id 169377, Common Name 'portobella') | 12/12 | 0 changes | 0 changes |
| gai-lan | chinese broccoli | vegetable | FoodData_Central_sr_legacy_food_csv_2018-04.zip food_attribute.csv row 2315 (fdc_id 169404, Common Name 'gai-lan, kai-lan') | 12/12 | 0 changes | 0 changes |
| kai-lan | chinese broccoli | vegetable | FoodData_Central_sr_legacy_food_csv_2018-04.zip food_attribute.csv row 2315 (fdc_id 169404, Common Name 'gai-lan, kai-lan') | 12/12 | 0 changes | 0 changes |
| mamey colorado | mamey sapote | fruit | FoodData_Central_sr_legacy_food_csv_2018-04.zip food_attribute.csv row 2090 (fdc_id 167760, Common Name 'mamey colorado, marmalade plum') | 12/12 | 0 changes | 0 changes |
| marmalade plum | mamey sapote | fruit | FoodData_Central_sr_legacy_food_csv_2018-04.zip food_attribute.csv row 2090 (fdc_id 167760, Common Name 'mamey colorado, marmalade plum') | 12/12 | 0 changes | 0 changes |
| garlic pear | abiyuch | fruit | FoodData_Central_sr_legacy_food_csv_2018-04.zip food_attribute.csv row 2091 (fdc_id 167782, Common Name 'garlic pear') | 12/12 | 0 changes | 0 changes |
| pak choi | bok choy cabbage | vegetable | FoodData_Central_sr_legacy_food_csv_2018-04.zip food_attribute.csv row 2503 (fdc_id 170390, Common Name 'pak choi, bok choy') | 12/12 | 0 changes | 0 changes |

The 12 forms compared per alias (alias line vs target line, group and unassessed status): `X`, `salted X`, `X (sugar)`, `X (pickled)`, `X (canned)`, `X (XQ9)`, `X powder`, `100% X powder`, `Rice, X`, `X, salt`, `unsalted X`, `X (no added salt)`. 23 x 12 = 276 comparisons, 0 mismatches.

## 2. NOT applied (14), no synonyms entry

| alias | reason parked | stays unrecognised and unassessed (before and after) |
|---|---|---|
| badishep | partial evidence stays unverified | yes |
| chick peas | partial evidence stays unverified | yes |
| tumeric | quote unverified (host unreachable) | yes |
| chili | quote unverified (host unreachable) | yes |
| cane sugar | quote unverified (host unreachable) | yes |
| yellow cherries | held: generic phrase | yes |
| gingelly oil | NEEDS_EQUIVALENCE_EVIDENCE | yes |
| carom seeds | NEEDS_EQUIVALENCE_EVIDENCE | yes |
| desi ghee | NEEDS_EQUIVALENCE_EVIDENCE | yes |
| maida | NEEDS_EQUIVALENCE_EVIDENCE | yes |
| cassia | NEEDS_EQUIVALENCE_EVIDENCE | yes |
| cassia whole | NEEDS_EQUIVALENCE_EVIDENCE | yes |
| refined palmolien oil | AMBIGUOUS | yes |
| bok choy | EXCLUDED BY THE GATE: the alias is a word-prefix of its own target ('bok choy' -> 'bok choy cabbage'); the synonym engine rewrites 'bok choy cabbage' to 'bok choy cabbage cabbage' and the canonical row stops being recognised (drift 1 -> abstain). Evidence is sound; needs a mechanism decision | yes |

`bok choy` is the one row dropped by the GATE from the owner's 24: the synonym engine rewrites the alias inside the canonical row's own name ('bok choy cabbage' becomes 'bok choy cabbage cabbage' and stops being recognised, drift 1 -> abstain). Its evidence is sound (FDC 170390 Common Name 'pak choi, bok choy'); `pak choi` is applied and routes to `bok choy cabbage`. Re-adding `bok choy` needs a mechanism decision (a lexicon row for the bare word, or an engine rule), which is a code/lexicon change outside this batch.

## 3. Applied-gate evidence (committed branch; BEFORE = worktree of main d27faee, AFTER = this branch; separate fresh processes)

| check | result |
|---|---|
| synonyms.csv | additions-only: 127 -> 150 lines, base lines kept in order True, 23 rows added, from-set equals the 23 expected True |
| lexicon.csv / markers.csv | byte-identical to main (True / True) |
| after-build proof | 23 of 23 aliases recognised after and not before |
| frozen 66 | changed 0, group changes 0, status changes 0, unexplained 0, abstain->4 0 |
| out-of-sample 32 | changed 2 (S01: 'mandarin oranges' recognised; S24: 'Sucrose' recognised), group changes 0, status changes 0, unexplained 0, abstain->4 0 |
| drift (existing lexicon terms and synonyms, 510 probes) | 0 differences |
| powder surface (552 forms) | changed 0; bare X powder Group 1 after 0 |
| controls | 24 negative (the 14 parked aliases plus 10 conditioned forms) and 26 positive in `applied_gate.json` 'controls' |
| suite | 1491 passed, 5 xfailed |
| parity | 641/641 identical (additions-only: +38 inputs over 603, 0 lines removed) |

## 4. Notes
- `portobello` and `portobella` cite Common Name attributes of the grilled portabella records (FDC 169243, 169377): name evidence for the canonical raw row; the placement is the canonical row's.
- `sucrose` -> `sugar` is Group 2 (culinary); `mandarin oranges` -> `tangerines` rests on the FDC description bracket (no Common Name attribute exists on 169105).
- One existing test (`tests/test_class_bulk_1.py`) asserted that no Batch-1 synonym candidate was in synonyms.csv; it now allows the two (`moth bean`, `mat bean`) that this batch applies, with an explanation.

