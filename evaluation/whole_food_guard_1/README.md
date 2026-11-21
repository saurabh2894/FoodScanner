# whole_food_guard_1: conservative condition and nested-food abstentions for kind whole_food (PROPOSAL, revision 2; merge stops with the owner)

Branch claude/whole-food-guard-1 off main cf06f63. Decision reference: owner review 2026-11-21 of b2f8360 (three corrections). Abstention only: no Group 3 is asserted for salted or sugared milk or eggs, and no new group appears anywhere.

## 1. Change (`classify.py`, mirrored in `foodscan.js`: `whole_food_observed`, `whole_food_nested`)
1. **Own-text condition, observed condition named.** A recognised `whole_food` item whose OWN name or bracket names salt, sugar, honey, syrup, jaggery, glazed, candied, brine, a recognised culinary substance (an oil) or a canned/bottled/preserved/pickled form abstains. The reason lists the observed condition: "an item whose own text names an added or preserving condition (Milk (sugar): sugar): the general Group 3 definition covers group 1 foods with salt, oil, sugar or other group 2 ingredients added, but this food's form and composition are not established by the label evidence and the rules available, so neither Group 1 nor Group 3 is asserted". It does not deny the general source; it says what the label evidence leaves open. Negations ('unsalted', 'no added salt') keep Group 1.
2. **Exemption narrowed to the supported condition.** For the 23 grain/flour terms of per-form-2a, only SALT (and salt-named culinary parts) is exempt and keeps its Group 3. Any other observed condition on such an item abstains. Corrected from b2f8360, where the whole condition was bypassed.
3. **Nested food: explicit equivalences, no taxonomy.** A recognised food in the item's own bracket abstains unless it is explicitly the same food: the identical row (descriptor-resolved parts included: `Rice (Brown Rice)`); egg with eggs; a plain milk row (milk, toned milk, double toned milk, buffalo milk, cow milk, goat milk) with milk, cow milk, buffalo milk or goat milk (the species-milk brackets of per-form-1 and per-form-2b); milk solids with the plain milk they are made from (frozen label b3/Q04 'Milk solids (Toned Milk) & Active Culture'; the `Milk solids (... cow milk)` Q10 abstention is unchanged, it comes from the earlier species rule); and the class-phrase row `dehydrated vegetable` with a vegetable row (its row source names dried vegetables as a class). Everything else is a different food, including two different plants (`Rice (Wheat)`), a plant and a nut (`Rice (Walnuts)`), a milk fraction inside milk (`Milk (Milk Solids)`), `Milk (Toned Milk)`, `Dehydrated Vegetable (Peas)` (a legume row), and any future meat or other row. Neutral, culture and culinary parts are not nested foods (culinary parts fall under 1). Reason: "a bracket names a different food inside the item (...): no rule or source available here establishes that it is the same food or how the two combine, so what the item is made of is not established and neither Group 1 nor Group 3 is asserted".
4. Existing species rule and existing-kind reason texts are unchanged (`Rice (Buffalo Milk)` keeps its earlier text).

## 2. Gates (committed tree vs main cf06f63; separate fresh processes)
| check | result |
|---|---|
| lexicon / synonyms / markers / descriptors | 406 -> 406, nothing changed; synonyms.csv, markers.csv byte-identical |
| frozen 66 / out-of-sample 32 | changed 0 / 0; unexplained 0; abstain->4 0 (b3/Q04 stays Group 1 through the milk-solids equivalence) |
| drift (556) | 0 differences |
| descriptor (812) / powder (558) surfaces | 0 changed |
| salted surface (49 base rows, 147 forms) | 46 changed, all Group 1 -> abstain, none to Group 1 or 3 |
| overlay (this branch + the five held dairy rows, `overlay_dairy_gate/`) | frozen 66 / OOS 32 changed 0, drift 0, surfaces unchanged; new-row forms below |
| suite | 1807 passed, 5 xfailed (two assertions updated, section 4) |
| parity | 778/778 identical (additions-only, +29 inputs; reason text compared) |

