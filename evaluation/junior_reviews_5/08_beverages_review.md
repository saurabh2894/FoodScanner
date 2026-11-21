# Senior review: antigravity/class-bulk-8-beverages (FDC 'Beverages' plain forms); docs only, no staging

Reviewed head 615b99d (one commit on stated base cecccb9). Decision reference: owner instruction 2026-11-21 (review only; no staging until verified).

## 0. Boundary check
| check | result |
|---|---|
| merge-base with stated base (STATUS.md `base=cecccb9cb951...`) | cecccb9 (equal); one commit |
| `git diff --name-status cecccb9...615b99d` | 6 paths, all status A, all under `evaluation/class_bulk_8_beverages_1/`; no path outside the folder |
| `accept_records.csv` sha256 (raw blob bytes, 7114 bytes) | `a2b8305aeb84a7039e331076cfaa94f1e886ea167ad6cccee792d20eca03c133`; equals the pin |
| classification verdicts / kinds | the CSVs carry candidate dispositions and a `suggested_kind` (`neutral`); no repository file is changed. The kind is reviewed in section 3 |

## 1. Counts reproduced
370 candidates = 22 accept / 34 queue / 314 reject (366 SR Legacy + 4 Foundation), equal key for key to the cached FDC category 'Beverages'; no duplicates, none missing or extra; 370/370 names equal the raw FDC descriptions; queue and reject reason counts match the junior README. Accept split: 3 canonical = `water` (12 records; already a row, kind neutral) + `tea` (7) + `coffee` (3).

## 2. Quotes (FAO ca5644en)
- **Pass, verbatim:** the Group 1 example "tea, coffee, and drinking water" (the table cell breaks the line after 'coffee,'); "Spring and tap water."; the Group 4 example list ('carbonated soft drinks', "'energy' drinks; milk drinks, 'fruit' yoghurts and 'fruit' drinks; 'cocoa' drinks", with ellipses).
- **Fail: the 'Verbatim Group 1 Definition Clause (Table 1, p. 11)' is a splice, not a quotation.** Its first sentence ("Unprocessed (or natural) foods are the edible parts of plants (such as fruit, leaves, stems, seeds, roots) or from animals (such as muscle, offal, eggs, milk), and also fungi, algae and water, after separation from nature.") is verbatim from the section-2 prose of the report, not from Table 1 (whose Group 1 cell reads "Edible parts of plants (fruit, seeds, leaves, stems, roots, tubers) or of or from animals (muscle, fat, offal, eggs, milk), and also fungi, algae, all after separation from nature. Spring and tap water."). The junior then joins "Spring and tap water." (Table 1) and a second sentence that mixes the prose wording ("Minimally processed foods are natural foods altered by ...") with the Table 1 process list. The result matches no page. Correct locators for water: section-2 prose 'and also fungi, algae and water, after separation from nature' (verbatim, a prose clause) and Table 1 'Spring and tap water' and 'drinking water'.
No accepted record needs the failed quote: every accept row also cites the passing example "tea, coffee, and drinking water".

## 3. Findings
1. **Kind 'neutral' is not supported for tea and coffee.** `neutral` rows carry no processing signal and are dropped from classification (measured on main: `water` alone and `water, sugar` both abstain; a neutral item contributes nothing to a list). Tea and coffee are named in the Group 1 examples as foods; as `neutral` a list such as 'Tea, Sugar' would lose its Group 1 food and could read as a lone culinary ingredient. The kind to propose is the existing `whole_food` (a plain sole item answers Group 1, food plus sugar is Group 3, an unknown bracket abstains). The junior preserved both options without a recommendation consistent with the clause; no kind is invented either way. Water stays as is.
2. **Plain-form evidence is for prepared beverages, not for the ingredient.** All FDC records are brewed or ready-to-drink drinks. The ingredient term ('tea', 'coffee') is named by the clause; the FDC names serve only as naming. The junior's 'pure brewed X' and brand composition claims (EVIAN 'natural mineral spring water', DASANI and AQUAFINA 'purified drinking water', 'natural alpine spring water') are not in any FDC name and are unsupported; they matter only as evidence for the existing water row and are not relied on.
3. **Ready-to-drink records are split.** Three RTD records are accepted (171911 and 171924 'unsweetened', brand WENDY'S; 174144 'black, ready to drink'), while the decaf RTD (173212) is queued and sweetened RTD tea is rejected. One rule: a ready-to-drink bottled or brand record is queued (ingredients such as acidulants or preservatives are not stated). Three accepts move to queue; brewed records remain (tea: 171917, 173227, 174120, 174155; coffee: 171881, 171890, 171891).
4. **The 82 'alcoholic_beverage' rejects are mis-bucketed and mis-reasoned.** The FAO text read names no alcoholic beverage (the word appears only in 'non-alcoholic fermentation'), so beer, wine, sake and distilled spirits are source-silent, which is a queue state, not a conditioned reject. Of the 82: 54 are beer, wine, sake, malt beer or distilled records (move to `queue_alcohol_source_silent`); 13 are formulated mixed drinks or liqueurs with added sugar, juice or cream (stay reject); 15 are not alcoholic at all (cranberry juice cocktails, cocktail and whiskey-sour mixes, root beer, ginger ale, an energy drink, a sweetened ginseng tea, non-alcoholic wine and malt beverage) and keep their reject with the correct code.
5. **Juices ('roadmap_parked', V8 V-Fusion):** the junior calls them '100% fruit juice blend'; the FDC names say only 'Juices'. Unsupported claim; queue unchanged. Coconut water, plant milks, herbal infusions (hibiscus, chamomile), chicory and cereal coffee substitutes, sparkling water: source-silent, queue unchanged. Decaffeinated and instant forms stay synonym candidates (naming-only; instant tea or coffee is a dried extract, not the brewed record).
6. **Synonym candidates** (black/green/oolong tea, brewed tea/coffee, espresso, decaf, tap/well/bottled water) are naming-only; the FDC names do not establish that a label's 'green tea' equals the ingredient 'tea'. Parked.

## 4. Reconciled counts
| measure | junior | senior |
|---|---|---|
| accept: stage candidates (tea 4, coffee 3 brewed records) | 10 | 7 |
| accept: existing row `water`, no change | 12 | 12 |
| accept held (RTD) | 0 | 3 |
| queue (34 + 3 held + 54 alcohol source-silent) | 34 | 91 |
| reject | 314 | 260 |
| records | 22 / 34 / 314 | 19 accept (7 + 12) / 91 queue / 260 reject = 370 |

Per-record dispositions: `08_beverages_dispositions.csv`.

## 5. For the staging decision (not started)
Two rows, `tea` and `coffee`, kind `whole_food`, inference level exact-named for the ingredient terms (clause "tea, coffee, and drinking water"); measure: sole item, with sugar, milk, 'instant' and 'decaf' forms (unrecognised), unknown brackets, the whole-food condition guard if it has merged, and combinations such as 'Tea, Sugar, Flavour'. No synonym, marker or classifier change.
