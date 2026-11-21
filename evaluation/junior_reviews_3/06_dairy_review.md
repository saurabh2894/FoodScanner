# Senior review: antigravity/class-bulk-6-dairy (FDC 'Dairy and Egg Products'); docs only, no staging

Reviewed head bbc0fb8 (one commit on base 22966c8). Decision reference: owner instruction 2026-11-21 (review only; staging waits for owner verification). The branch is named class-bulk-6-dairy; the instruction's 'class-bulk-4-dairy' is read as that branch (the pin below matches its file).

## 0. Boundary check
| check | result |
|---|---|
| merge-base with stated base (STATUS.md `base=22966c812b49...`) | 22966c8 (equal); one commit |
| `git diff --name-only 22966c8...bbc0fb8` | 6 paths, all under `evaluation/class_bulk_6_dairy_1/` (README, STATUS, accept_records, queue, reject, source_rules); no path outside the folder; no source, resource or ingest file |
| classification verdicts by the junior | none in code or resources; the CSVs carry candidate dispositions only |
| `accept_records.csv` sha256 (raw blob bytes, 6488 bytes) | `f7fc91f06535b82a233fe1dd890daeda0c962ca0f77e15fd669e0ca604f9c86f`; equals the pin |

## 1. Counts reproduced
341 candidates = 19 accept / 223 queue / 99 reject (291 SR Legacy + 50 Foundation), equal key for key to the cached FDC category 'Dairy and Egg Products'; no duplicates, none missing or extra; 341/341 names equal the raw FDC descriptions; queue and reject reason-code counts match the junior README. Accept split: 10 canonical (milk, eggs, buffalo milk and milk powder already covered; 6 new: sheep milk, human milk, duck, goose, quail and turkey eggs).

## 2. Quotes
Verified verbatim in ca5644en: "fresh, powdered or pasteurized milk"; "fresh, powdered, chilled or frozen eggs"; "fresh or pasteurized plain yoghurt"; "simple cheeses to which salt is added"; "freshly made unpackaged breads and cheeses"; the minimal-processing sentence; the whey/casein sentence (source uses typographic single quotes around 'mechanically separated meat'; text otherwise identical); the butter quote joins two passages with an ellipsis, the second half ("Also includes products consisting of group 2 items, such as salted butter") is verbatim. Not verified as a quote: "Fruit yogurt or yogurt with added sugar/flavors is ultra-processed (Group 4)" (p. 8 / 10) is a paraphrase; the source lists 'fruit yoghurt' among ultra-processed examples and the 'added sugar/flavors' wording is not in that passage. Page labels were not re-derived here. Every accept row cites only the two verified Group 1 clauses, which pass.

## 3. Accept records: senior disposition (19)
| records | senior |
|---|---|
| milk: 171266, 172205, 172217, 173432, 173441; buffalo milk 171280; eggs 171287, 172202, 323604, 748967 | existing rows (`milk`, `buffalo milk`, `eggs`); evidence only, no change |
| nonfat dry milk 170877, whole dry milk 173454 | existing behaviour (see question a); no row |
| instant nonfat dry milk 172196 | **hold (queue)**: the standing milk-powder exception abstains on instant forms; the junior collapsed 'instant' into the canonical |
| human milk 171279 | **hold (queue)**: outside the milk rows since per-form-2b (owner exclusion); the junior quotes the same species-silent clause, which does not settle it |
| sheep milk 170882 | stage candidate: class-instance of the FAO animal milk, same level as goat milk (the species is not named by a source read) |
| duck 172189, goose 172190, quail 172191, turkey 172192 eggs | stage candidates: class-instance of FAO eggs; names state whole, fresh, raw |

Weaker evidence noted: 748967 'Eggs, Grade A, Large, egg whole' states only 'whole' (raw is not in the name); the canonical `eggs` has three records with 'raw' in the name, and the row exists already.

## 4. Question (a): 'skimmed milk powder' -> 'milk powder' against the Q10 powder precedent
Measured on main (46ad81c), `Ingredients: X.`:

| input | result |
|---|---|
| skimmed milk powder / whole milk powder / toned milk powder / buffalo milk powder | Group 1, driver "powdered milk (FAO Table 1 Group 1: 'fresh, powdered or pasteurized milk')" |
| skim milk powder / nonfat dry milk / instant skimmed milk powder | abstain (not in the local vocabulary) |
| milk solids | Group 1 (an existing PROVISIONAL row, 'single recognised unprocessed food') |
| Milk solids (Pasteurized skimmed cow milk) | abstain (Q10; bracket content on a whole_food head that is not plain milk) |

