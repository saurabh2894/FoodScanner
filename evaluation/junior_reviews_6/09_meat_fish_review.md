# Senior review (boundary and first findings): antigravity/class-bulk-9-meat-poultry and class-bulk-10-fish-seafood (Task 14 repairs); docs only, no staging

Candidates, not usable coverage. Decision reference: owner instruction 2026-11-21 (boundary check and senior review; no app staging). Status: boundary, totals, identity checks and the first findings are done; items marked OPEN below are not yet reviewed (quota), and no completion is claimed.

## 0. Boundary check
| item | meat | fish |
|---|---|---|
| tip actually fetched | 00f504c | 7fbdc9d |
| named repair commit | 8b47c44 (an ancestor) | 30c2fa5 (an ancestor) |
| tip vs repair commit | STATUS.md only | STATUS.md only |
| stated base / merge-base | c0ece2b / c0ece2b | 46ad81c / 46ad81c |
| paths vs merge-base | 8, all status A, all under `evaluation/class_bulk_9_meat_poultry_1/` | 8, all status A, all under `evaluation/class_bulk_10_fish_seafood_1/` |
| source or runtime paths changed | none | none |
| `canonical_candidates.csv` sha256 (raw blob bytes) | `a1c3eb6c9a78fca045697a79549cc24e3bea4c9648665c6d4277362c8777e245` = pin | `e3835c3a2ad1fe9d3209fdb5cc7f5d4935e7627add736cb41549f9ee4ba0e65d` = pin |
(`accept_records.csv` raw hashes, for the record: meat `a3c100c7...`, fish `ca08e13c...`.)

## 1. Reproduced mechanically (own run against the cached FDC files)
| check | meat | fish |
|---|---|---|
| records in scope = category filter, key for key | 2179 (Beef 975, Lamb/Veal/Game 466, Poultry 395, Pork 343) | 288 (Finfish and Shellfish) |
| disposition rows unique and equal to the universe | yes | yes |
| accept / queue / reject = dispositions, no overlap | 1649 / 242 / 288 | 149 / 80 / 59 |
| every record name equals the raw FDC description | 2179/2179 | 288/288 |
| canonical rows, supporting-ID unions equal to accept IDs per canonical, counts | 8 rows, exact | 68 rows, exact |
| excerpts in `exact_source_excerpts` equal the raw names | 24/24 | 128/128 |
| existing lexicon or synonym matches for the canonical labels | none (only `egg` exists) | none |

## 2. Findings (senior owns recoverable wording and identity fixes)
1. **Spliced 'definition' still in the meat rules.** `source_rules.md` (meat) still carries a 'Verbatim Group 1 Definition Clause (Table 1, p. 11)' that splices a section-2 prose sentence ("Unprocessed (or natural) foods are the edible parts of plants (such as fruit, leaves, ...) or from animals (such as muscle, offal, eggs, milk), and also fungi, algae and water, after separation from nature.") with a Table 1 process list: the same defect as the beverages batch. The README says the animal-food definition is now quoted separately, so the repair is internally inconsistent. The canonical rows quote "edible parts ... from animals (such as muscle, offal, eggs, milk)" with an ellipsis: the words 'such as muscle, offal, eggs, milk' are verbatim from the report prose, whereas the Table 1 Group 1 cell reads "Edible parts of plants (fruit, seeds, leaves, stems, roots, tubers) or of or from animals (muscle, fat, offal, eggs, milk), and also fungi, algae, all after separation from nature." Offal is named in both, but the locator 'Table 1 definition p. 11' is wrong for the 'such as' wording and the ellipsis joins two passages: not a continuous verbatim quote.
2. **Verified verbatim:** the examples clause "meat, poultry, fish and seafood, whole or in the form of steaks, fillets and other cuts" (right column of the Group 1 cell; the cell breaks the lines after 'fish' and 'steaks,'); the Group 3 example "salted, dried, cured, or smoked meats and fish; canned fish (with or without added preservatives)"; the Group 4 example list with 'nuggets' and 'sticks', sausages, burgers, hot dogs, reconstituted meat products; the Group 2 'butter and lard obtained from milk and pork'.
3. **Meat accepts that should not be accepted (39 records, all moved to queue; `09_meat_fish_senior_changes.csv`):**
   - 169157 'Pork, pickled pork hocks': pickled is a preserved form.
   - 170600 'Beef, sandwich steaks, flaked, chopped, formed and thinly sliced, raw': a restructured form.
   - 37 ground records (e.g. 'Beef, ground, 70% lean meat / 30% fat, raw', 'Pork, ground, 84% lean / 16% fat, cooked, crumbles', 'Turkey, ground, fat free ...'): the junior queued 17 ground records as 'ground_form_unstated' (source-silent) but accepted these because a lean/fat percentage is stated. Grinding is a named minimal process, but a stated percentage does not show that nothing was added or which cuts were combined; one rule for the form: queue all ground records until a per-form decision.
   Meat after these changes: accept 1610, queue 281, reject 288; the 8 canonical rows keep supporting records (see item 8 for the next change).
