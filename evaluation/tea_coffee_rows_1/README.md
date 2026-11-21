# tea_coffee_rows_1: two whole_food rows, tea and coffee (PROPOSAL; staging only, merge stops with the owner)

Branch claude/tea-coffee-rows-1 (off main cf06f63; main 0810267, with the whole-food guard and the dairy rows, merged in, no rebase). Input: junior branch antigravity/class-bulk-8-beverages (615b99d), senior review `evaluation/junior_reviews_5/08_beverages_review.md` (claude/junior-reviews-5, 7d7c3f8). Decision reference: owner instruction 2026-11-21 (stage exactly tea and coffee as whole_food; water unchanged).

## 1. Rows (text in the lexicon `source` column; `staged_rows.csv`)
| term | clause (FAO 2019 ca5644en Table 1 Group 1 example, p.11, verified verbatim; the table cell breaks the line after "coffee,") | FDC records (names only; brewed drinks, not the label ingredient) | inference level |
|---|---|---|---|
| tea | "tea, coffee, and drinking water" | sr_legacy 171917, 173227, 174120, 174155 (brewed green, black, oolong, black with distilled water) | exact-named (the ingredient term is named by the clause) |
| coffee | same | sr_legacy 171881, 171890, 171891 (brewed breakfast blend, brewed with tap water, brewed espresso) | exact-named |
Used only the verified example. Not used: the junior's spliced 'Group 1 definition', any 'pure' or purity claim, brand records. Not staged and not changed: `water` (existing `neutral` row), ready-to-drink and brand records (held), instant, decaf, extract, leaves/beans, black and oolong tea, espresso, other aliases, herbal infusions, coffee substitutes, juices, alcoholic drinks. Kind `whole_food` (existing), not `neutral`: see the review (neutral would drop tea and coffee from classification and from combinations).

## 2. Gates (committed tree vs main 0810267; separate fresh processes)
| check | result |
|---|---|
| lexicon | 411 -> 413 (+2 whole_food rows; none changed or removed); synonyms.csv, markers.csv byte-identical; no source file changed |
| frozen 66 / out-of-sample 32 | changed 0 / 0; unexplained 0; abstain->4 0 |
| drift (561) | 0 differences |
| salted (162) / descriptor (822) / powder (573) surfaces | 0 changed |
| after-build proof | both rows recognised after, neither before |
| suite | **1884 passed, 5 xfailed** (main 1833 + 51 new tests; earlier 1861 is stale) |
| parity | **816/816** identical (main 801 + 15 added entries, 0 removed; reason and driver compared; earlier 804 is stale) |

## 3. Measured forms (tea and coffee identical; before = unrecognised; `applied_gate.json` controls; the whole-food guard is in the base)
| form | group | form | group |
|---|---|---|---|
| X; roasted X; green X; unsalted X; 100% X powder | 1 | X, sugar; sugar, X; X, salt; X, milk solids, sugar | 3 |
| X, flavour; X, natural flavour; X, maltodextrin; X, colour (INS 150d) | 4 | X, milk; X, water; water, X; X, tea; X, coffee; tea, coffee | abstain |
| X (sugar); X (milk); X (egg); X (rice); X (XQ9); X (chicory) | abstain | salted X; X (salted); X (canned); X (brine); X (sunflower oil) | abstain |
| instant X; decaffeinated X; X extract; X powder; flavoured X; X (flavoured); ready to drink X; iced X; black X; X leaves; X beans; herbal X | abstain (unrecognised or no rule) | X, acidity regulator (INS 330) | abstain |
Other beverages and held aliases stay unrecognised: hibiscus tea, chamomile tea, black tea, oolong tea, espresso, instant coffee, decaf coffee, coffee beans, tea leaves, tea extract, coffee substitute, chicory, cocoa, drinking water, bottled water, juice, cola. `Coffee (Chicory)` abstains (unknown bracket).

## 4. Explained results and holes
1. **Widened hole closed by the guard (measured before it merged, on main cf06f63):** without the whole-food guard `Tea (sugar)`, `Tea (milk)`, `Tea (egg)`, `Tea (rice)`, `Salted Tea`, `Tea (canned)`, `Tea (brine)` and `Tea (sunflower oil)` answered Group 1 (same for coffee). With the guard in the base all abstain. This proposal therefore must not merge before the guard; it is merged now, so the dependency is satisfied.
2. `Green Tea` answers Group 1 and `Black Tea` does not: 'green' is a global descriptor, so `Green Tea` resolves to the row `tea` through it; no alias was added. Reported as an accident of the descriptor, correct in outcome; `Black Tea`, `Oolong Tea` stay held.
3. `100% Tea Powder` and `100% Coffee Powder` answer Group 1 under the powder standard (composition stated); the bare `X powder` abstains; no instant or extract form is recognised.
4. `Tea, Coffee` abstains (the list combination rule); `Tea, Milk` abstains.
5. The FDC evidence is for brewed beverages; the row asserts only the ingredient term named by the clause.

## 5. Tests
`tests/test_tea_coffee_rows_1.py` (new): plain forms, sugar/salt/flavour lists, milk and unknown-bracket abstentions, held forms and aliases, conditioned and nested forms (through the guard), the green-descriptor observation, and row provenance (verified clause, no spliced definition, no purity claim).

## 6. Exact diff vs main 0810267 (7 paths, from `git diff --name-only main HEAD` on the committed merge tree)
- `data/ingest/tea_coffee_rows_1.json`
- `evaluation/tea_coffee_rows_1/README.md`
- `evaluation/tea_coffee_rows_1/applied_gate/applied_gate.json`
- `evaluation/tea_coffee_rows_1/staged_rows.csv`
- `scripts/parity_check.py`
- `src/foodscan/resources/lexicon.csv`
- `tests/test_tea_coffee_rows_1.py`
