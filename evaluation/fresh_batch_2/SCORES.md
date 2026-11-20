# Fresh batch 2: scores for ONE frozen build (code commit 2eb5f39)

Frozen build: code at `2eb5f39`. The selection rule (`2fc3ab4`) and the references (`f8cac25`) were committed before any run; no change under src/, web_preview/, scripts/ or tests/ after `2eb5f39`. No code was changed while scoring and nothing
was tuned to this batch. One sample: 15 drawn, M02 excluded before scoring under the rule (its photo shows a nutrition table, no ingredient list), so 14 scored; M13's item list is unjudged (unreadable photo) so extraction uses 13 labels and 94 reference
items, classification uses 14 judged labels. References were written by an LLM from the photos before any run and are NOT yet spot-checked by the owner. OCR-garbled items count as present when a human can recognise them (approximate).
Correction to the README: five scored labels (not six) share a product family with development items: M01, M04, M05, M10, M14; "without overlap" below means the other 9 labels.
Outputs: `frozen_results_2eb5f39/` (every OCR reading and its time are in photo_results.json).

## A. Extraction (reference items)
| Mode | Own item | Merged | Omitted | Additions | List found in the right place |
|---|---|---|---|---|---|
| Paste (untouched Open Food Facts text) | 77/94 | 6 | 11 | 1 | 13/13 |
| Photo (browser OCR, second reading when needed) | 27/94 | 23 | 44 | 0 | 7/13 (6 no list) |
- Paste merges: M08 `milk solids and sugar` (milk solids is not in the vocabulary, so the pair is not split), M09 `malt extract and dough conditioner (INS 223)` (the shared-code-list rule keeps it whole: one trailing code could belong to either side; the earlier N02 split worked only because its first side was a flavouring, which carries no INS number), M12 `(clove, cinnamon, chilli) PRESERVATIVE (INS 211)` (the pack has no comma; completeness stayed "complete").
  Paste omissions: M09 1 (the source text lacks the flavouring phrase that is on the pack), M10 8 (second section after a full stop: set aside under "not read" and flagged), M11 2 (a stray full stop in the source text: flagged). Addition: M06 `Made from Toned Milk` read as an ingredient.
- Photo: no list on M03, M06, M08, M10, M14, M15 (and M13). M09's list is found, but an unclosed bracket makes one garbled item of all 13. OCR damage, not a parser rule, in every no-list case I checked (the heading is not read or the text is mostly garbage).

## B. Classification (14 judged labels; abstentions are their own outcome)
| Mode | Correct confident | Wrong confident | Abstained | Without the 5 overlapping labels (9) |
|---|---|---|---|---|
| Paste | 11 | 0 | 3 (M03, M06, M08: all plain dairy or milk-solids lists) | 6 correct, 0 wrong, 3 abstained |
| Photo | 4 (M01, M07, M09, M11) | 0 | 10 | 3 correct, 0 wrong, 6 abstained |
The milk-plus-culture rule fired on **0 of 28 runs**. The plain dairy labels exposed why: `milk solids` is not in the vocabulary and not in the rule (M03, M08); M06 carried a trailing `Made from Toned Milk` item in the source text, so the list was no longer "only milk plus cultures"; M06 and M03 photos found no list.

## C. Hint, disagreement and role-phrase paths
- Function hint ("Read as INS x. ... Possible misread"): fired once in paste, on **M10 (Maggi) for INS 508 under "Thickeners": a FALSE hint**. The pack prints 508 as a thickener; the JECFA page for 508 lists flavour enhancer, gelling agent and yeast food, so the check disagreed. It did not change anything, but it is exactly the failure mode the wording warns about ("a missing function in one database is not proof"). Photo: 0 hints. The codes 296 and 334 on M15 and 330 on several labels raised no hint.
- Two-readings disagreement: fired once (photo M11: the first reading had no code, the second read INS 330, 627, 631). It never replaced anything.
- Role phrase: the provisional-mapping warning showed on M12 in both modes (paste: drove Group 4; photo: "stabilizing agent" read as the stabiliser class, the emulsifier word was misread, so the result abstained).
- Negation bug (photo M07): "CONTAINS NO ADDED FLAVOURS, ADDED COLOUR OR PRESERVATIVES" was read as a declaration: the result lists a declared flavour as a driver next to the real firming-agent driver. The group is right only because INS 509 (firming) decides anyway.

## D. Added time of the second OCR reading (14 photos, headless browser)
Mean total per photo 13.3 s (three large photos took 16 to 49 s on the first reading); mean first reading 9.4 s, mean second reading 2.9 s; the second reading ran on 13 of 14 photos, almost always because the first reading was not clean.
Only ONE photo (M07, 0.8 s) ran the second reading solely because the first reading held codes. Added time attributable to the codes trigger: 0.8 s over the whole set: not material, so the trigger is not narrowed.

## E. Did uncertainty warnings work?
Worked: paste M07, M10, M11 (flagged uncertain: truncated or text not read), photo M05, M09, M11, M12 (uncertain with warnings). Did not work (extraction wrong, completeness "complete", no warning): paste M08 (merge), M12 (merge, missing comma on the pack), M06 (non-ingredient text added), photo M04 (flavouring and acidity regulator merged, COMPLETE). No wrong confident group resulted in any of them.

Not general accuracy. Not validation. A later independent check needs another fresh batch.