4. **'Biological class-instance' wording.** The junior describes beef, chicken and the fish labels as biological species. No source read resolves taxonomy; the labels (beef, lamb, pork, chicken, veal, turkey, duck, goose; butterfish, ling, monkfish, bluefin tuna, ...) are source-stated food labels, class-instance of the named class (meat, poultry, fish and seafood), never NAMED, no taxonomic resolution. Descriptor absence ('no added salt' in a name) is not an ingredient guarantee: SR Legacy names are commodity descriptors and no purity claim may be carried into a row.
5. **Snow crab / queen crab (fish).** The `snow crab` canonical rests on FDC 171969 and 172008 ('Crustaceans, crab, queen, raw / cooked, moist heat') and 2747670 ('Snow crab, legs only, frozen'). The README states queen crab and snow crab (Chionoecetes opilio) are reconciled; no source read in this review shows that equivalence and the FDC names do not state it. Senior: the two queen-crab records keep their own exact label `queen crab` (68 canonical rows stay 68: `snow crab` is replaced by `queen crab`), the alias is held, and 2747670 (raw or cooked not stated; a different label) moves to queue. Fish after senior changes: accept 148, queue 81, reject 59.
6. **Other fish labels:** `spot croaker` is the junior's label for records named 'Fish, spot'; the source term is 'spot', so the label is relabelled `spot` (alias held). `mahimahi`, `walleye pike` (record 'Fish, pike, walleye'), `greenland halibut`, `atlantic pollock`, `ling`, `lingcod`, `butterfish`, `monkfish`, `bluefin tuna` are source-stated labels, class-instance only; no species merge by inference.
7. **Positively checked, no change:** no accepted record in either set carries fried, smoked, kipper, canned, breaded, cured, salted, dried-and-salted, moisture-added, broth or gravy wording (own scan over all 1649 + 149 names). Generic fish (18) and ground beef 172161 are queued as the owner described. Wild/farmed, frozen wild-caught and 'previously frozen' fish records are physical-state descriptors; kept, with the descriptor-only caveat.

8. **False rejects in the meat rejects (found by scanning reject and queue names without a condition word):** 8 New Zealand beef records (173075, 173076, 173099, 173100, 173101, 173102, 174719, 174720: chuck eye roll and cube roll) are rejected as 'added seasonings, sauce, commercial formulation, or prepared product (roll,)': the junior keyword 'roll' matched a cut name. The names state plain cuts (separable lean, raw or cooked braised or fast roasted). Senior: reject -> accept candidate (recoverable). The other no-condition-word rejects are consistent with their reasons (two HORMEL 'ALWAYS TENDER' fresh pork records are branded enhanced product; five rotisserie BBQ chicken records are seasoned). The no-condition-word queues are source-silent game, squab and guinea hen (queue stays) or generic or mixed-species fish (queue stays).
   Meat after items 3 and 8: accept 1618, queue 281, reject 280 (total 2179); fish: accept 148, queue 81, reject 59 (total 288).

## 3. OPEN (not yet reviewed; not claimed)
- Row-by-row reading of the meat and fish rejects and queues for overlap words and one deterministic disposition: only the accepts (condition words) and the reject and queue names WITHOUT a condition word were scanned (item 8); rejects that do carry a condition word are not yet read one by one.
- Group-class fit per canonical (pork is also named in the Group 2 'lard' clause; offal grounding) and per-record `plain_form_evidence` strings against the cached names.
- Cooked forms (roasted, braised, stewed, simmered, grilled, broiled, boiled): kept as accepted here because boiling and roasting are listed minimal processes; the per-form decision is the owner's.
- Yield for a future staging proposal: existing 0; new candidates 8 meat + 68 fish canonical labels; held: ground forms, game and rare species, goat and mutton, fried methods, separable fat and skin, generic fish and shellfish names (shrimp, lobster tail, catfish, halibut, tilapia, carp, ...). Generic label words such as 'fish', 'shrimp', 'prawn' and 'mutton' would remain unrecognised.

No app staging is proposed. Next step after the 21:00 reset: finish section 3, then publish the staging proposal only after the owner verifies this review.
