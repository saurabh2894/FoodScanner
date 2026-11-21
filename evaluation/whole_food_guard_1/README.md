# whole_food_guard_1: conservative condition and nested-food abstentions for kind whole_food (PROPOSAL; merge stops with the owner)

Branch claude/whole-food-guard-1 off main cf06f63. Decision reference: owner instruction 2026-11-21 (scoped conservative proposal; the dairy-rows-1 integration waits on this review). Abstention only: no Group 3 is asserted for salted or sugared milk or eggs, and no new group appears anywhere.

## 1. Change (`classify.py`, mirrored in `foodscan.js`; `whole_food_condition`, `whole_food_nested`)
1. **Own-text condition.** A recognised `whole_food` item whose OWN name or bracket carries salt, salted, sugar, sugared, sweetened, honey, syrup, jaggery, glazed, candied, brine, a recognised culinary substance (an oil) in its bracket, or a canned/bottled/preserved/pickled word abstains: "an item whose own text carries added salt, sugar, brine, oil or a canned, bottled or preserved form (...): the food is recognised, but no source read states whether that addition moves this food out of Group 1, so neither Group 1 nor Group 3 is established". Negations ('unsalted', 'no added salt') keep Group 1. The 23 grain/flour terms whose salted form already answers Group 3 (per-form-2a) are excluded from this guard for salt; for those terms sugar, oil, brine or preserved words now abstain.
2. **Distinct nested food.** A recognised food in the item's own bracket whose class differs from the head's (classes: dairy = a term containing 'milk', plus dahi; egg = a term ending 'egg' or 'eggs'; plant = the rest) abstains: "a bracket names a different kind of food inside the item (...): what the item is made of is not established, ...". Same-class parts stay supported (`Milk (Buffalo Milk)`, `Milk (Cow Milk)`, `Eggs (Egg)`, `Rice (Rice)`, `Dehydrated Vegetable (Onion)`). Neutral, culture and culinary parts are not treated as nested foods (culinary parts fall under 1). Classes are read from the term, so rows added later (sheep milk, duck eggs) join the right class without a constant.
3. Existing species rule unchanged: `Rice (Buffalo Milk)` keeps its earlier abstention and reason text. Existing-kind reason texts are unchanged; the two new texts apply only to whole_food items that previously answered Group 1.

Source: none beyond the Group 3 definition already quoted elsewhere; the rule is deliberately an abstention ("not established"), not a placement. Inference level: not applicable (no group is derived).

## 2. Gates (committed tree vs main cf06f63; separate fresh processes)
| check | result |
|---|---|
| lexicon / synonyms / markers / descriptors | 406 -> 406, nothing changed; synonyms.csv, markers.csv byte-identical |
| frozen 66 / out-of-sample 32 | changed 0 / 0 (no label holds one of these forms); unexplained 0; abstain->4 0 |
| drift (556) | 0 differences |
| descriptor (812) / powder (558) surfaces | 0 changed |
| salted surface (49 base rows, 147 forms) | 46 changed, all Group 1 -> abstain, none to Group 1 or 3: see section 3 |
| suite | 1787 passed, 5 xfailed (two assertions updated, see section 4) |
| parity | 778/778 identical (additions-only, +18 inputs; reason text compared) |

## 3. Attributed behaviour changes (30 whole_food rows x 24 forms, `applied_gate.json` controls; before -> after)
| form | change |
|---|---|
| X | 1 -> 1 (all 30) |
| salted X / X (salted) | 7 stay Group 3 (the 23-term grain guard rows in the list: rice, barley, millet, black rice, buckwheat, sorghum, wild rice); 23 go 1 -> abstain (milk family, eggs, dahi, yeast, roasted gram, dehydrated vegetable, ragi, oat, wheat, maize, corn, jowar, bajra, foxtail/pearl millet, quinoa) |
| X (sugar), X (sunflower oil), X (canned), X (brine), X (preserved) | 1 -> abstain (all 30) |
| X, salt / X, sugar / X, sunflower oil (list form) | 3 -> 3 (unchanged: list-level combination rule) |
| roasted X, unsalted X, X (no added salt), X (pasteurized), X (raw) | 1 -> 1 |
| X powder / 100% X powder | unchanged (powder routing untouched) |
| X (XQ9), sugared X | abstain -> abstain |
| X (egg) | 1 -> abstain for 28 (not for egg, eggs) |
| X (rice) | 1 -> abstain for 10 (milk, toned milk, double toned milk, buffalo milk, cow milk, goat milk, milk solids, dahi, egg, eggs) |
| X (cow milk) / X (buffalo milk) | unchanged: Group 1 for the six milk-class heads, abstain elsewhere (as before) |
Salted surface: the 42 base-row changes are exactly the former 'Salted Milk'/'Salted Egg'-type Group 1 answers on non-scoped whole_food rows, `salted X` and `roasted salted X` (the 2a measurement 141/42/0 on main); +4 for cow milk and goat milk. Flour rows (e.g. refined wheat flour, potato flour) are outside this scope and still answer Group 1 when salted.

## 4. Tests updated (explained, none weakened)
`tests/test_salted_grain_guard.py`: 'Salted Milk' and 'Salted Egg' were expected Group 1 ("measured-unchanged, parked"); they are now expected to abstain (the parked decision is unchanged: no Group 3 is asserted). New `tests/test_whole_food_guard_1.py` covers added-substance forms, nested foods, supported same-food/species brackets, lists, negations and other kinds.

## 5. Explanation fit and open items
- Nested-food abstentions no longer use the 'vocabulary does not recognise' wording for foods the vocabulary does recognise.
- The condition text is generic across salt, sugar, brine, oil and preserved forms; it says only that no source read states the effect for this food.
- Not changed: flour, legume, vegetable, fruit and nut kinds; powder routing; synonyms; the parked `Salted Milk`/`Salted Egg` Group 3 decision; extending the salted-grain guard to grain rows outside the 23 terms (they now abstain when salted instead of answering Group 1).
- Effect on the held dairy proposal: with this guard the five new rows would abstain on salted, sugared, canned, brined, oiled and distinct-food-bracket forms (they inherit the class rule through their term words).

## 6. Exact diff vs main cf06f63
`data/ingest/whole_food_guard_1.json`, `evaluation/whole_food_guard_1/{README.md,applied_gate/applied_gate.json}`, `scripts/parity_check.py` (+18 inputs), `src/foodscan/classify.py`, `tests/test_salted_grain_guard.py` (two expectations), `tests/test_whole_food_guard_1.py` (new), `web_preview/foodscan.js`.
