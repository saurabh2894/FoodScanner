# Frozen Evaluation Rollup (fresh_batch_1 & fresh_batch_2)

This document summarizes the hand-adjudicated frozen evaluation artifacts recorded in `evaluation/fresh_batch_1` and `evaluation/fresh_batch_2`. Stated figures and notes are extracted read-only from each batch's respective `SCORES.md` and `ERRATA.md`. The tie-out verification computes category sums and compares them directly against stated and table denominators to verify integrity.

## 1. Batch Summaries & Denominator Overview

| Batch | Title | Stated Extraction Denom | Table (Derived) Ext Denom | Stated Classif Denom | Summed (Derived) Classif Denom |
|---|---|---|---|---|---|
| `fresh_batch_1` | Fresh batch 1: scores for ONE frozen build (code commit 12e7226) | 121 reference items in 15 labels | 121 | 13 labels (N07 and N10 unjudged) | 13 |
| `fresh_batch_2` | Fresh batch 2: scores for ONE frozen build (code commit 2eb5f39) | 13 labels and 94 reference items | 94 | 14 judged labels | 14 |

## 2. Batch: `fresh_batch_1`
**Title**: Fresh batch 1: scores for ONE frozen build (code commit 12e7226)

**Errata Notice:**
- references.md and reference.json are NOT edited: batch 1's original scores (build 12e7226) keep their 121-item denominator. Any re-run from the fix round on
- states the corrected denominator below.
- Erratum 1 (v1): N13, `nature identical and natural flavouring substances` is ONE item
- What changes in the re-run table (REGRESSION.md, build 9c00962), recomputed on 120

**Metadata & Context:**
- Frozen build: code at `12e7226`; the reference commit `608fc6c` adds only evaluation files (no change under src/, web_preview/, scripts/, tests/ between them). No code was changed while scoring and nothing was tuned to this batch. One sample, 15 labels scored (16 drawn; N04 excluded before scoring as a variant of a development product): not a general accuracy figure. References were written by an LLM from the photos before any run and have not been spot-checked by the owner. Item adjudication for OCR-garbled items counts an item as present when a human can recognise it; those counts are approximate. All numbers are from `frozen_results_12e7226/`.
- Judged for classification: 13 labels (N07 and N10 unjudged). Extraction denominator: 121 reference items in 15 labels.

### Extraction Outcomes
| Mode | List Found | Own Item | Merged | Split | Omitted | Additions |
| --- | --- | --- | --- | --- | --- | --- |
| Paste (untouched Open Food Facts text) | 15/15 labels | 92/121 | 17 | 2 | 10 | 0 (stray text glued into an item on N03 and N09) |
| Photo (browser OCR, with second pass when needed) | 7/15 labels (1 wrong block, 7 no list) | 18/121 | 10 | 0 | 93 (72 of them in the 7 no-list photos) | 8 |

**Extraction Notes:**
- Paste merges: N02 (flavouring + dough conditioner), N08 (two cultures), N13 (nature-identical + natural flavouring), N15 (missing comma), N16 (missing comma, then an unclosed bracket swallows 7 items). Splits: N13 (thickeners + code), N14 (the group name 'Dry Fruits, Nuts & Seeds'). Omitted: N03's whole second section (10 items), set aside under "not read" and flagged.
- Photo: OCR read error versus parser error. No heading text was read on N01, N02, N03, N10, N14, N15 and N16, so no list was found. On N01, N03 and N14 the list text was partly read, so block inference could not recover them; on N02, N10, N15 and N16 the OCR was mostly garbage. N13 is a parser error: the word INGREDIENTS inside a marketing line ('COOKING INGREDIENTS & MEALS') was taken as the heading, giving the wrong block, with completeness reported "complete".

### Classification Outcomes (abstentions are their own outcome)
| Mode | Correct Confident | Wrong Confident | Abstained |
| --- | --- | --- | --- |
| Paste | 8 (all Group 4: N01, N02, N05, N06, N13, N14, N15, N16) | 0 | 5 (N03 section unread, N08 and N09 vocabulary, N11 weak/unlisted only, N12 emulsifying agent not recognised as an emulsifier) |
| Photo | 2 (N05, N06) | 0 | 11 |

