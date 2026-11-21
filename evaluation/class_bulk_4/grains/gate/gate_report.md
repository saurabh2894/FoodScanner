# Gate report: class-grains-1

**Verdict: READY_FOR_REVIEW**

Nothing was merged. `lexicon_candidate_rows.csv` holds the ready rows in lexicon.csv layout and `synonyms_candidate_rows.csv` the synonym candidates in synonyms.csv layout, for review.

| Check | Result |
|---|---|
| staged rows | 23 |
| schema errors | 0 |
| provenance errors | 0 |
| duplicates (exact, synonym, already recognised) | 9 |
| variants of an existing term (informational) | 14 |
| parked in the ambiguity queue | 42 (Counter({'clause_tier': 42})) |
| ready rows (new lexicon rows) | 14 |
| synonym candidates (variant policy variant-policy-class-grains-1) | 0 |
| policy errors | 0 |
| verbatim clause vs FAO text | PASS |
| harness proof (separate processes) | lexicon rows 370 -> 384; all 14 staged terms recognised after; 0 already recognised before |
| flip check (66 frozen inputs, before and after in separate fresh processes) | group 0, drivers 0, status 0, reason 0, warnings 0, ingredients 0, unassessed 0, ins_mappings 0 |
| group/status/driver flips | 0  |
| unexplained changes | 0 |

## Ready rows (new lexicon rows)

- `amaranth flour`
- `barley flour`: separate row because a different grain or a different form (flour vs whole grain, rice type) than the existing row ['barley']; kept as its own row, the existing row is left untouched and not widened
- `black rice`: separate row because a different grain or a different form (flour vs whole grain, rice type) than the existing row ['rice']; kept as its own row, the existing row is left untouched and not widened
- `buckwheat`
- `buckwheat flour`
- `cornmeal`
- `millet flour`: separate row because a different grain or a different form (flour vs whole grain, rice type) than the existing row ['millet']; kept as its own row, the existing row is left untouched and not widened
- `oat flour`: separate row because a different grain or a different form (flour vs whole grain, rice type) than the existing row ['oat']; kept as its own row, the existing row is left untouched and not widened
- `quinoa flour`: separate row because a different grain or a different form (flour vs whole grain, rice type) than the existing row ['quinoa']; kept as its own row, the existing row is left untouched and not widened
- `rye flour`
- `semolina`
- `sorghum`: separate row because a different grain or a different form (flour vs whole grain, rice type) than the existing row ['sorghum flour']; kept as its own row, the existing row is left untouched and not widened
- `spelt flour`
- `wild rice`: separate row because a different grain or a different form (flour vs whole grain, rice type) than the existing row ['rice']; kept as its own row, the existing row is left untouched and not widened

## Synonym candidates (variant policy: same ingredient, plant part and form)


## Duplicates (excluded: already covered)

- `barley`: exact lexicon term (kind whole_food)
- `millet`: exact lexicon term (kind whole_food)
- `parboiled rice`: already recognised by this build (descriptors, plurals or synonyms)
- `red rice`: already recognised by this build (descriptors, plurals or synonyms)
- `rice`: exact lexicon term (kind whole_food)
- `rice flour`: exact lexicon term (kind flour)
- `sorghum flour`: exact lexicon term (kind flour)
- `wheat flour`: exact lexicon term (kind flour)
- `whole wheat flour`: exact lexicon term (kind flour)

## Variants of existing terms (kept; informational)

- `barley flour` ~ ['barley']
- `black rice` ~ ['rice']
- `millet flour` ~ ['millet']
- `oat flour` ~ ['oat']
- `quinoa flour` ~ ['quinoa']
- `sorghum` ~ ['sorghum flour']
- `wild rice` ~ ['rice']

## Ambiguity queue (parked, never included)