Reading: the precedent is the exact-named clause 'powdered milk', not a milk-solids rule. A powder of milk (whole, skimmed, toned, buffalo; nothing else listed) is dried milk, so it falls under the clause; a fraction ('milk solids') is a different term and Q10 abstains on its own bracket evidence. The precedent therefore genuinely covers records 170877 and 173454, and it already does so in the engine: no row or synonym is needed, and nothing is staged for them. It does **not** cover 172196 (instant), nor 'nonfat dry milk' as a label wording: FDC equates 'nonfat' with 'skim' only for fluid milk (173432, "fat free or skim"), not for the dried record, so 'nonfat dry milk' -> 'milk powder' is a naming inference and stays a synonym candidate to be sourced. Open measurement for you: `skim milk powder` abstains today because `skim milk` is not a recognised head (only 'skimmed' resolves) although the exception's word list allows 'skim'; the junior's `skim milk` -> `milk` synonym candidate would close that and rests on the same FDC fluid-milk naming.

## 5. Question (b): 'dairy' and 'egg' kinds
The repo has no 'dairy' or 'egg' kind. Existing milk, toned milk, double toned milk, buffalo milk, milk solids, dahi, egg and eggs are all `whole_food`. Proposed mapping: dairy -> `whole_food`, egg -> `whole_food`, one to one, no new kind. Consequences to measure at staging, not now: (1) the `whole_food` unrecognised-bracket guard already applies (measured: `eggs (duck eggs)` and `milk (sheep milk)` abstain, as `rice (cow milk)` does); (2) the species-of-origin bracket rule and the milk-powder route are keyed to the milk rows in `classify.py` (`_MILK_TERMS`, `_MILK_POWDER_ROWS`, `_MILK_POWDER_WORDS`), so a `sheep milk` row would answer Group 1 plain but `sheep milk powder` and `milk (sheep milk)` would stay abstain unless that constant is extended (an engine change, proposed separately as for goat milk); (3) the powder standard abstains on `duck egg powder`. Nothing is held for taxonomy reasons.

## 6. Queue/reject consistency (overlap words)
Overlap tokens are mostly product nouns (cheese, cream, yogurt, egg). Two real inconsistencies, one deterministic rule each:
- **Fruit/flavoured yoghurt.** The junior rejected 22 flavoured yoghurts (vanilla, strawberry, chocolate, sweetener) but queued 22 fruit or fruit-flavoured ones (fruit variety, Chobani fruit lines, 'with low calorie sweetener'). Rule: a yoghurt or kefir whose name carries a fruit, flavour or sweetener word is flavoured -> reject; plain -> queue. 22 records move queue -> reject.
- **Poached and boiled eggs.** 172186 (poached) and 173424 (hard-boiled) were rejected as cooked; poaching and boiling are FAO-listed minimal processes, the same call as the boiled nuts. Fried, scrambled and omelette stay reject (fat or other items). 2 records move reject -> queue.

| measure | junior | senior |
|---|---|---|
| accept: existing row or behaviour, no change | 14 (as 'already covered') | 12 |
| accept: stage candidates | 5 | 5 (sheep milk, 4 avian eggs) |
| queue (incl. 2 held accepts) | 223 | 205 |
| reject | 99 | 119 |
| total | 341 | 341 |

Per-record dispositions: `06_dairy_dispositions.csv`.

## 7. Parked observations (not acted on; for the owner)
- Plain yoghurt: the clause names 'fresh or pasteurized plain yoghurt'; 13 plain yoghurt and kefir records sit in the queue and the repo has no plain-yoghurt row (`dahi` exists). A row or the milk-plus-culture route is an owner decision.
- Powdered whole egg: the clause names 'powdered ... eggs'; 'Egg, whole, dried' (172188, 329490) is queued 'per-form pending'. Today `egg powder` abstains (powder standard) while `dried egg` answers Group 1. The glucose-reduced, stabilised record (173425) is a processed form and stays queued. An egg-powder exception parallel to milk powder is an owner decision.
- Butter and salted butter: FAO names salted butter in Group 2; the junior rejects 'Butter, salted' as salted. Not relevant to staging.
- Cheese (111 records), cream, ghee, paneer, buttermilk, whey/casein, condensed/evaporated, fortified milks: queue, untouched.