**Classification Notes:**
- Unjudged (excluded): N07 and N10, abstained in both modes. Abstentions are their own outcome, not counted as failures or successes.
- The milk-plus-culture rule fired on 0 of 15 labels (N08's 'probiotic culture' and N09's 'buffalo milk' are not in the vocabulary).

### Uncertainty Warning Effectiveness
- **Worked:** paste N03, N08, N16; photo N05, N11, N12 (completeness uncertain with reasons or warnings); every Group 4 given on an incomplete reading carried a warning.
- **Did not work:** (extraction wrong, completeness "complete", no warning): paste N02, N13, N14, N15; photo N07 (2 items omitted), N08 (3 items merged), N13 (wrong block). None of these produced a wrong confident group (paste answers were correct; the photo cases abstained).

### Recorded vs. Unrecorded Inventory
**Recorded Fields & Sections:**
- Extraction section: Recorded (2 rows)
- Extraction table: Split column: Recorded
- Classification section: Recorded (2 rows)
- Uncertainty warnings section: Recorded

**Unrecorded / Missing in this Batch:**
- Classification table: Without overlapping labels column (not recorded in batch table)

### Denominator & Tie-Out Verification
- Extraction items (Paste): 92 own + 17 merged + 2 split + 10 omitted = 121/121 (Ties out exactly; table denominator matches stated denominator (121))
- Extraction items (Photo): 18 own + 10 merged + 0 split + 93 omitted = 121/121 (Ties out exactly; table denominator matches stated denominator (121))
- Classification labels (Paste): 8 correct + 0 wrong + 5 abstained = 13/13 (Ties out exactly with stated denominator)
- Classification labels (Photo): 2 correct + 0 wrong + 11 abstained = 13/13 (Ties out exactly with stated denominator)

## 3. Batch: `fresh_batch_2`
**Title**: Fresh batch 2: scores for ONE frozen build (code commit 2eb5f39)

**Metadata & Context:**
- Frozen build: code at `2eb5f39`. The selection rule (`2fc3ab4`) and the references (`f8cac25`) were committed before any run; no change under src/, web_preview/, scripts/ or tests/ after `2eb5f39`. No code was changed while scoring and nothing was tuned to this batch. One sample: 15 drawn, M02 excluded before scoring under the rule (its photo shows a nutrition table, no ingredient list), so 14 scored; M13's item list is unjudged (unreadable photo) so extraction uses 13 labels and 94 reference items, classification uses 14 judged labels. References were written by an LLM from the photos before any run and are NOT yet spot-checked by the owner. OCR-garbled items count as present when a human can recognise them (approximate). Correction to the README: five scored labels (not six) share a product family with development items: M01, M04, M05, M10, M14; "without overlap" below means the other 9 labels. Outputs: `frozen_results_2eb5f39/` (every OCR reading and its time are in photo_results.json).

### Extraction Outcomes
| Mode | List Found | Own Item | Merged | Split | Omitted | Additions |
| --- | --- | --- | --- | --- | --- | --- |
| Paste (untouched Open Food Facts text) | 13/13 | 77/94 | 6 | not recorded in batch table | 11 | 1 |
| Photo (browser OCR, second reading when needed) | 7/13 (6 no list) | 27/94 | 23 | not recorded in batch table | 44 | 0 |

**Extraction Notes:**
- Paste merges: M08 `milk solids and sugar` (milk solids is not in the vocabulary, so the pair is not split), M09 `malt extract and dough conditioner (INS 223)` (the shared-code-list rule keeps it whole: one trailing code could belong to either side; the earlier N02 split worked only because its first side was a flavouring, which carries no INS number), M12 `(clove, cinnamon, chilli) PRESERVATIVE (INS 211)` (the pack has no comma; completeness stayed "complete").
- Paste omissions: M09 1 (the source text lacks the flavouring phrase that is on the pack), M10 8 (second section after a full stop: set aside under "not read" and flagged), M11 2 (a stray full stop in the source text: flagged). Addition: M06 `Made from Toned Milk` read as an ingredient.
- Photo: no list on M03, M06, M08, M10, M14, M15 (and M13). M09's list is found, but an unclosed bracket makes one garbled item of all 13. OCR damage, not a parser rule, in every no-list case I checked (the heading is not read or the text is mostly garbage).

