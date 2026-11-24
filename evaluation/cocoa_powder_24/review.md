# cocoa-powder-24: one culinary row (cocoa powder), with the parked bracket condition implemented

Batch of one row, demand-led: cocoa powder is the rank-5 open demand term (inputs b1/N14 "Cocoa Powder (7%)" and
b3/Q12 "Cocoa Powder (1.5%)" now assess; both were unassessed before). Head terms 562 -> 563.

## Placement
- Row: `cocoa powder`, kind culinary, Group 2 (processed culinary ingredient).
- Primary: FAO 2019 (ca5644en.pdf) Table 1 Group 2 general definition (p.11), class-instance (cocoa powder is the
  pressed and ground residue of cocoa beans after part of the cocoa butter is removed). Clause verified verbatim
  against the local PDF copy 2026-11-24.
- Corroboration (exact-named): PMC10127522 (Martinez Steele et al., J Nutr 2022) table footnote 5 names
  "cocoa powder" under "Other processed culinary ingredients". Verified LIVE 2026-11-24 on the rendered PMC article
  page (browser DOM; web_fetch markdown drops the footnotes). Licence unverified: short quote only, corroborating,
  per the 2026-11-21 admissibility decision.
- Under the 2026-11-21 placement rule (one strong applicable primary NOVA source suffices; naming-only sources never
  place), this meets the bar alone; the exact-named corroboration is additional.

## The pmc-reresearch-4 park, honoured
The Nov 21 record parked cocoa powder "until an item-level 'unsweetened' condition mechanism exists for this kind".
That mechanism is now built: `cocoa_powder_residual` in classify.py (mirrored in web_preview/foodscan.js). An item
places as Group 2 only when its bracket is empty, a percentage/quantity, or the word "unsweetened"; any other bracket
content (sugar, milk, alkalising agents, another food) abstains with a cocoa-specific reason. An independent strong
marker still decides first ("Cocoa Powder (sugar, flavour)" -> Group 4 via the flavour marker).

## Conditioned-form review (new surfaces probed, results locked in tests/test_cocoa_powder_24.py)
- "cocoa powder", "COCOA POWDER", "Cocoa Powder (5%)" / "(1.5%)" / "(unsweetened)" -> Group 2.
- "Cocoa Powder (Sugar)", "(alkalised)", "(Milk)" -> abstain (composition not established as plain cocoa powder).
- "cocoa" (bare) -> abstain: ambiguous (powder, mass, drinking cocoa); no alias assumed.
- "cocoa solids", "cocoa mass", "cocoa nibs" -> abstain: stay parked, no authoritative source names them.
- "sweetened cocoa powder", "dutch cocoa powder", "unsweetened cocoa powder" (name words) -> abstain: conditioned
  name forms are not aliased; documented in the row provenance.
- "cocoa butter" row unchanged; no collision (distinct terms, no alias overlap).
- "Milk, Cocoa Powder, Sugar" -> Group 3 (whole food + culinary); "cocoa powder, sugar" -> abstain (existing
  culinary-mixture rule).

## Gates
- Flip check (separate fresh processes, evaluation/cocoa_powder_24/before-text.json vs after-text.json): the only
  changes are b1/N14 and b3/Q12 unassessed lists losing the cocoa powder item; no group/status/driver flips.
- Full suite: 10913 passed + 5 xfailed; two pre-existing sandbox-environment failures (tesseract OCR variance in
  test_millet_puff_photo, missing node 'playwright' in test_result_source_provenance) reproduce identically on clean
  9563538 and are unrelated to this batch.
- scripts/parity_check.py: 16471/16471 identical Py/JS, including 8 new focused cocoa pairs.
