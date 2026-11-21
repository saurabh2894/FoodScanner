# Gate report: class-fruits-1

**Verdict: READY_FOR_REVIEW**

Nothing was merged. `lexicon_candidate_rows.csv` holds the ready rows in lexicon.csv layout and `synonyms_candidate_rows.csv` the synonym candidates in synonyms.csv layout, for review.

| Check | Result |
|---|---|
| staged rows | 76 |
| schema errors | 0 |
| provenance errors | 0 |
| duplicates (exact, synonym, already recognised) | 1 |
| variants of an existing term (informational) | 1 |
| parked in the ambiguity queue | 22 (Counter({'clause_tier': 22})) |
| ready rows (new lexicon rows) | 75 |
| synonym candidates (variant policy variant-policy-class-fruits-1) | 0 |
| policy errors | 0 |
| verbatim clause vs FAO text | PASS |
| harness proof (separate processes) | lexicon rows 295 -> 370; all 75 staged terms recognised after; 0 already recognised before |
| flip check (66 frozen inputs, before and after in separate fresh processes) | group 0, drivers 0, status 0, reason 0, warnings 0, ingredients 0, unassessed 0, ins_mappings 0 |
| group/status/driver flips | 0  |
| unexplained changes | 0 |

## Ready rows (new lexicon rows)

- `abiyuch`
- `acerola`
- `apples`
- `apricots`
- `asian pears`
- `avocados`
- `bananas`
- `black currants`
- `blackberries`
- `blueberries`
- `boysenberries`
- `breadfruit`
- `cantaloupe melons`
- `carambola`
- `carissa`
- `casaba melons`
- `cherimoya`
- `cherries`
- `clementines`
- `crabapples`
- `custard-apple`
- `elderberries`
- `feijoa`
- `figs`
- `gooseberries`
- `grapefruit`
- `grapes`
- `groundcherries`
- `guavas`
- `honeydew melons`
- `jackfruit`
- `java-plum`
- `jujube`
- `kiwifruit`
- `kumquats`
- `limes`
- `litchis`
- `longans`
- `loquats`
- `mamey sapote`
- `mammy-apple`
- `mandarin`
- `mulberries`
- `muscadine grapes`
- `nance`
- `nectarines`
- `oheloberries`
- `oranges`
- `papayas`
- `passion-fruit`
- `pawpaw`
- `pears`
- `persimmons`
- `pineapple`
- `pitanga`
- `plantains`
- `plums`
- `pomegranates`
- `prickly pears`
- `pummelo`
- `quinces`
- `raspberries`
- `red currants`
- `rhubarb`
- `rose-apples`
- `rowal`
- `sapodilla`
- `sour cherries`
- `soursop`
- `strawberries`
- `strawberry guavas`
- `sugar-apples`: separate row because a named fruit (sweetsop); the shared word 'sugar' with the existing 'sugar' row is incidental (false variant match)
- `tangerines`
- `watermelon`
- `yellow peaches`

## Synonym candidates (variant policy: same ingredient, plant part and form)


## Duplicates (excluded: already covered)

- `mangos`: already recognised by this build (descriptors, plurals or synonyms)

## Variants of existing terms (kept; informational)

- `sugar-apples` ~ ['sugar']

## Ambiguity queue (parked, never included)

- `Watermelon, seedless, rind only, raw` (clause_tier, queue_rind): a plant-part variant (rind) of a fruit.
- `Rhubarb, stalk, raw` (clause_tier, queue_stalk): plant-part variant.
- `Lemons, raw, without peel` (clause_tier, queue_peel): a plant-part variant (peel, rind) of a fruit: not established as a label term.
- `Lemon peel, raw` (clause_tier, queue_peel): a plant-part variant (peel, rind) of a fruit: not established as a label term.
- `Tamarinds, raw` (clause_tier, queue_tamarinds): tamarind is a culinary pulp/sourcing ingredient on Indian labels (tamarind pulp, paste): the raw fruit name is queued until the pulp/paste forms are decided (owner).
- `Naranjilla (lulo) pulp, frozen, unsweetened` (clause_tier, queue_pulp): a fruit pulp is a processed mass (a puree-like product), not the whole or cut fruit; per-item decision.
- `Horned melon (Kiwano)` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Jujube, Chinese, fresh, dried` (clause_tier, queue_dried): dried forms: the clause names 'dried' but earlier owner policy (dehydrated-policy-1) keeps dried/dehydrated forms per-term only.
- `Roselle, raw` (clause_tier, queue_roselle): calyces used as a hibiscus herb/tea; not established as a fruit term.
- `Durian, raw or frozen` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Litchis, dried` (clause_tier, queue_dried): dried forms: the clause names 'dried' but earlier owner policy (dehydrated-policy-1) keeps dried/dehydrated forms per-term only.
- `Loganberries, frozen` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Orange peel, raw` (clause_tier, queue_peel): a plant-part variant (peel, rind) of a fruit: not established as a label term.
- `Longans, dried` (clause_tier, queue_dried): dried forms: the clause names 'dried' but earlier owner policy (dehydrated-policy-1) keeps dried/dehydrated forms per-term only.
- `Melon balls, frozen` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Oranges, raw, with peel` (clause_tier, queue_peel): a plant-part variant (peel, rind) of a fruit: not established as a label term.
- `Persimmons, japanese, dried` (clause_tier, queue_dried): dried forms: the clause names 'dried' but earlier owner policy (dehydrated-policy-1) keeps dried/dehydrated forms per-term only.
- `cranberries` (clause_tier, dedupe_stays_out): STANDING EXCLUSION (lexicon-1 senior review, tests/test_lexicon_1.py): 'cranberry' on b1/N14 does not establish plain dried status (cranberries are typically sweetened when dried), so the term must stay out; the raw FDC record is queued, not staged.
- `Currants, zante, dried` (clause_tier, queue_dried): dried forms: the clause names 'dried' but earlier owner policy (dehydrated-policy-1) keeps dried/dehydrated forms per-term only.
- `Goji berries, dried` (clause_tier, queue_dried): dried forms: the clause names 'dried' but earlier owner policy (dehydrated-policy-1) keeps dried/dehydrated forms per-term only.
- `Blueberries, wild, frozen (Includes foods for USDA's Food Distribution Program)` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `american type grapes` (clause_tier, dedupe_stays_out): a grape type descriptor (slip skin) that is not a label term; stays out rather than inflating the lexicon

## Unassessed drops attributed to ready rows