### Classification Outcomes (abstentions are their own outcome)
| Mode | Correct Confident | Wrong Confident | Abstained | Without the 5 overlapping labels (9) |
| --- | --- | --- | --- | --- |
| Paste | 11 | 0 | 3 (M03, M06, M08: all plain dairy or milk-solids lists) | 6 correct, 0 wrong, 3 abstained |
| Photo | 4 (M01, M07, M09, M11) | 0 | 10 | 3 correct, 0 wrong, 6 abstained |

**Classification Notes:**
- The milk-plus-culture rule fired on **0 of 28 runs**. The plain dairy labels exposed why: `milk solids` is not in the vocabulary and not in the rule (M03, M08); M06 carried a trailing `Made from Toned Milk` item in the source text, so the list was no longer "only milk plus cultures"; M06 and M03 photos found no list.

### Uncertainty Warning Effectiveness
- **Worked:** paste M07, M10, M11 (flagged uncertain: truncated or text not read), photo M05, M09, M11, M12 (uncertain with warnings).
- **Did not work:** (extraction wrong, completeness "complete", no warning): paste M08 (merge), M12 (merge, missing comma on the pack), M06 (non-ingredient text added), photo M04 (flavouring and acidity regulator merged, COMPLETE). No wrong confident group resulted in any of them.

### Additional Recorded Sections
#### C. Hint, disagreement and role-phrase paths
- Function hint ("Read as INS x. ... Possible misread"): fired once in paste, on **M10 (Maggi) for INS 508 under "Thickeners": a FALSE hint**. The pack prints 508 as a thickener; the JECFA page for 508 lists flavour enhancer, gelling agent and yeast food, so the check disagreed. It did not change anything, but it is exactly the failure mode the wording warns about ("a missing function in one database is not proof"). Photo: 0 hints. The codes 296 and 334 on M15 and 330 on several labels raised no hint.
- Two-readings disagreement: fired once (photo M11: the first reading had no code, the second read INS 330, 627, 631). It never replaced anything.
- Role phrase: the provisional-mapping warning showed on M12 in both modes (paste: drove Group 4; photo: "stabilizing agent" read as the stabiliser class, the emulsifier word was misread, so the result abstained).
- Negation bug (photo M07): "CONTAINS NO ADDED FLAVOURS, ADDED COLOUR OR PRESERVATIVES" was read as a declaration: the result lists a declared flavour as a driver next to the real firming-agent driver. The group is right only because INS 509 (firming) decides anyway.

#### D. Added time of the second OCR reading (14 photos, headless browser)
- Mean total per photo 13.3 s (three large photos took 16 to 49 s on the first reading); mean first reading 9.4 s, mean second reading 2.9 s; the second reading ran on 13 of 14 photos, almost always because the first reading was not clean.
- Only ONE photo (M07, 0.8 s) ran the second reading solely because the first reading held codes. Added time attributable to the codes trigger: 0.8 s over the whole set: not material, so the trigger is not narrowed.

### Recorded vs. Unrecorded Inventory
**Recorded Fields & Sections:**
- Extraction section: Recorded (2 rows)
- Classification section: Recorded (2 rows)
- Classification table: Without overlapping labels column: Recorded
- Uncertainty warnings section: Recorded
- Additional section: C. Hint, disagreement and role-phrase paths: Recorded
- Additional section: D. Added time of the second OCR reading (14 photos, headless browser): Recorded

**Unrecorded / Missing in this Batch:**
- Extraction table: Split column (not recorded in batch table)

### Denominator & Tie-Out Verification
- Extraction items (Paste): 77 own + 6 merged + 11 omitted = 94/94 (Sum matches table denominator, assuming 0 splits as split column is not recorded; table denominator matches stated denominator (94))
- Extraction items (Photo): 27 own + 23 merged + 44 omitted = 94/94 (Sum matches table denominator, assuming 0 splits as split column is not recorded; table denominator matches stated denominator (94))
- Classification labels (Paste): 11 correct + 0 wrong + 3 abstained = 14/14 (Ties out exactly with stated denominator)
- Classification labels (Photo): 4 correct + 0 wrong + 10 abstained = 14/14 (Ties out exactly with stated denominator)
