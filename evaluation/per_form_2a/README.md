# per_form_2a: salted-grain guard (ready for review; NOT merged)

Branch claude/per-form-2a off main 0ceb941. Scope: the 23 Batch-4 grain/flour terms. Nut, legume, vegetable and fruit guards and the global `salted` descriptor's other behaviour are untouched. Decision reference: owner decision 2026-11-21: salted-grain guard, source-qualified, Group 3 only where a quoted clause supports it.

## 1. Source qualification (FAO 2019 ca5644en; verified verbatim against the report text; table cells rebuilt from the column layout)

| # | location | quote (verbatim) |
|---|---|---|
| Q1 | p.7 (printed) prose | "They are made by adding salt, oil, sugar or other substances from group 2 to group 1 foods." |
| Q2 | p.9 (printed) prose | "Some of what are now ultra-processed foods were originally manufactured only with group 1 foods and salt or sugar or other substances from group 2, and thus would be classed in NOVA group 3 as processed foods." |
| Q3 | Table 1 Group 3 definition, p.12 (printed) | "Products made by adding salt, oil, sugar or other group 2 ingredients to group 1 foods, using preservation methods such as canning and bottling, and, in the case of breads and cheeses, using non- alcoholic fermentation." |
| Q4 | p.10 (printed) prose, bread | "Industrial breads made only from wheat flour, water, salt and yeast are processed foods, while those whose lists of ingredients also include emulsifiers or colours are ultra-processed." |
| Q5 | p.10 (printed) prose, plain cereals | "Plain steel-cut oats, plain corn flakes and shredded wheat are minimally processed foods, while the same foods are processed when they also contain sugar, and ultra-processed if they also contain flavours or colours." |
| Q6 | Table 1 Group 3 examples, p.12 (printed) | "Canned or bottled vegetables and legumes in brine; salted or sugared nuts and seeds" |

**What the clauses cover.** Q1, Q2 and Q3 state the rule in general terms: a Group 1 food with salt (a Group 2 substance) added is a Group 3 processed food. Q2 is the most direct: Group 1 foods plus salt are classed in NOVA group 3. Q6 shows the same logic on a cereal example (plain cereals minimally processed, the same foods processed with sugar added). Q5 shows wheat flour plus water, salt and yeast as a processed food. Flour is a Group 1 food named in the examples ("grits, flakes or flour made from corn, wheat, oats, or cassava"), so the rule applies to flours as written.

**What they do not cover (explicit).** No clause names a salted grain or a salted flour; the named salted analogues are nuts and seeds (Q4 examples), meats and fish, and bread (a baked product, not a salted flour). Q3 ties the definition to 'preservation methods such as canning and bottling' ('such as' is illustrative, and the same cell lists dry-salted nuts without canning). The clauses do not quantify salt, do not say whether the salt must be a preservation salt, and do not address a salt that is merely part of a seasoning. Hence the inference level below is 'class-instance of the stated rule', not 'named'. Q6 supports sugared cereals but sugar and oil on grains are NOT implemented here (batch scope: salt).

## 2. What was implemented

`classify.grain_added_salt` (mirrored in `foodscan.js`): an item whose row kind is whole_food or flour AND whose resolved row term is one of the 23 Batch-4 terms (the same closed set as `_SCOPED_TERMS`) AND whose OWN name or bracket carries `salt` or `salted` (negations 'unsalted', 'no added salt', 'salt free' are not matched) takes **Group 3**, driver: "grain or grain flour with added salt (FAO: group 1 foods with salt added are classed in NOVA group 3 as processed foods; inference: no clause names a salted grain)". In a longer whole_food list the item contributes a Group 2 substance on a Group 1 food (same combination rule as salted nuts); the existing flour-list rule still abstains for flour lists. Markers keep priority. Where a clause did not support a placement the design would have abstained with a reason; here Q1-Q3 support Group 3, so no abstain-unresolved outcome was needed for the in-scope terms. Flours are included because Q1-Q3 cover Group 1 foods as a class and flour is named Group 1; this is a stated judgement (one constant, `_SCOPED_TERMS`, would exclude them).

## 3. Per-row provenance (single row-level table; the 23 in-scope terms)

