# Backlog (next round; nothing here is being implemented now)

Rule from the reviewer: this round ends with the sweetener + soybean bundle. New case fixes that arrive are recorded here, not implemented.

## Parser and vocabulary
- A bare code after a US-spelled class word ("Stabilizer (414)") is not read as an INS code (code extraction runs before spelling is normalised).
- The note "(INS-INTERNATIONAL NUMBERING SYSTEM)" gets glued onto the flavouring item (Appy, R4).
- A product-name line under the heading ("THE GOOD PRO MIX") gets glued onto the first item.
- "Thickening & Stabilizing Agents" is not matched as a class word.
- Additive codes in a "Contains" line are not shown as code rows.
- Unmodelled on the Good Pro Mix label: fructooligosaccharides, monk fruit, "Probiotic Blend" (Not assessed).
- Processed soy terms (soy lecithin, soya protein isolate) have no rows; "soy" family beyond the soybean row is untouched.
- Silent "complete" status on some merged items (M12, M08, M04): left alone by direction.

## Sourcing
- humectant and firming agent: markers rest on research/02 only; the FAO 2019 text does not name them (research/04 open question).
- ins_map.csv rows whose source column still says "Codex reference data shown separately" (211, 627, 631, 102, 110, 150d, 171): standing rule says no Codex-derived data; licence question open in research/05.
- Reference spot-checks (batches 2, 3, negation addendum) by the owner.

## OCR
- Dominant no-list cause is upright text damaged by blur, size or glare: image quality before and during recognition (sharpness, resolution, glare handling, cropping to the ingredients panel). Rotation was measured and switched off.
