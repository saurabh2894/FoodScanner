# Direct culinary coverage 2

## Scope

Based on main `c60aab433316f701acc00a3bcef04dcfa39446a6`: add three canonical ingredients, corn starch, baking powder and baking soda, plus the names cornstarch and maize starch. Candidate totals: 512 canonical entries and 156 aliases. These are not counts of foods proven accurate on market labels.

No INS mapping, marker, pending Codex/GSFA data, OCR algorithm, deployment setting or live-site change is part of this batch. The earlier four suji/rawa/cilantro/Chinese-parsley aliases are preserved.

## Placement and naming evidence

| Ingredient | Placement | Evidence role |
| --- | --- | --- |
| corn starch | Group 2 | Class-instance of FAO Table 1, printed p.11: "starches extracted from corn and other plants". Applies to plain corn starch, not corn flour or modified starch. |
| baking powder | Group 2 | Explicitly named in Table 4, footnote 5, under Other processed culinary ingredients in the published NOVA coding study PMC10127522. This is the study's named placement, not an alleged FAO quote. |
| baking soda | Group 2 | Same exact-named Table 4, footnote 5 placement. No inference from this food name to an INS code, chemical name or unspecified additive function. |
| cornstarch, maize starch | Same ingredient as corn starch | USDA National Agricultural Library Thesaurus preferred term and synonyms, concept 29170. Naming only, not independent NOVA evidence. |

Sources:
- FAO, *Ultra-processed foods, diet quality, and health using the NOVA classification system*: https://www.fao.org/4/ca5644en/ca5644en.pdf
- Published NOVA coding study, PMC10127522, Table 4: https://pmc.ncbi.nlm.nih.gov/articles/PMC10127522/table/tbl4/
- USDA NALT, corn starch: https://lod.nal.usda.gov/nalt/en/page/29170
- USDA FoodData Central SR Legacy naming inventory: https://fdc.nal.usda.gov/download-datasets/

The PMC table and its category/footnote relationship were checked against the saved HTML retrieved on November 22, 2026 at12:20IST. A later fetch returned no content; this does not constitute a new successful source read. No bulk text is imported. Article reuse licence remains unverified; only the short food names needed to identify the placement are quoted. USDA naming records do not decide NOVA groups.

## Narrow safeguards

The existing culinary composition check now also covers exactly the three new canonical identities. It does not expand across all historical culinary rows or all raw-food rows. Unknown bracket content or a known non-culinary carrier does not inherit the head ingredient's Group 2 placement. The corn/maize source words are a closed corn-starch identity exception. Recognised Group 2 coingredients keep the existing culinary-mixture treatment.

A new culinary child inside a flour head must not turn a previously unassessed mixture into plain Group 1 flour. This safeguard is limited to the new identities. Historical salt/sugar/flour policies and existing mixed-raw-food routes are not changed here. The broader proposed guards, including their 592 answer-to-abstention changes, remain out of this batch.

Corn Oil (baking powder) retains the existing oil-powder abstention. No new exception is invented for that inherited conservative route.

## Historical evidence

The older starch test exclusions were earlier technical evidence holds, not a newly discovered user prohibition on further source-backed work. The corn/maize exception is explicit in the affected historical tests. Potato starch and modified/other starch forms retain their negative controls. Frozen historical labels and results are not edited.

## Local validation, November 22, 2026

- 107 new pytest cases, including scope/provenance and 106 form assertions.
- 1133/1133 shipped Python/JavaScript parity cases, up from921. Both input paths include the new forms.
- A further2757 full-field Python/JavaScript comparisons, including every509legacy canonical head with each of the five new ingredient names as a bracket child.
- All6108previously measured conditioned legacy inputs are identical across every captured field.
- Frozen66labels: zero captured-field differences.
- Existing resource bytes are unchanged prefixes; exactly three rows and two aliases are appended locally.
- Supported pytest suite:2451passed,2failed,2skipped,1deselected,5xfailed. The two failures reproduce the original baseline: the millet photo OCR omits the Puff section heading, and the demand-miner test lacks archived historical fenugreek-result evidence. These are validation gaps, not green tests. Pending-INS-reference tests and the one dependent web test are excluded, not recovered or fabricated.
- The32out-of-sample input cache is absent from this reconstruction, so that gate has not been rerun. Do not claim out-of-sample validation.
- Fresh local preview built. Actual pixels inspected for Cornstarch, Group2, and Baking Powder (XQ9), abstention. This is local UI evidence, not a live deployment claim.

The2545legacy-head/new-child interaction probes add1435answers:160culinary mixtures become Group2 and1275fruit/legume/nut/vegetable mixtures become Group3 under existing source-based mixture rules. None becomes Group1. These synthetic results are not measured market coverage. Other interactions remain abstaining or unchanged; flour and whole-food form uncertainty is retained.

## Release state

Prepared and tested locally. Do not infer a push or deployment from this document. Before publication, revalidate current main, inspect the complete diff and final uploaded contents, and verify the resulting main commit. Manual Vercel retries remain held for the existing evening window. The first independent four-alias push is already on main atc60aab4; this second batch is separate.