| term | resolved lexicon row | kind | `salted X` / `roasted salted X` (before -> after) | clauses | inference level |
|---|---|---|---|---|---|
| amaranth flour | amaranth flour | flour | Group 1 -> Group 3 | Q1, Q2, Q3 | class-instance of the stated rule; not named |
| barley | barley | whole_food | Group 1 -> Group 3 | Q1, Q2, Q3, Q6 | class-instance of the stated rule; not named |
| barley flour | barley flour | flour | Group 1 -> Group 3 | Q1, Q2, Q3 | class-instance of the stated rule; not named |
| black rice | black rice | whole_food | Group 1 -> Group 3 | Q1, Q2, Q3 | class-instance of the stated rule; not named |
| buckwheat | buckwheat | whole_food | Group 1 -> Group 3 | Q1, Q2, Q3, Q6 | class-instance of the stated rule; not named |
| buckwheat flour | buckwheat flour | flour | Group 1 -> Group 3 | Q1, Q2, Q3, Q5 | class-instance of the stated rule; not named |
| cornmeal | cornmeal | flour | Group 1 -> Group 3 | Q1, Q2, Q3 | class-instance of the stated rule; not named |
| millet | millet | whole_food | Group 1 -> Group 3 | Q1, Q2, Q3, Q6 | class-instance of the stated rule; not named |
| millet flour | millet flour | flour | Group 1 -> Group 3 | Q1, Q2, Q3 | class-instance of the stated rule; not named |
| oat flour | oat flour | flour | Group 1 -> Group 3 | Q1, Q2, Q3, Q6 | class-instance of the stated rule; not named |
| parboiled rice | rice (via global descriptor) | whole_food | Group 1 -> Group 3 | Q1, Q2, Q3 | class-instance of the stated rule; not named |
| quinoa flour | quinoa flour | flour | Group 1 -> Group 3 | Q1, Q2, Q3 | class-instance of the stated rule; not named |
| red rice | rice (via global descriptor) | whole_food | Group 1 -> Group 3 | Q1, Q2, Q3 | class-instance of the stated rule; not named |
| rice | rice | whole_food | Group 1 -> Group 3 | Q1, Q2, Q3, Q6 | class-instance of the stated rule; not named |
| rice flour | rice flour | flour | Group 1 -> Group 3 | Q1, Q2, Q3 | class-instance of the stated rule; not named |
| rye flour | rye flour | flour | Group 1 -> Group 3 | Q1, Q2, Q3 | class-instance of the stated rule; not named |
| semolina | semolina | flour | Group 1 -> Group 3 | Q1, Q2, Q3 | class-instance of the stated rule; not named |
| sorghum | sorghum | whole_food | Group 1 -> Group 3 | Q1, Q2, Q3, Q6 | class-instance of the stated rule; not named |
| sorghum flour | sorghum flour | flour | Group 1 -> Group 3 | Q1, Q2, Q3 | class-instance of the stated rule; not named |
| spelt flour | spelt flour | flour | Group 1 -> Group 3 | Q1, Q2, Q3 | class-instance of the stated rule; not named |
| wheat flour | wheat flour | flour | Group 1 -> Group 3 | Q1, Q2, Q3, Q5 | class-instance of the stated rule; not named |
| whole wheat flour | whole wheat flour | flour | Group 1 -> Group 3 | Q1, Q2, Q3, Q5 | class-instance of the stated rule; not named |
| wild rice | wild rice | whole_food | Group 1 -> Group 3 | Q1, Q2, Q3 | class-instance of the stated rule; not named |

## 4. Salted surface (re-measured; BEFORE = worktree of main 0ceb941, AFTER = this branch; separate fresh processes)

| form | rows probed | Group 1 before | Group 1 after | changed | newly Group 1 |
|---|---|---|---|---|---|
| `salted X` | 47 | 47 | 26 | 21 | 0 |
| `roasted salted X` | 47 | 47 | 26 | 21 | 0 |
| `toasted salted X` | 47 | 0 | 0 | 0 | 0 |
| total | 141 | 94 | 52 | 42 | 0 |

