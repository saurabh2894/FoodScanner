# Negation addendum: scores (build dd13c04, real labels, pre-registered)

One frozen-build sample of 6 hand-chosen labels, not an accuracy claim. References are LLM-prepared from the photos and need the owner's spot-check. Code under test unchanged from dd13c04 (src/, web_preview/ identical; scripts/ differs only by 8 parity corpus texts). Reference hash: REFERENCES.sha256 (taken before any run). pytest 505 passed; parity 362/362 identical.

## Paste (untouched record text), 6 labels
| Label | Negation / statement | Expected | Result | Verdict |
|---|---|---|---|---|
| R1 Dlecta cheddar (list cut off in photo) | 'CONTAINS NO ADDED FLAVOUR & NO A...' | abstain, never 4 | abstain: only a stabiliser (INS 509, unlisted); no flavour driver | pass |
| R2 Budhani wafers | 'Contains: No artificial colours, flavours or preservatives.' + processing-facility advice | 3 or abstain, never 4 | abstain (palmolien oil, peanut oil, 'lodized' not in vocabulary); no drivers | pass (abstain) |
| R3 Urja lassi | MIXED same sentence: 'CONTAINS ADDED FLAVOUR(S) (...) NO PRESERVATIVES.' | 4 | 4, one driver: declared flavour; no preservative driver | pass |
| R4 Appy | 'NO ADDED PRESERVATIVE' after the list | 4 | 4 (colour INS 150d, flavouring); preservative not read | pass |
| R5 Magnum (paste only) | allergen-free: 'May contain soy and other nuts. Gluten free.' | 4 | 4 (emulsifier, flavourings, colour); no gluten/nut item or driver; 18 of 18 items | pass |
| R6 Bovonto | positive colours+flavours Contains sentence, then 'CONTAINS NO FRUIT JUICE OR PULP' | 4 | 4; drivers: declared colour and flavour only; the negation is not an item or driver | pass |
Correct confident 4 (R3-R6), abstained 2 (R1, R2), wrong confident 0. The two abstentions are the labels where nothing but the negation could have produced a Group 4.

## Did the negation fix matter on real labels? (comparison, not scored)
The same inputs on the pre-fix build 2eb5f39 gave a false Group 4 on R1 and R2 (the negated claim read as a declared flavour/colour). R3-R6 gave Group 4 on both builds. So the fix flips two of six real labels from a wrong confident answer to an abstention.

## Photo (frozen browser build), 5 labels (R5 photo has no list)
| Label | Result | Cause |
|---|---|---|
| R1 | abstain: no ingredient list found | OCR noise on the cut-off pack (first reading 15.6 s) |
| R2 | abstain: 'text after a full stop looks like more ingredients' | OCR split 'Edible' ('gdible') and the line break; negation text not reached |
| R3 | abstain: no list found | OCR lost the heading and several words ('Mil Solids ( lt curd)') |
| R4 | Group 4, correct | list read; 'NO ADDED PRESERVATIVE' not read as a preservative |
| R6 | abstain: truncated (unclosed bracket) | OCR damaged the Contains line; negation line not misread |
Correct confident 1, wrong confident 0, abstained 4. Negation was therefore exercised through the photo path on one label only (R4); the other photo failures are OCR, not the negation rule. Per-call timings are in photo_results.json (totals 2.6 s to 19.8 s).

## Extraction notes (paste)
- R4: the note '(INS-INTERNATIONAL NUMBERING SYSTEM)' is glued onto the flavouring item (also in the photo reading); it did not change the group. Reference criterion 'note is not an ingredient' is NOT met. Also the source text has a mismatched bracket '[... INS 331(iii)]'.
- R1: three items read (pasteurized milk, stabilizer INS 509, 'MICROBIAL CULTU' cut off); the marketing and address text after the list was set aside.

## Limits
Six labels; negation phrases found were mostly 'no preservatives / no added flavour' types. The mixed-line case (R3) is same sentence; a mixed case where a negated span and a positive span use the same additive class in one sentence ('no added colours, contains preservative') is covered by unit tests only, because none was found among the candidates.
