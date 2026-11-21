# 08 Admissible-source survey for re-researching parked terms (2026-11-21; REPORT ONLY: nothing below is used for a row until you agree)

Standing limits applied: FDC (CC0) + citable public sources only; FSSAI/Indian texts as NAMING sources only, never classification authority; no paid sources; no commodity dataset deciding a group; no Codex-derived bulk data; IFCT hook only; Open Food Facts reference only; licence recorded per source.

## 1. What this environment can reach (tested with plain GET, 2026-11-21)
| Host | Result | Note |
|---|---|---|
| fdc.nal.usda.gov | reachable | CC0; names only |
| fao.org (ca5644en.pdf) | reachable | already read |
| pmc.ncbi.nlm.nih.gov article pages and /search/ | reachable, but THROTTLED | about 10 rapid article fetches triggered a reCAPTCHA wall that also blocked pages read earlier; further reads must be spaced one at a time. I did not try to get around it |
| nupens.fsp.usp.br | reachable | descriptive pages only (read) |
| apps.who.int JECFA database | reachable | compound/additive monographs; not tested for vitamins/minerals |
| in./world.openfoodfacts.org | reachable | REFERENCE ONLY, never a vocabulary source |
| fssai.gov.in (home and PDF) | HTTP 502 on three URLs | would be NAMING only; may be transient, retry later |
| eutils.ncbi, Europe PMC, doi.org, Cambridge Core, worldnutritionjournal.org, bvsms.saude.gov.br, gov.br, PAHO IRIS, codexalimentarius.org, who.int, efsa.europa.eu, eur-lex | blocked by the proxy | an allowlist change needs your approval |

## 2. New candidate classification source found and partly read
Martinez Steele E, et al. "Identifying and Estimating Ultraprocessed Food Intake in the US NHANES According to the Nova Classification System of Food Processing", J Nutr 2022 Dec 15;153(1):225-241, doi 10.1016/j.tjnut.2022.09.001 (PMC10127522; authors from NUPENS/USP and NCI). Licence: the PMC page shows only a copyright/licence link; NOT verified, so short verbatim quotation only, as with the other PMC copies.
Verbatim, from its food-group table footnotes (the row labels were lost in my text extraction, so which group each footnote belongs to is inferred from order and must be confirmed against the table itself):
- footnote 2: "Including nuts and seeds (unsalted); yeast; dried fruits (without added sugars) and vegetables; nonpresweetened, non-whitened, non-flavored coffee and tea; coconut water and meat; homemade soup and sauces (with no underlying ingredients); flours; tapioca." (a non-ultra-processed unprocessed/minimally processed row)
- footnote 3: "Including honey, molasses, and maple syrup (100%)." footnote 4: "Including unsalted butter, lard, and cream."
- footnote 5: "Including starches; coconut and milk cream; unsweetened baking chocolate, cocoa powder and gelatin powder; vinegar; baking powder and baking soda."
- Text: "food substances of no or rare culinary use (such as high fructose corn syrup, hydrogenated oils, modified starches and protein isolates)"; Group 4 breads "when, in addition to wheat flour, yeast, water, sugar, and salt, their ingredients include substances that are not used in culinary preparations, such as hydrogenated vegetable fat, whey, emulsifiers, and other additives"; branded corn flakes coded ultraprocessed from their ingredient lists (malt flavour, high fructose corn syrup), "although some brands might be processed" (this supports keeping bare `corn flakes` parked).
What it could unlock among parked terms, IF you accept it as a NAMING-and-placement source (my reading, to confirm): cocoa powder (unsweetened) and starches sit with the culinary-ingredient footnote; yeast and flours sit with the unprocessed/minimally processed footnote; whey is named as a non-culinary substance. Caveat: `starch`/`tapioca starch` are a standing lexicon-1 exclusion and `yeast extract` a standing non-marker decision (yeast is not yeast extract); neither changes without your decision.

## 3. Sources NOT yet findable or readable
- Other open NOVA papers (Monteiro 2010 Cad Saude Publica; Monteiro 2016 World Nutrition; Louzada, Baraldi, Machado food-coding papers): the PMC search returned ~35 candidate ids but I could not read them after the throttle. A slow, one-at-a-time read is the next step if you approve; each needs its licence recorded.
- Indian naming (maida, khand, jowar, roasted gram, pipal): only FSSAI-type texts would do; unreachable now.

## 4. Proposed next actions (no row until you agree)
1. Confirm the table row labels for footnotes 2-5 of PMC10127522 (a slow single read of the table), record the licence if visible, then decide whether it is admissible as a placement source for cocoa powder, yeast and flours (rows would still be PROVISIONAL, and the standing exclusions stay).
2. Retry FSSAI later; if it stays down, tell me whether you can allow a mirror or want an alternative naming source.
3. Space out further PMC reads (one every few seconds, stop at the first challenge page).

# Decision record (owner, 2026-11-21) and confirmed row labels
- PMC10127522 is ADMISSIBLE as a CORROBORATING placement source only, under these conditions: read-only, no bulk import of its tables; rows cite it by identifier with "licence unverified" and PARAPHRASE its coding (no verbatim excerpt beyond a few words); never the sole support for a placement that contradicts or extends beyond FAO 2019 / Monteiro: then park and flag; its context is dietary-recall items, so label-context conditions still apply.
- Footnote row labels CONFIRMED from the article's table markup (not inferred): footnote 2 belongs to "Other unprocessed or minimally processed foods"; footnote 3 to "Table sugar" (under Processed culinary ingredients); footnote 4 to "Animal fats"; footnote 5 to "Other processed culinary ingredients"; footnote 6 to "Other processed foods".
- FSSAI stays blocked (no circumvention); if it becomes reachable it is NAMING-only. No alternative Indian naming source was reachable without circumvention; none used.
- The reachable/blocked host lists above are the merged evidence for this survey. First application: evaluation/pmc_reresearch_1/.