Reconciliation: 47 whole_food/flour rows = 21 in-scope lexicon rows (7 grain whole_food: barley, black rice, buckwheat, millet, rice, sorghum, wild rice; 14 flours; `red rice` and `parboiled rice` are not separate rows, they resolve to `rice`) + 26 out-of-scope rows (refined wheat flour, milk, egg, eggs, ragi, potato flour, oat, wheat, maize, corn, jowar, bajra, foxtail millet, pearl millet, quinoa, besan, toned milk, dahi, double toned milk, buffalo milk, milk solids, yeast, soya flour, split pulse urad flour, roasted gram, dehydrated vegetable). All 42 changes are Group 1 -> Group 3 (21 `salted X` + 21 `roasted salted X`), each attributed to the guard; 94 - 42 = 52 Group 1 answers remain, all on the 26 out-of-scope rows (`Salted Milk`, `Salted Egg` stay Group 1: measured-unchanged, outside the 23-term scope, parked).

## 5. Gates (committed tree)

| check | result |
|---|---|
| frozen 66 | changed 0 (no frozen label contains a salted in-scope grain); unexplained 0; abstain->4 0 |
| out-of-sample 32 | changed 0; unexplained 0; abstain->4 0 |
| drift (534 existing terms/synonyms alone) | 0 differences |
| descriptor surface (`roasted`, `toasted`, 768 probed) | 0 changed (clean) |
| powder surface (552 forms) | changed 0 (clean) |
| lexicon / synonyms / markers | 384 -> 384 rows, none added or changed; synonyms.csv and markers.csv byte-identical; no row was needed |
| suite | 1589 passed, 5 xfailed |
| parity | 709/709 identical (additions-only: 693 + 16 inputs, 0 lines removed) |

## 6. Controls (applied_gate.json 'controls'; before -> after group)

| control | before | after |
|---|---|---|
| salted buckwheat | 1 | 3 |
| roasted salted buckwheat | 1 | 3 |
| salted rice | 1 | 3 |
| salted wheat flour | 1 | 3 |
| salted oat flour | 1 | 3 |
| rice (salted) | 1 | 3 |
| rice (rice, salt) | 1 | 3 |
| salted parboiled rice | 1 | 3 |
| toasted salted oat flour | None | None |
| salted rice powder | None | None |
| salted wheat flour, water | None | None |
| rice, salted buckwheat | None | 3 |
| rice | 1 | 1 |
| unsalted rice | 1 | 1 |
| rice (no added salt) | 1 | 1 |
| roasted buckwheat | 1 | 1 |
| toasted oat flour | 1 | 1 |
| salted milk | 1 | 1 |
| salted egg | 1 | 1 |
| salted almonds | 3 | 3 |
| salted pinto beans | 3 | 3 |
| salted potatoes | 3 | 3 |
| salted mango | 3 | 3 |
| mango (preserved) | None | None |
| kidney beans (canned) | None | None |
| salted lychee | 3 | 3 |
| salted kale | 3 | 3 |

Nut, legume, vegetable and fruit salted controls are unchanged (the same before and after).

## 7. Search record (parked / not implemented)

- Sugar and oil on grains: Q6 (cereals with sugar are processed) is a source for sugared grains; not implemented (batch scope: salt). Parked.
- The 26 out-of-scope whole_food/flour rows with a salted form (`Salted Milk`, `Salted Egg`, ...): Group 1 before and after; no per-row source qualification done here. Parked.
- Salted forms of products whose kind is not whole_food/flour (e.g. salted rice powder): the powder standard abstains first; unchanged.
- 'Roasted' stays the pre-existing global descriptor; `toasted salted X` still abstains (the toasted path refuses salted names).

## 8. Exact diff vs main 0ceb941

9 files: `.instinct/scale-up-handoff.md`, `data/ingest/per_form_2a.json`, `evaluation/per_form_2a/README.md`, `evaluation/per_form_2a/applied_gate/applied_gate.json`, `evaluation/per_form_2a/fao_quotes.txt`, `scripts/parity_check.py`, `src/foodscan/classify.py`, `tests/test_salted_grain_guard.py`, `web_preview/foodscan.js`. normalise.py, lexicon.csv, synonyms.csv, markers.csv, descriptors.csv: untouched.
