# Fresh batch 3: scores (frozen build dd13c04)

Single frozen-build sample, not a general accuracy claim. References are LLM-prepared from photos and still need the owner's spot-check. Selection rule `eadb54e`, references `cb8d4f2`; no code changed between the freeze and these scores (diff of src/, web_preview/, scripts/, tests/ against dd13c04 is empty). Tests 499 passed; parity 354/354 identical.
Scope: 13 labels run (Q01 excluded before scoring). Classification judged on 13 (Q02-Q14). Extraction judged on 11 labels (Q02-Q12), 38 reference items. Q13, Q14 extraction unjudged.
Development-overlap labels: Q05, Q06, Q11, Q14 (results given with and without).

## Extraction (38 reference items, Q02-Q12)
| Mode | own | merged | split | omitted | notes |
|---|---|---|---|---|---|
| Paste | 28 | 10 | 0 | 0 | merged: Q05 vitamin pair (2), Q07 'Milk & Milk Solids Milk' (2), Q08 vitamin pair (2), Q12 acidity regulator through Vitamin D (4, unclosed bracket) |
| Photo | 22 | 7 | 0 | 9 | merged: Q11 acidity regulator + stabilisers + vitamins (3), Q12 (4). Omitted: no list found Q02 (1), Q05 (3), Q09 (2), Q10 (1); Q08 vitamins read as garbage (2) |

Photo 'own' includes noisy items: Q03 'lodised Sal AONTAINS MILK' (glued line, OCR fault), Q06 item carries the glued 'For any queries reach us at, fat 3.50% Min.'.

## Classification (13 labels Q02-Q14; expected group provisional)
| Mode | Subset | Correct confident | Wrong confident | Abstained | Coverage | Accuracy on answered |
|---|---|---|---|---|---|---|
| Paste | all 13 | 6 (Q02, Q04, Q10, Q12, Q13, Q14) | 0 | 7 | 46% | 6/6 |
| Paste | without overlap (9) | 5 | 0 | 4 | 56% | 5/5 |
| Photo | all 13 | 2 (Q04, Q12) | 0 | 11 | 15% | 2/2 |
| Photo | without overlap (9) | 2 | 0 | 7 | 22% | 2/2 |
Part A (plain dairy, Q02-Q10, 9 judged): paste answered 3 of 9 (Q02, Q04, Q10), photo 1 of 9 (Q04).

## Did the fixed rule fire on real labels?
- Milk-plus-culture rule: fired on Q04 (Nandini curd: 'Milk Solids (Toned Milk) & Active Culture'), paste and photo, Group 1. Zero other firings. Controls Q11, Q12 did not fire it (correct).
- Not fired, abstained (no rule exists or vocabulary gap): Q03 'lodised' (OCR typo), Q05/Q08 vitamins unrecognised, Q06 'cow milk' unrecognised, Q07/Q09 milk plus milk solids (no culture, no rule), Q11 stabilisers/acidity regulator unlisted.
- Provenance line ('Made from ...'): no label in this batch had one; the path was not exercised.
- Negation: NOT exercised. Q13's text ('Contains Non-Caloric Sweeteners') holds no negation; the selection pattern 'contains no' matched the prefix of 'Non'. This is a selection-rule defect found at scoring, recorded here, not corrected after the draw. B2 therefore yielded no real negation label; negation is covered only by unit tests (tests/test_dairy_negation_round.py).
- Function-class hint: removed; no flag seen. Name-tie hint: not triggered. Two-readings disagreement flag: fired on Q11 (INS 339(i) vs INS 339); the label reads 339 (ii), so neither reading was right and the flag only said the readings differ.

## Timing (photo, every OCR call timed)
Total per photo (ms) sorted: 1309, 1469, 1499, 1528, 3174, 3281, 3666, 5161, 5361, 8108, 12190, 13232, 17246; median 3666. A second reading ran on 12 of 13 photos (not Q04, which read clean). Slowest single call 10183 ms (Q02 first reading).

## Findings
1. Abstentions are vocabulary gaps and merges, not wrong answers: vitamins, 'cow milk', 'milk + milk solids' without culture, stabiliser-only lists.
2. Q10: the second reading held the full list ('INGREDIENT: MilK solids (Pasteurized skimmed cow milk)') but a stray bullet and the OCR-noisy lines left it unusable (yield tie, first reading kept), so the result is 'OCR produced little text'. Paste-equivalent of that text abstains too. No change made.
3. Q02, Q05, Q09, Q13, Q14 photos: no list found (sideways or tiny text, damaged OCR); abstained rather than guessed.
4. Q07 paste input carries a stray trailing 'Milk' from the source record; photo reading is clean.
5. Q12 the OCR-style bracket '[INS 339 (ii)' without closing makes four reference items merge; Group 4 still stands through Option A with the warning.
6. Q11: stabilisers and acidity regulator are unlisted classes, so an abstention (reference expected Group 4); not a wrong answer.
7. Selection-rule defect above (Q13).
Not done by design: no tuning, no code change, nothing pushed.
