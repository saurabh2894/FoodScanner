# Backlog

## Reconciled 23 November 2026
Current technical checks below supersede stale implementation status, not historical source/authority claims. No repository reviewer attribution is treated as owner permission.

Resolved in current main: US Stabilizer (414) extracts code 414; Thickening & Stabilizing Agents extracts listed codes and existing class evidence; Contains-line codes are exposed as declaration-only entries; INS explanatory note is not glued into flavour item; M08 splits Milk solids and Sugar. Existing soy lecithin/isolate handling must be checked term-by-term in markers/synonyms rather than inferred from this old no-row note.

Current candidate: M12 adjacent food/additive brackets remain one unchanged item, with a possible-boundary warning and uncertain text accounting. No split, code, driver or group change. M04 is not claimed resolved: complete word accounting alone does not prove correct compound-food boundaries.

Product-name prefix remains unresolved. A synthetic exact heading followed by THE GOOD PRO MIX is still merged with Rice, but no accessible original image/reference was recovered for a safe exclusion rule. Do not strip arbitrary capitalized lines or tune a product-name exception from this synthetic probe.

Other sourcing/OCR/family-code holds below are unchanged. No new OCR tie-break or source admission.

## Historical backlog snapshot (not instructions)

Historical note attributed the old round boundary to a reviewer. Original user-channel research found no direct instruction forbidding a future diagnostic completeness review; the old attribution itself supplies no authority.

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

## Deferred: narrow sourced fix for the 407/407a name-tie hint
- Suppress name-tie "Possible misread" hints only for curated, sourced same-family code pairs stored as data (start: 407/407a). Until then the 407 (carrageenan) display row stays withheld from `ins_names.csv`, because with it "Carrageenan (INS 407a)" raised a false hint (a legitimate family code, e.g. processed eucheuma seaweed). Do not ship the noisy hint together with the 407 row.
- Sources to cite for the pair:
  - JECFA Monograph 4 (2007), Processed Eucheuma Seaweed (PES) specification: https://www.fao.org/fileadmin/user_upload/jecfa_additives/docs/monograph4/additive-353-m4.pdf (synonyms include PNG-carrageenan and semi-refined carrageenan).
  - JECFA database page: https://apps.who.int/food-additives-contaminants-jecfa-database/Home/Chemical/467
  - EFSA 2018 re-evaluation: https://efsa.onlinelibrary.wiley.com/doi/full/10.2903/j.efsa.2018.5238
  - Marinalg monograph (industry source, use with care): https://www.marinalg.org/wp-content/uploads/2012/09/CGN-PES-monograph-November-2006.pdf. Note: US labels may use "carrageenan" for PES.
- Gate: the design and its tests are independently reviewed before shipping.
