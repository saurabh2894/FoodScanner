# per_form_1: roasted/toasted plain grains, whole_food unknown-bracket safeguard, species-of-origin milk provenance (round 2; ready for review; NOT merged)

Branch claude/per-form-1 off main 22966c8. Round 2 = the owner's hold (species-of-origin), amendment 1 (Q10 on its own evidence; salted-grain surface) and amendment 2 (narrowed `toasted`).

## 1. Per-row provenance (single row-level table)

| item | table / code | status | source (verbatim) | inference level | condition kept |
|---|---|---|---|---|---|
| `roasted` | descriptors.csv (existing global row, UNCHANGED by this branch) | exact-named method | FAO 2019 ca5644en p.6 (printed): "Minimally processed foods are natural foods altered by methods that include removal of inedible or unwanted parts, and also processes that include drying, crushing, grinding, powdering, fractioning, filtering, roasting, boiling, non-alcoholic fermentation, pasteurization, chilling, freezing, placing in containers, and vacuum packaging." | exact-named ('roasting') | unchanged and not widened or narrowed here (it is broad: `Roasted Milk` is Group 1, pre-existing) |
| `toasted` | descriptors.csv NEW row, kind-scoped (`kinds` = whole_food;flour) plus a CLOSED TERM SET in `classify._SCOPED_TERMS` (mirrored in `foodscan.js`) | PROVISIONAL | the same p.6 sentence | INFERENCE: toasting read as the same dry-heat method as the named 'roasting' | narrowed by owner amendment 2: strips ONLY when the remaining name is one of the 23 Batch-4 terms and carries no other qualifier |
| unknown-bracket abstention | `classify._RESIDUAL_EXTRA_KINDS` = (flour, whole_food) | code rule | owner ruling: an item with a bracket naming content the vocabulary does not recognise cannot be answered Group 1 | intended attributed change class (`Rice (XQ9)` 1 -> abstain) | benign parts: recognised foods, descriptors, condition words, negations, connectors, digits/codes, and the species rule below |
| species-of-origin provenance | `classify.bracket_residual` (inside the bracket-benign check) | code rule | owner decision (this branch's hold message, verbatim in section 3) | provenance only, never a placement | exact final rule in section 3 |

**Closed `toasted` term set (exactly the 23 canonical terms Batch 4 placed; `tests/test_per_form_1.py` asserts it equals `evaluation/class_bulk_4/grains/staged_rows.csv`):**
- 9 grain whole_food terms: barley, black rice, buckwheat, millet, parboiled rice, red rice, rice, sorghum, wild rice (`red rice` and `parboiled rice` resolve to the row `rice` through the global descriptors).
- 14 flour terms: amaranth flour, barley flour, buckwheat flour, cornmeal, millet flour, oat flour, quinoa flour, rice flour, rye flour, semolina, sorghum flour, spelt flour, wheat flour, whole wheat flour.
- Refusals: any name with another qualifier abstains (salted, sugar/sugared/sweetened, honey, flavoured, oiled, fried, spiced, masala: none is in the benign list {unsalted, organic, whole, plain, pure, white, brown, red, common, edible}); global descriptors are NOT stripped on this path (`Toasted Rolled Oats`, `Toasted Parboiled Rice` abstain); `Toasted Milk`, `Toasted Egg`, `Toasted Almonds` and every other row abstain. Note: the flour terms include flours (oat, rye, spelt, quinoa, amaranth, wheat) whose whole grain is not itself a Batch-4 whole_food row; they are in the set because your own control `Toasted Oat Flour` requires oat flour.

`toasted` surface under the narrowed scope (re-measured on the committed trees, '<word> <term>' for all 384 lexicon rows): **768 probed, 21 changed** (toasted / flour: 14, toasted / whole_food: 7); every change is None -> Group 1 and inside the explicit set; changes outside it: []; group moves other than None -> 1: 0. `roasted` surface: 0 changes.

## 2. Parked (NOT implemented; no rows)

| term | runtime | park reason (owner ruling) |
|---|---|---|
| `enriched flour` / `fortified X` | unrecognised, abstains | a US standard of identity (21 CFR 137.165) does not establish compliance or an identical meaning for an unqualified term on an Indian or unknown-jurisdiction label, and composition alone does not establish replacement purpose; unresolved |
| sprouted anything | recognised by name only (unplaced) | no positive placement evidence (identity unverified at primary) |
| `pearled barley` | unrecognised, abstains | no applicable grain-processing clause |
| `Vitamins and Minerals` standalone | recognised by name only, abstains | unresolved; abstention stands |
| a salted-grain guard | pre-existing | recorded for a later batch (section 5) |

## 3. Species-of-origin provenance: owner decision (verbatim) and the exact final rule

> Species-of-origin words in brackets are benign provenance when they modify a recognised milk term (owner decision, this message is the decision record). ... a species word from the explicit closed set {cow, buffalo, goat} is treated as recognised provenance ONLY when the same bracket also contains a recognised milk/dairy term (e.g. 'milk', 'milk solids'). Mechanism: resolve these inside the bracket-benign check, NOT as lexicon rows and NOT as globally recognised words.

**Amendment 1 (verbatim core):** "'milk solids' is not necessarily identical to milk, and a bracket naming 'pasteurized skimmed cow milk' is at most composition evidence whose fit must be established, not assumed ... restore Group 1 only if an actual source you can quote places that exact form ... If no source establishes it, Q10 stays abstain."

**Exact final rule** (`classify.bracket_residual`, mirrored in `foodscan.js`): a bracket part is benign provenance iff ALL hold: (1) the HEAD item is a recognised plain milk item: lexicon row kind `whole_food` and term in {milk, toned milk, double toned milk, buffalo milk} (`milk solids` is EXCLUDED by amendment 1); (2) the part contains the word `milk`; (3) it contains at least one species word from the closed set {cow, buffalo, goat}; (4) every other word is a descriptor, a benign connector/condition word, or one of {milk, toned, double, solids}. The species words are not lexicon rows, not synonyms and not recognised words anywhere else (`cow milk`, `goat milk` and `cow` as ingredient names stay unrecognised). Scope choice recorded as you allowed: head-row restriction instead of trying to scope by bracket content alone (so `Rice (Cow Milk)` abstains).

**Where Q10 landed: ABSTAIN (attributed).** b3/Q10 `Milk solids (Pasteurized skimmed cow milk)`: Group 1 -> None, status unchanged, attributed to the whole_food unknown-bracket rule. Source search for a quote that places this exact form: FAO 2019 p.11 Table 1 Group 1 names milk by form: "fresh, powdered or pasteurized milk" (verbatim); it names neither milk solids nor a solids fraction, and the repo's own earlier ruling treats a solids fraction as not the named powdered-milk form (`milk solids powder` abstains). The `milk solids` lexicon row is PROVISIONAL on FSSAI wording only ('treated as dried or concentrated milk': no NOVA source). No source places it, so Group 1 would be an unjustified placement. The four frozen-input tests keep their explained updates (8ec340c state, unchanged since).

**Control deviation, stated plainly:** you listed `Goat Milk (Pasteurized)` -> 1. Under the rule as scoped (species words are never recognised words) the HEAD name `goat milk` is unrecognised, so it abstains (None -> None). Recognising `<species> milk` as a head name would be a global recognition and would move frozen inputs b2/M02 and b3/Q06, which contain `cow milk` as an item (the existing flip-harness test `test_flip_harness_detects_and_blocks_a_group_flip` proves that adding the term flips exactly those two). `Milk (Goat Milk)` -> Group 1 works. Say so if you want head-name recognition in a separate gated change.

## 4. Gate evidence (committed tree; BEFORE = worktree of main 22966c8; separate fresh processes)

| check | result |
|---|---|
| frozen 66 | changed 1 (b3/Q10, abstain, attributed); unexplained 0; abstain->4 0 |
| out-of-sample 32 | changed 0; unexplained 0; abstain->4 0 |
| drift (534 existing terms/synonyms alone) | 0 differences |
| descriptor surface (`roasted`, `toasted`) | 768 probed, 21 changed, all None -> 1 inside the explicit set |
| salted surface (`salted X`, `roasted salted X`, `toasted salted X` for all 47 whole_food/flour rows) | 141 probed, 0 changed, **0 newly Group 1** |
| powder surface (552 forms) | changed 0; bare X powder Group 1 after 0 (clean) |
| lexicon / synonyms / markers | 384 -> 384 rows, 0 added, 0 source-changed; synonyms.csv and markers.csv byte-identical |
| suite | 1559 passed, 5 xfailed |
| parity | 693/693 identical (additions-only: 653 + 40 inputs, 0 lines removed) |

**Salted surface, measured per form (before -> after):**

| form | rows probed | Group 1 before | Group 1 after | changed | newly Group 1 |
|---|---|---|---|---|---|
| `salted X` | 47 | 47 | 47 | 0 | 0 |
| `roasted salted X` | 47 | 47 | 47 | 0 | 0 |
| `toasted salted X` | 47 | 0 | 0 | 0 | 0 |

No form becomes newly Group 1 through the salted path, so no extra guard was needed in this batch. Measured-unchanged and pre-existing: `salted X` and `roasted salted X` are Group 1 for all 47 whole_food/flour rows both before and after (94 Group-1 answers; the global `salted` descriptor has no grain guard, e.g. `Roasted Salted Buckwheat`). The dedicated salted-grain guard batch stays parked (owner: recorded for a later batch). `toasted salted X`: 0 before, 0 after (the narrowed `toasted` refuses salted names).

## 5. Controls (applied_gate.json 'controls'; before -> after group)

| control | before | after |
|---|---|---|
| roasted buckwheat | 1 | 1 |
| roasted milk | 1 | 1 |
| toasted oat flour | None | 1 |
| toasted unsalted oat flour | None | 1 |
| toasted brown rice | None | 1 |
| toasted milk | None | None |
| toasted egg | None | None |
| toasted almonds | None | None |
| toasted salted oat flour | None | None |
| toasted sweetened oat flour | None | None |
| toasted honey oat flour | None | None |
| toasted flavoured oat flour | None | None |
| toasted oats | None | None |
| enriched wheat flour | None | None |
| fortified wheat flour | None | None |
| sprouted ragi | None | None |
| pearled barley | None | None |
| vitamins and minerals | None | None |
| rice (xq9) | 1 | None |
| oat flour (xq9) | None | None |
| milk (pasteurized cow milk) | 1 | 1 |
| milk (buffalo milk) | 1 | 1 |
| milk (goat milk) | 1 | 1 |
| milk (cow) | 1 | None |
| rice (cow milk) | 1 | None |
| goat milk (pasteurized) | None | None |
| milk solids (pasteurized skimmed cow milk) | 1 | None |
| mango powder | None | None |
| 100% mango powder | 1 | 1 |
| milk powder | 1 | 1 |

## 6. Exact diff vs main 22966c8

18 files (including this README): `data/ingest/class_grains_1.json`, `data/ingest/per_form_1.json`, `evaluation/class_bulk_4/README.md`, `evaluation/per_form_1/README.md`, `evaluation/per_form_1/applied_gate/applied_gate.json`, `evaluation/per_form_1/fao_p6_quote.txt`, `scripts/applied_gate.py`, `scripts/class_gate.py`, `scripts/parity_check.py`, `src/foodscan/classify.py`, `src/foodscan/resources/descriptors.csv`, `tests/test_per_form_1.py`, `tests/test_sweetener_foods_note.py`, `tests/test_thickener_emulsifying_salt_markers.py`, `tests/test_validate_batch.py`, `tests/test_vocab_gap_and_soybean.py`, `web_preview/foodscan.js`, `evaluation/per_form_1/README.md`. normalise.py, lexicon.csv, synonyms.csv, markers.csv: untouched.