- `Flour, 00` (clause_tier, queue_00): a flour grade name; no label word established.
- `Oats, whole grain, rolled, old fashioned` (clause_tier, queue_rolled): rolled oats are flaked (process); the clause names 'flakes' of oats: per-term decision (existing 'oat' row).
- `Oats, whole grain, steel cut` (clause_tier, queue_steel): steel cut oats: per-term decision.
- `Chia seeds, dry, raw` (clause_tier, queue_chia): a seed (nut_seed batch).
- `Bulgur, dry, raw` (clause_tier, queue_bulgur): parboiled cracked wheat: the clause names 'parboiled' rice; per-term decision.
- `Einkorn, grain, dry, raw` (clause_tier, queue_einkorn): rare grain; QUEUE per-term.
- `Farro, pearled, dry, raw` (clause_tier, queue_pearled): pearled grains are polished (a milling step beyond the clause's whole grain); QUEUE per-term.
- `Fonio, grain, dry, raw` (clause_tier, queue_fonio): rare grain; QUEUE per-term.
- `Khorasan, grain, dry, raw` (clause_tier, queue_khorasan): a trademarked wheat (Kamut); rare; QUEUE.
- `Sorghum flour, white, pearled, unenriched, dry, raw` (clause_tier, queue_pearled): pearled grains are polished (a milling step beyond the clause's whole grain); QUEUE per-term.
- `Sorghum grain, white, pearled, unenriched, dry, raw` (clause_tier, queue_pearled): pearled grains are polished (a milling step beyond the clause's whole grain); QUEUE per-term.
- `Quinoa, uncooked` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Rice, brown, parboiled, dry, UNCLE BEN'S` (clause_tier, queue_uncle): a brand-name record (Uncle Ben's), not a food term.
- `Rye grain` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Triticale flour, whole-grain` (clause_tier, queue_triticale): hybrid grain; rare; QUEUE per-term.
- `Wheat, hard red spring` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Wheat, hard red winter` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Wheat, soft red winter` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Corn grain, white` (clause_tier, queue_corn): corn overlaps vegetables (sweet corn, queued in Batch 2) and cereal; QUEUE for an owner decision on corn.
- `Corn flour, whole-grain, blue (harina de maiz morado)` (clause_tier, queue_corn): corn overlaps vegetables (sweet corn, queued in Batch 2) and cereal; QUEUE for an owner decision on corn.
- `Cornstarch` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Couscous, dry` (clause_tier, queue_couscous): couscous is named in the Group 1 DEFINITION ('pasta, couscous and polenta made with flours, flakes or grits and water'), not in the examples: per-term decision.
- `Oats (Includes foods for USDA's Food Distribution Program)` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Sorghum grain` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Triticale` (clause_tier, queue_triticale): hybrid grain; rare; QUEUE per-term.
- `Wheat, hard white` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Wheat, soft white` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Wheat, durum` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Wheat, sprouted` (clause_tier, queue_sprouted): sprouted grains: process-terms review proposes per-term inference rows from the general method clause; owner decision pending (P-A).
- `Barley malt flour` (clause_tier, queue_malt): malted product: malt forms are parked/unplaced in this project (malt extract PARK); QUEUE.
- `Oat flour, partially debranned` (clause_tier, queue_debranned): a milling fraction (bran partly removed): not the plain whole flour.
- `Wheat, KAMUT khorasan, uncooked` (clause_tier, queue_khorasan): a trademarked wheat (Kamut); rare; QUEUE.
- `Spelt, uncooked` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Teff, uncooked` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Corn flour, whole-grain, white` (clause_tier, queue_corn): corn overlaps vegetables (sweet corn, queued in Batch 2) and cereal; QUEUE for an owner decision on corn.
- `Barley, pearled, raw` (clause_tier, queue_pearled): pearled grains are polished (a milling step beyond the clause's whole grain); QUEUE per-term.
- `Buckwheat` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Corn grain, yellow` (clause_tier, queue_corn): corn overlaps vegetables (sweet corn, queued in Batch 2) and cereal; QUEUE for an owner decision on corn.
- `Corn flour, whole-grain, yellow` (clause_tier, queue_corn): corn overlaps vegetables (sweet corn, queued in Batch 2) and cereal; QUEUE for an owner decision on corn.
- `Amaranth grain, uncooked` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Arrowroot flour` (clause_tier, queue_arrowroot): arrowroot flour is a starch product (FAO Group 2 starch example), not a grain flour.
- `Bulgur, dry` (clause_tier, queue_bulgur): parboiled cracked wheat: the clause names 'parboiled' rice; per-term decision.

## Unassessed drops attributed to ready rows