## 3. Measured behaviour (30 whole_food rows x 34 forms; `applied_gate.json` controls; before -> after)
| form | change |
|---|---|
| X; roasted X; unsalted X; X (no added salt); X (pasteurized); X (raw) | 1 -> 1 (all 30) |
| salted X / X (salted) | 7 scoped grain rows stay Group 3; 23 go 1 -> abstain (milk family, eggs, dahi, yeast, roasted gram, dehydrated vegetable, ragi, oat, wheat, maize, corn, jowar, bajra, foxtail/pearl millet, quinoa) |
| X (salt) | same split: 7 stay 3, 23 go 1 -> abstain |
| X (salt, sunflower oil) / X (salt, sugar) / salted X (canned) / salted X (brine) | scoped grains 3 -> abstain (7); other rows 1 -> abstain (23) |
| X (sugar), X (sunflower oil), X (canned), X (brine), X (preserved) | 1 -> abstain (all 30) |
| X, salt / X, sugar / X, sunflower oil (lists) | 3 -> 3 (list-level rule untouched) |
| X powder / 100% X powder | unchanged |
| X (XQ9); sugared X | abstain -> abstain |
| X (wheat) / X (walnuts) | 1 -> abstain for 29 and 30 (`wheat (wheat)` stays: identical row) |
| X (milk solids) | 1 -> abstain for 29 (`milk solids (milk solids)` stays) |
| X (toned milk) | 1 -> abstain for 28; `toned milk (toned milk)` (identical row) and `milk solids (toned milk)` (source milk) stay |
| X (milk) | 7 stay 1 (milk family and milk solids), 23 go 1 -> abstain |
| X (egg) | 28 go 1 -> abstain; egg and eggs stay |
| X (rice) | 29 go 1 -> abstain; `rice (rice)` stays |
| X (cow milk) / X (buffalo milk) | unchanged: Group 1 for the six plain-milk heads, abstain elsewhere |
Salted surface: the 42 base-row changes are the former `Salted Milk`/`Salted Egg`-type Group 1 answers on non-scoped whole_food rows (`salted X`, `roasted salted X`), +4 for cow milk and goat milk. Flour rows are outside scope and still answer Group 1 when salted.

**Overlay with the five held dairy rows (sheep milk, duck, goose, quail, turkey eggs):** plain X 1; roasted/dry roasted/unsalted/(no added salt) 1; salted, roasted salted, X (sugar), X (canned), X (XQ9), X powder, sugared X, toasted forms: abstain; X, salt: 3; 100% X powder 1; whole X powder 1 for the four egg rows. Reported exceptions (no listed equivalence, so they abstain): `Milk (Sheep Milk)`, `Eggs (Duck Eggs)`, `Duck Eggs (Eggs)`, `Sheep Milk (Milk)`; `Sheep Milk (Sheep Milk)` and `Duck Eggs (Duck Eggs)` stay Group 1 (identical row). No constant is changed for the new rows: the species equivalences stay an explicit decision for the dairy batch.

## 4. Tests (explained, none weakened)
`tests/test_salted_grain_guard.py`: 'Salted Milk' and 'Salted Egg' now expect abstain (were Group 1, 'measured-unchanged, parked'). `tests/test_whole_food_guard_1.py` (new, 70+ cases): added-substance forms, observed-condition reasons, scoped-grain salt exemption (Rice (salt, sunflower oil), Salted Rice (canned), Rice (salt, sugar), Salted Buckwheat (brine) abstain; Salted Rice, Rice (Rice, Salt), Salted Buckwheat, Salted Wheat Flour keep 3), distinct-food controls (Rice (Wheat), Rice (Walnuts), Milk (Milk Solids), Milk (Toned Milk), Dehydrated Vegetable (Peas)), supported brackets, and a subprocess overlay test that appends the five dairy rows to a copy of the lexicon.

## 5. Explanation fit and open items
- Nested-food abstentions never use the 'vocabulary does not recognise' wording for foods the vocabulary does recognise.
- The condition reason names the observed condition and cites the general definition; it asserts no group.
- Not changed: flour, legume, vegetable, fruit and nut kinds; powder routing; synonyms; the parked `Salted Milk`/`Salted Egg` Group 3 decision; the grain guard's scope (non-scoped grain rows now abstain when salted).
- Equivalence exceptions to decide later: `Milk (Toned Milk)` and other plain-milk cross-brackets abstain here (no source read equates them); `Dehydrated Vegetable` covers vegetable-kind parts only (peas, a legume row, abstain).

## 6. Exact diff vs main cf06f63
`data/ingest/whole_food_guard_1.json`, `evaluation/whole_food_guard_1/{README.md,applied_gate/applied_gate.json,overlay_dairy_gate/applied_gate.json}`, `scripts/parity_check.py` (+29 inputs), `src/foodscan/classify.py`, `tests/test_salted_grain_guard.py` (two expectations), `tests/test_whole_food_guard_1.py` (new), `web_preview/foodscan.js`.
