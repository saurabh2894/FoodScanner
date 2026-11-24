# pool-a-24: four culinary rows from the verified PMC footnote 5 residue

Batch of four rows, from candidate-pool-24.md pool A (admissibility graded 2026-11-24). Head terms 563 -> 567.

## Placement (each row)
- Primary: FAO 2019 (ca5644en.pdf) Table 1 Group 2 general definition (p.11), class-instance; clause verified verbatim
  against the local PDF. Per-term class fit: coconut cream (pressed/extracted from coconut flesh), milk cream
  (centrifuged from milk; "centrifuging" is a named method), unsweetened baking chocolate (ground cocoa mass),
  gelatin powder (extracted from animal tissues, which are group 1 foods; general-definition fit, noted as the weakest).
- Corroboration (exact-named): PMC10127522 footnote 5 names "coconut and milk cream; unsweetened baking chocolate,
  cocoa powder and gelatin powder" under "Other processed culinary ingredients" — verified LIVE in browser DOM
  2026-11-24. Licence unverified: short quote only, corroborating; never sole support.
- research/09 dairy hold pre-review (recorded in candidate-pool-24.md): does not cover a standalone milk cream row;
  the row inherits nothing from milk rows.

## Mechanism: cocoa-powder-24 generalised
cocoa_powder_residual is generalised to plain_culinary_residual over _PLAIN_CONDITION_CULINARY = {cocoa powder,
coconut cream, milk cream, unsweetened baking chocolate, gelatin powder}, mirrored in web_preview/foodscan.js.
Bracket beyond a share or the word "unsweetened" abstains with a per-term plain-food reason. Cocoa behaviour and
message unchanged (single-term tail still reads "...not established as plain cocoa powder...").

## Conditioned-form review (locked in tests/test_pool_a_24.py)
- Plain rows, "(x%)" and "(unsweetened)" -> Group 2, single culinary driver.
- "(Sugar)" on each row -> abstains, "not established as plain <term>".
- "cream of coconut", "whipped cream", "aerosol cream", "baking chocolate" (bare: the source names only the
  unsweetened form), "sweetened baking chocolate", "jelly crystals", "gelatin dessert", "cream" (bare: ambiguous
  between coconut/milk cream; no alias assumed), "gelatin" (bare), "agar agar" -> abstain.
- Neighbours unchanged: cocoa powder / cocoa butter / vinegar behave as before.

## Gates
- Flip check (separate fresh processes, before-text.json vs after-text.json over the frozen inputs): 0 diffs.
- Full suite: 10913 passed + 5 xfailed with only the two pre-existing sandbox-environment failures (tesseract OCR
  variance in test_millet_puff_photo; missing node playwright in test_result_source_provenance), both reproduced on
  clean main before this batch and reported distinctly, never folded into pass counts.
- scripts/parity_check.py: 16487/16487 Py/JS identical, including 8 new focused pool-a pairs.
