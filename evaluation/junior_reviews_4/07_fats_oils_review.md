# Senior review: antigravity/class-bulk-7-fats-oils (FDC 'Fats and Oils'); docs only, no staging

Reviewed head 1b015d2 (one commit on stated base 79e3f19). Decision reference: owner instruction 2026-11-21 (review only; no staging until verified).

## 0. Boundary check
| check | result |
|---|---|
| merge-base with stated base (STATUS.md `base=79e3f1981ed1...`) | 79e3f19 (equal); one commit |
| `git diff --name-status 79e3f19...1b015d2` | 6 paths, all status A (additions only), all under `evaluation/class_bulk_7_fats_oils_1/`: README, STATUS, accept_records, queue, reject, source_rules; no path outside the folder |
| `accept_records.csv` sha256 (raw blob bytes, 19375 bytes) | `5e4ebb7aae03cdd760f2dad7fdd7c2e9490d779a73cbf98a5eb4ecfd61e6162c`; equals the pin |
| classification verdicts / kinds | the junior's `suggested_kind` is `culinary` for all 50 accepts: an existing repository kind (Group 2 single-item); no kind is invented |

## 1. Counts reproduced
228 candidates = 50 accept / 16 queue / 162 reject (216 SR Legacy + 12 Foundation), equal key for key to the cached FDC category 'Fats and Oils'; no duplicates, none missing or extra; 228/228 names equal the raw FDC descriptions; queue and reject reason counts match the junior README. Accept split: 32 canonical = 11 already rows (cocoa butter, coconut oil, cottonseed oil, mustard oil, olive oil, palm oil, peanut oil, rice bran oil, sesame oil, soybean oil, sunflower oil; all `culinary`) + 21 new.

## 2. Quotes (FAO ca5644en)
All pass verbatim: Group 2 definition ("Substances obtained directly from group 1 foods or from nature by industrial processes such as pressing, centrifuging, refining, extracting or mining. Used to prepare, season and cook group 1 foods. May contain additives that prolong product duration, protect original properties or prevent proliferation of microorganisms."); Group 2 examples ("Vegetable oils crushed from seeds, nuts or fruit (notably olives); butter and lard obtained from milk and pork; ... vegetable oils with added anti-oxidants; ... Also includes products consisting of group 2 items, such as salted butter, ..."); section-2 prose ("Processed culinary ingredients include oils, butter, lard, sugar and salt." and the two following sentences); Group 4 ("Ingredients include sugar, oils or fats, or salt, generally in combination, and substances ... such as high fructose corn syrup, hydrogenated or interesterified oils, and protein isolates"; "margarines and other spreads"); "hydrogenated or interesterified oil. The presence in the list of ingredients of one or more of these food substances identifies a product as ultra-processed." Ellipses mark joins; page labels not re-derived. Every accept row cites only the Group 2 'Vegetable oils crushed from seeds, nuts or fruit (notably olives)' clause, which passes.

## 3. Findings
1. **Plain-form evidence overstated.** The junior writes 'pure single-ingredient X oil' as plain-form evidence. No FDC record name states purity or an ingredient list; the record names only 'Oil, X'. For Group 2 that is enough (the definition covers oils pressed or extracted from group 1 foods, refined, even with added antioxidants), but 'pure' is not a verified statement and must not enter row provenance.
2. **'industrial' is split across all three dispositions.** Accepted: 171042 (industrial canola high oleic), 171438 and 171439 (industrial soy low/ultra-low linolenic), 172357 (industrial mid-oleic sunflower). Rejected as 'industrial_oil_mix': 172359 (industrial canola for salads, woks), 173598 (industrial soy refined, for woks); rejected as 'whipped_spray': 173595 (industrial coconut, principal uses candy coatings). The word is a US trade/use designation of the FDC record, not an identity, and no source read treats it as one: US-only designation and composition cannot establish placement. One deterministic rule: a record named 'industrial' (not 'industrial and retail'), with no named added substance and no hydrogenation, is queued (`queue_industrial_grade`); conditioned records (172358 'with antifoaming agent'; hydrogenated; shortenings; margarines) stay reject. Also held: 171033 'Natreon canola, high stability, non trans, high oleic (70%)' (a brand and composition designation). Result: 5 accepts held (171042, 171438, 171439, 172357, 171033), 3 rejects moved to queue. No canonical loses support: canola, soybean and sunflower oil keep other plain records.
3. **Lard queued although exact-named.** The junior's own table marks lard 'Exact-named' ('butter and lard obtained from milk and pork'; 'oils, butter, lard') yet queues FDC 171401 'Lard' under animal fat. Senior: accept as a stage candidate, `culinary`, inference level exact-named. Other animal fats (beef tallow, chicken, turkey, goose fat, bacon grease) are not named: queue, class-instance only and unsourced as to culinary use.
4. **Grain and germ oils.** Wheat germ oil and oat oil are not 'seeds, nuts or fruit' examples; placement rests on the general Group 2 definition (obtained directly from a group 1 food by pressing/extracting/refining). Inference level for these two: class-instance of the definition, not of the example list.
5. **'Butter' name collision.** Nutmeg butter and ucuhuba butter are plant fats; the clause names butter 'obtained from milk'. They stay candidates as class-instance vegetable fats; a label 'nutmeg butter' lands in the same Group 2 either way. The junior's synonym candidates (shea butter -> sheanut oil, rapeseed -> canola, maize -> corn, extra virgin/virgin/extra light olive oil -> olive oil, flax seed oil, tea seed oil, cupuacu) are naming-only (FDC does not name them) and stay parked until sourced.
6. **Olive oil 'exact-named'.** The clause names olives as the source ('notably olives'), not the term 'olive oil'; accepted as exact-named in the sense of the named source fruit; recorded as such.
7. **Queue items**: fish oils (five) and animal fats are source-silent for a culinary placement; fat fractions and confection fats (soy lecithin, 'industrial' coconut/palm kernel confection fats) are separate decisions; dairy butter 'light' (172344, 173581): the clause names butter and salted butter, an existing `butter` row covers plain butter; the 'light' (reduced-fat) records are composition grades and stay queued.

## 4. Reconciled counts
| measure | junior | senior |
|---|---|---|
| accept: existing rows, no change | 11 canonical (records not split) | 20 records |
| accept: stage candidates | 21 canonical | 22 canonical (21 + lard), 26 records |
| accept held (industrial/brand) | 0 | 5 records |
| queue | 16 | 23 (16 - lard + 5 held + 3 moved) |
| reject | 162 | 159 |
| records | 50 / 16 / 162 | 46 accept (20 + 26) / 23 queue / 159 reject = 228 |

Per-record dispositions: `07_fats_oils_dispositions.csv`.

## 5. For the staging decision (not started)
Rows would be kind `culinary` (existing), so they take Group 2 as a single item. Items to measure at staging: a Group 1 food plus an oil row in a list (Group 3 combination), oil rows inside brackets of nuts/seeds (`walnuts (walnut oil)` would read the oil as a recognised culinary substance in the nut's own bracket), and the powder/descriptor surfaces. No synonym, marker or classifier change is proposed.
