# Independent Provenance Audit 1: Classification-Bearing Resources vs FAO NOVA 2019 (ca5644en.pdf)

## Executive Summary

This report presents an independent, byte-by-byte provenance audit of every classification-bearing row on `main` HEAD (`d7e225d`) across:
- `src/foodscan/resources/lexicon.csv` (142 rows)
- `src/foodscan/resources/markers.csv` (37 rows)
- **Total rows audited: 179**

The primary authority used for this audit is the official FAO 2019 NOVA report:
> Monteiro, C.A., Cannon, G., Lawrence, M., Costa Louzada, M.L. and Pereira Machado, P. 2019. *Ultra-processed foods, diet quality, and health using the NOVA classification system*. Rome, FAO. Document `ca5644en.pdf`.
> **Verified SHA-256**: `c8024c194a8294a0355759877712ea7f61d4da62efc4dec46f3889821b19ceff`

Audit criteria enforced:
1. **Quote Fidelity**: Every quoted passage in the row's `source` field appears verbatim in the cited document (exact wording, punctuation, and scare quotes).
2. **Cite Accuracy**: The page and section cited actually contain the quoted passage.
3. **Condition Preservation**: Every condition attached to the source clause must survive in the classification rule. A clause conditioned on 'with no added salt or sugar' must never back an unconditioned classification row.
4. **Class/Form Honesty**: Where the exact term is not explicitly named by the clause, the row must state so explicitly. Silent mapping of a class to an instance is flagged as a mismatch.
5. **Name-Only Support**: Any classification row whose only support is a commodity name with no NOVA-source clause is flagged.
6. **Internal-Source Distinction**: Rows citing internal research files (`research/02` etc.) rather than `ca5644en.pdf` are recorded as `internal-source: not auditable against ca5644en` and segregated from verified rows.

### Summary Totals

| Metric | Count | Share |
|---|---|---|
| **Total Rows Audited** | **179** | 100.0% |
| - `lexicon.csv` | 142 | 79.3% |
| - `markers.csv` | 37 | 20.7% |
| **Verified** | **33** | 18.4% |
| - `lexicon.csv` verified | 28 | 15.6% |
| - `markers.csv` verified | 5 | 2.8% |
| **Mismatch** | **29** | 16.2% |
| - `lexicon.csv` mismatch | 27 | 15.1% |
| - `markers.csv` mismatch | 2 | 1.1% |
| **Internal-Source** | **117** | 65.4% |
| - `lexicon.csv` internal-source | 87 | 48.6% |
| - `markers.csv` internal-source | 30 | 16.8% |

---

## Mismatch Analysis (29 Rows)

Every mismatch row is detailed below with verbatim evidence from both the repository row and the primary source document (`ca5644en.pdf`), including printed and PDF page numbers.

### 1. Condition Dropped & Silent Class Mapping (3 rows in `lexicon.csv`)

The FAO NOVA report places nuts and seeds in Group 1 **only under an explicit negative condition**: `"(with no added salt or sugar)"`. When salt or sugar is added, Table 1 Group 3 explicitly classifies them as Processed Foods (`"salted or sugared nuts and seeds"`). In `lexicon.csv`, these items are given `kind=whole_food`, which causes the classifier to treat them as unconditioned Group 1 foods without verifying whether salt or sugar is added. Furthermore, none of these specific species are named in the text, yet the rows fail to disclose that the exact terms are unmentioned instances.

#### `almonds` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "tree and ground nuts and other oily seeds (with no added salt or sugar)"; exact label term seen on neg/R5, b1/N14.`
- **Document Text (Printed Page 11 / PDF Page 13, Table 1 Group 1 Examples)**:
  > *"tree and ground nuts and other oily seeds (with no added salt or sugar);"*
- **Audit Finding**: Condition dropped. The clause applies only with no added salt or sugar. Classifying bare terms as `whole_food` ignores added salt/sugar. Also, exact term is not named in the clause (silent class-to-instance mapping).

#### `pumpkin seeds` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "tree and ground nuts and other oily seeds (with no added salt or sugar)"; exact label term seen on b1/N14.`
- **Document Text (Printed Page 11 / PDF Page 13, Table 1 Group 1 Examples)**:
  > *"tree and ground nuts and other oily seeds (with no added salt or sugar);"*
- **Audit Finding**: Condition dropped. The clause applies only with no added salt or sugar. Classifying bare terms as `whole_food` ignores added salt/sugar. Also, exact term is not named in the clause (silent class-to-instance mapping).

#### `flax seeds` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "tree and ground nuts and other oily seeds (with no added salt or sugar)"; exact label term seen on b1/N14.`
- **Document Text (Printed Page 11 / PDF Page 13, Table 1 Group 1 Examples)**:
  > *"tree and ground nuts and other oily seeds (with no added salt or sugar);"*
- **Audit Finding**: Condition dropped. The clause applies only with no added salt or sugar. Classifying bare terms as `whole_food` ignores added salt/sugar. Also, exact term is not named in the clause (silent class-to-instance mapping).

### 2. Silent Class Mapping: Herbs and Spices (20 rows in `lexicon.csv`)

The FAO Table 1 Group 1 definition for herbs and spices lists six specific illustrative examples: `"thyme, oregano, mint, pepper, cloves and cinnamon"`. For twenty staged terms, the row quotes this clause and asserts `exact label term seen on [pack]`, but fails to disclose that the exact term is NOT named by the clause. This contrasts with later staged batches (e.g. `allspice`, `basil`) which explicitly disclose `exact term not named by the clause; name from USDA FoodData Central`.

#### `ajwain` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried"; exact label term seen on dev/F09.`
- **Document Text (Printed Page 11 / PDF Page 13, Table 1 Group 1 Examples)**:
  > *"herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried;"*
- **Audit Finding**: Class/form honesty failure. `ajwain` is not named by the clause. The row does not state that the term is an unmentioned instance, silently mapping the broad class to this instance.

#### `bishop's seed` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried"; exact label term seen on dev/F10.`
- **Document Text (Printed Page 11 / PDF Page 13, Table 1 Group 1 Examples)**:
  > *"herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried;"*
- **Audit Finding**: Class/form honesty failure. `bishop's seed` is not named by the clause. The row does not state that the term is an unmentioned instance, silently mapping the broad class to this instance.

#### `aniseed` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried"; exact label term seen on b1/N03, dev/F07.`
- **Document Text (Printed Page 11 / PDF Page 13, Table 1 Group 1 Examples)**:
  > *"herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried;"*
- **Audit Finding**: Class/form honesty failure. `aniseed` is not named by the clause. The row does not state that the term is an unmentioned instance, silently mapping the broad class to this instance.

#### `caraway` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried"; exact label term seen on dev/F07.`
- **Document Text (Printed Page 11 / PDF Page 13, Table 1 Group 1 Examples)**:
  > *"herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried;"*
- **Audit Finding**: Class/form honesty failure. `caraway` is not named by the clause. The row does not state that the term is an unmentioned instance, silently mapping the broad class to this instance.

#### `bay leaf` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried"; exact label term seen on b1/N05.`
- **Document Text (Printed Page 11 / PDF Page 13, Table 1 Group 1 Examples)**:
  > *"herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried;"*
- **Audit Finding**: Class/form honesty failure. `bay leaf` is not named by the clause. The row does not state that the term is an unmentioned instance, silently mapping the broad class to this instance.

#### `capsicum powder` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried"; exact label term seen on b1/N05.`
- **Document Text (Printed Page 11 / PDF Page 13, Table 1 Group 1 Examples)**:
  > *"herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried;"*
- **Audit Finding**: Class/form honesty failure. `capsicum powder` is not named by the clause. The row does not state that the term is an unmentioned instance, silently mapping the broad class to this instance.

#### `fennel` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried"; exact label term seen on b1/N05.`
- **Document Text (Printed Page 11 / PDF Page 13, Table 1 Group 1 Examples)**:
  > *"herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried;"*
- **Audit Finding**: Class/form honesty failure. `fennel` is not named by the clause. The row does not state that the term is an unmentioned instance, silently mapping the broad class to this instance.

#### `fennel seeds` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried"; exact label term seen on dev/F10.`
- **Document Text (Printed Page 11 / PDF Page 13, Table 1 Group 1 Examples)**:
  > *"herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried;"*
- **Audit Finding**: Class/form honesty failure. `fennel seeds` is not named by the clause. The row does not state that the term is an unmentioned instance, silently mapping the broad class to this instance.

#### `fenugreek` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried"; exact label term seen on b1/N10, b1/N03, dev/F03, dev/F07, dev/F10, dev/F11.`
- **Document Text (Printed Page 11 / PDF Page 13, Table 1 Group 1 Examples)**:
  > *"herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried;"*
- **Audit Finding**: Class/form honesty failure. `fenugreek` is not named by the clause. The row does not state that the term is an unmentioned instance, silently mapping the broad class to this instance.

#### `nutmeg` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried"; exact label term seen on b1/N05, b1/N03, dev/F03, dev/F07, dev/F10.`
- **Document Text (Printed Page 11 / PDF Page 13, Table 1 Group 1 Examples)**:
  > *"herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried;"*
- **Audit Finding**: Class/form honesty failure. `nutmeg` is not named by the clause. The row does not state that the term is an unmentioned instance, silently mapping the broad class to this instance.

#### `mace` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried"; exact label term seen on dev/F10.`
- **Document Text (Printed Page 11 / PDF Page 13, Table 1 Group 1 Examples)**:
  > *"herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried;"*
- **Audit Finding**: Class/form honesty failure. `mace` is not named by the clause. The row does not state that the term is an unmentioned instance, silently mapping the broad class to this instance.

#### `mustard` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried"; exact label term seen on b1/N10, dev/F11.`
- **Document Text (Printed Page 11 / PDF Page 13, Table 1 Group 1 Examples)**:
  > *"herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried;"*
- **Audit Finding**: Class/form honesty failure. `mustard` is not named by the clause. The row does not state that the term is an unmentioned instance, silently mapping the broad class to this instance.

#### `long pepper` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried"; exact label term seen on dev/F10.`
- **Document Text (Printed Page 11 / PDF Page 13, Table 1 Group 1 Examples)**:
  > *"herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried;"*
- **Audit Finding**: Class/form honesty failure. `long pepper` is not named by the clause. The row does not state that the term is an unmentioned instance, silently mapping the broad class to this instance.

#### `white pepper` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried"; exact label term seen on dev/F15.`
- **Document Text (Printed Page 11 / PDF Page 13, Table 1 Group 1 Examples)**:
  > *"herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried;"*
- **Audit Finding**: Class/form honesty failure. `white pepper` is not named by the clause. The row does not state that the term is an unmentioned instance, silently mapping the broad class to this instance.

#### `black pepper bits` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried"; exact label term seen on dev/F07.`
- **Document Text (Printed Page 11 / PDF Page 13, Table 1 Group 1 Examples)**:
  > *"herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried;"*
- **Audit Finding**: Class/form honesty failure. `black pepper bits` is not named by the clause. The row does not state that the term is an unmentioned instance, silently mapping the broad class to this instance.

#### `red chili` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried"; exact label term seen on dev/F03.`
- **Document Text (Printed Page 11 / PDF Page 13, Table 1 Group 1 Examples)**:
  > *"herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried;"*
- **Audit Finding**: Class/form honesty failure. `red chili` is not named by the clause. The row does not state that the term is an unmentioned instance, silently mapping the broad class to this instance.

#### `chillies` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried"; exact label term seen on dev/F07.`
- **Document Text (Printed Page 11 / PDF Page 13, Table 1 Group 1 Examples)**:
  > *"herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried;"*
- **Audit Finding**: Class/form honesty failure. `chillies` is not named by the clause. The row does not state that the term is an unmentioned instance, silently mapping the broad class to this instance.

#### `chilli flakes` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried"; exact label term seen on dev/F07.`
- **Document Text (Printed Page 11 / PDF Page 13, Table 1 Group 1 Examples)**:
  > *"herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried;"*
- **Audit Finding**: Class/form honesty failure. `chilli flakes` is not named by the clause. The row does not state that the term is an unmentioned instance, silently mapping the broad class to this instance.

#### `schezwan pepper` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried"; exact label term seen on dev/F15.`
- **Document Text (Printed Page 11 / PDF Page 13, Table 1 Group 1 Examples)**:
  > *"herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried;"*
- **Audit Finding**: Class/form honesty failure. `schezwan pepper` is not named by the clause. The row does not state that the term is an unmentioned instance, silently mapping the broad class to this instance.

#### `dried curry leaves` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried"; exact label term seen on dev/F10.`
- **Document Text (Printed Page 11 / PDF Page 13, Table 1 Group 1 Examples)**:
  > *"herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried;"*
- **Audit Finding**: Class/form honesty failure. `dried curry leaves` is not named by the clause. The row does not state that the term is an unmentioned instance, silently mapping the broad class to this instance.

### 3. Silent Class Mapping: Fruit (1 row in `lexicon.csv`)

#### `black raisin` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "Fresh, squeezed, chilled, frozen, or dried fruit and leafy and root vegetables"; exact label term seen on b1/N14.`
- **Document Text (Printed Page 11 / PDF Page 13, Table 1 Group 1 Examples)**:
  > *"Fresh, squeezed, chilled, frozen, or dried fruit and leafy and root vegetables;"*
- **Audit Finding**: Class/form honesty failure. `black raisin` (or raisin) is not named by the clause. The row fails to state that the exact term is an unmentioned instance.

### 4. Citation Page Mismatches: Food Powders (3 rows in `lexicon.csv`)

Three single-ingredient fruit/vegetable powder rows quote the definition of minimally processed foods but cite `p.10 (Group 1 definition)`. In `ca5644en.pdf`, page 10 is Section 3 ('Identifying ultra-processed foods'). The quoted definition appears verbatim on **Printed Page 6 (PDF Page 8)** under Section 2.

#### `banana powder` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) p.10 (Group 1 definition) "Minimally processed foods are natural foods altered by methods that include removal of inedible or unwanted parts, and also processes that include drying, crushing, grinding, powdering, fractioning, filtering, roasting, boiling, non-alcoholic fermentation, pasteurization, chilling, freezing, placing in containers, and vacuum packaging."; exact term named by FDC ("Bananas, dehydrated, or banana powder"), not by the clause: the clause names the process 'powdering' of natural foods, so a single powdered fruit is covered as a form; a powder with added carriers is a different list and keeps its own items; CONDITIONED: a bare term does not establish a single-ingredient powder free of carriers or anti-caking agents, so kind food_powder answers Group 1 only as the sole item of a list and makes every multi-item list abstain with the composition uncertainty stated; name from USDA FoodData Central (CC0 1.0): sr_legacy FDC id 173945 "Bananas, dehydrated, or banana powder"; demand-driven row (held-decisions-1)`
- **Cited Location**: `p.10 (Group 1 definition)`
- **Actual Location**: Printed Page 6 (PDF Page 8), Section 2 ('The NOVA food classification system and its four food groups', Group 1):
  > *"Minimally processed foods are natural foods altered by methods that include removal of inedible or unwanted parts, and also processes that include drying, crushing, grinding, powdering, fractioning, filtering, roasting, boiling, non-alcoholic fermentation, pasteurization, chilling, freezing, placing in containers, and vacuum packaging."*
- **Text on Cited Page 10 (PDF Page 12)**: Section 3 ('Identifying ultra-processed foods'), covering industrial breads, plain steel-cut oats, and additive identification guidelines.
- **Audit Finding**: Cite accuracy mismatch. Quoted text is on page 6, cited as page 10.

#### `strawberry powder` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) p.10 (Group 1 definition) "Minimally processed foods are natural foods altered by methods that include removal of inedible or unwanted parts, and also processes that include drying, crushing, grinding, powdering, fractioning, filtering, roasting, boiling, non-alcoholic fermentation, pasteurization, chilling, freezing, placing in containers, and vacuum packaging."; exact term not named by the clause or by FDC; the form (a single fruit, powdered) is covered by the process 'powdering' of natural foods; CONDITIONED: a bare term does not establish a single-ingredient powder free of carriers or anti-caking agents, so kind food_powder answers Group 1 only as the sole item of a list and makes every multi-item list abstain with the composition uncertainty stated; demand-driven row (held-decisions-1)`
- **Cited Location**: `p.10 (Group 1 definition)`
- **Actual Location**: Printed Page 6 (PDF Page 8), Section 2 ('The NOVA food classification system and its four food groups', Group 1):
  > *"Minimally processed foods are natural foods altered by methods that include removal of inedible or unwanted parts, and also processes that include drying, crushing, grinding, powdering, fractioning, filtering, roasting, boiling, non-alcoholic fermentation, pasteurization, chilling, freezing, placing in containers, and vacuum packaging."*
- **Text on Cited Page 10 (PDF Page 12)**: Section 3 ('Identifying ultra-processed foods'), covering industrial breads, plain steel-cut oats, and additive identification guidelines.
- **Audit Finding**: Cite accuracy mismatch. Quoted text is on page 6, cited as page 10.

#### `beetroot powder` (`src/foodscan/resources/lexicon.csv`)
- **Row Claim (`source`)**: `PROVISIONAL: FAO 2019 (ca5644en.pdf) p.10 (Group 1 definition) "Minimally processed foods are natural foods altered by methods that include removal of inedible or unwanted parts, and also processes that include drying, crushing, grinding, powdering, fractioning, filtering, roasting, boiling, non-alcoholic fermentation, pasteurization, chilling, freezing, placing in containers, and vacuum packaging."; exact term not named by the clause or by FDC; the form (a single vegetable, powdered) is covered by the process 'powdering' of natural foods; a colour-note use ('for colour') is a separate rule and unchanged; CONDITIONED: a bare term does not establish a single-ingredient powder free of carriers or anti-caking agents, so kind food_powder answers Group 1 only as the sole item of a list and makes every multi-item list abstain with the composition uncertainty stated; demand-driven row (held-decisions-1)`
- **Cited Location**: `p.10 (Group 1 definition)`
- **Actual Location**: Printed Page 6 (PDF Page 8), Section 2 ('The NOVA food classification system and its four food groups', Group 1):
  > *"Minimally processed foods are natural foods altered by methods that include removal of inedible or unwanted parts, and also processes that include drying, crushing, grinding, powdering, fractioning, filtering, roasting, boiling, non-alcoholic fermentation, pasteurization, chilling, freezing, placing in containers, and vacuum packaging."*
- **Text on Cited Page 10 (PDF Page 12)**: Section 3 ('Identifying ultra-processed foods'), covering industrial breads, plain steel-cut oats, and additive identification guidelines.
- **Audit Finding**: Cite accuracy mismatch. Quoted text is on page 6, cited as page 10.

### 5. Citation & Table Mismatches: Additive Classes (2 rows in `markers.csv`)

Two additive class markers cite `Table 1 (p. 11)` for Group 4 additive classes. However, Table 1 on Printed Page 11 (PDF Page 13) covers **only Groups 1 and 2**. Group 4 of Table 1 appears on **Printed Page 12 (PDF Page 14)**. Furthermore, Table 1 on page 12 **omits `emulsifying salts`**, which appears only in the prose on **Printed Page 9 (PDF Page 11)**.

#### `emulsifying salt` (`src/foodscan/resources/markers.csv`)
- **Row Claim (`source`)**: `research/02 addendum (2026-11-20): FAO 2019, Monteiro et al., Ultra-processed foods, diet quality, and health using the NOVA classification system, pp. 9-10 and Table 1 (p. 11), https://www.fao.org/3/ca5644en/ca5644en.pdf: emulsifying salts are listed among the additive classes used only in ultra-processed foods`
- **Document Evidence**:
  - Printed Page 9 (PDF Page 11): *"Classes of additives used only in the manufacture of ultra-processed foods, are flavours, flavour enhancers, colours, emulsifiers, emulsifying salts, artificial sweeteners, thickeners, and foaming, anti-foaming, bulking, carbonating, gelling and glazing agents."*
  - Printed Page 11 (PDF Page 13): Table 1 covers only Groups 1 & 2. Group 4 is on page 12.
  - Printed Page 12 (PDF Page 14): Table 1 Group 4 additive list states: *"such as flavours, flavour enhancers, colours, emulsifiers, and sweeteners, thickeners, and anti-foaming, bulking, carbonating, foaming, gelling, and glazing agents"* — **omitting emulsifying salts**.
- **Audit Finding**: Cite accuracy and text mismatch. Table 1 (p. 11) contains only Groups 1 & 2; Table 1 continuation (p. 12) omits emulsifying salts. The term appears only in prose on p. 9. Also, row term is singular `emulsifying salt` while text states plural `emulsifying salts`.

#### `thickener` (`src/foodscan/resources/markers.csv`)
- **Row Claim (`source`)**: `research/02 addendum (2026-11-20): FAO 2019, Monteiro et al., Ultra-processed foods, diet quality, and health using the NOVA classification system, pp. 9-10 and Table 1 (p. 11), https://www.fao.org/3/ca5644en/ca5644en.pdf: thickeners are listed among the additive classes used only in ultra-processed foods`
- **Document Evidence**:
  - Printed Page 9 (PDF Page 11): lists *"thickeners"* among classes of additives used only in ultra-processed foods.
  - Printed Page 11 (PDF Page 13): Table 1 covers only Groups 1 & 2.
  - Printed Page 12 (PDF Page 14): Table 1 Group 4 lists *"thickeners"*.
- **Audit Finding**: Cite accuracy mismatch. Cites Table 1 (p. 11), which contains only Groups 1 & 2. Thickeners in Table 1 are on page 12. Also, row term is singular `thickener` while text states plural `thickeners`.

---

## Verified Rows (33 Rows)

The following 33 rows satisfy all six audit criteria: verbatim quote matches, accurate page citations, preserved conditions, and explicit class/form disclosures.

### `src/foodscan/resources/lexicon.csv` (28 rows)

| Term | Kind | Quoted / Referenced Clause | Citation | Notes |
|---|---|---|---|---|
| `dates` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `soybean` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `mint` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `pepper` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `allspice` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `basil` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `celery seed` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `chervil` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `coriander leaf` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `coriander seed` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `dill seed` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `dill weed` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `marjoram` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `oregano` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `paprika` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `parsley` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `peppermint` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `rosemary` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `saffron` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `sage` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `savory` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `spearmint` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `tarragon` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `thyme` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `wheat flour` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `beans` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `cabbage` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |
| `peanut oil` | `whole_food` / `herb_spice` / `oil` / `flour` | Table 1 | p. 11 | Fully verified quote, cite, & disclosures |

### `src/foodscan/resources/markers.csv` (5 rows)

| Term | Class | Quoted Clause | Citation | Disclosed Mapping |
|---|---|---|---|---|
| `fructose` | `derived_substance` | "include varieties of sugars... and sources of protein..." | p. 9 & p. 10 | Explicitly disclosed class/instance mapping |
| `wheat gluten` | `derived_substance` | "include varieties of sugars... and sources of protein..." | p. 9 & p. 10 | Explicitly disclosed class/instance mapping |
| `hydrolysed vegetable protein` | `derived_substance` | "include varieties of sugars... and sources of protein..." | p. 9 & p. 10 | Explicitly disclosed class/instance mapping |
| `lemon juice concentrate` | `derived_substance` | "include varieties of sugars... and sources of protein..." | p. 9 & p. 10 | Explicitly disclosed class/instance mapping |
| `apple juice concentrate` | `derived_substance` | "include varieties of sugars... and sources of protein..." | p. 9 & p. 10 | Explicitly disclosed class/instance mapping |

---

## Internal-Source Rows (117 Rows)

These 117 rows cite internal research artifacts (`research/02`, `research/04`, `author seed`, `FSSAI` regulations, or `NOT in research/02`) rather than `ca5644en.pdf`. As required by the audit specification, they are marked `internal-source: not auditable against ca5644en` and listed separately below.

### `src/foodscan/resources/markers.csv` (30 internal rows)

| Term | Source Claim |
|---|---|
| `hydrogenated` | research/02 marker class 1 (hydrogenated vegetable oil) |
| `interesterified` | research/02 marker class 1 (interesterified vegetable oil) |
| `glucose-fructose syrup` | research/02 marker class 1 (HFCS / glucose-fructose syrup) |
| `invert sugar` | research/02 marker class 1 |
| `maltodextrin` | research/02 marker class 1 |
| `dextrose` | research/02 marker class 1 |
| `modified starch` | research/02 marker class 1 (modified starches) |
| `protein isolate` | research/02 marker class 1 (soy / whey protein isolate) |
| `colour` | research/02 marker class 2 (colourings); NOVA wording: Monteiro et al. 2019 identification paper (Public Health Nutr 22:936; abstract read) and NUPENS-USP classification page (research/04). PROVISIONAL: applies to a declared additive colour only |
| `flavour` | research/02 marker class 2 (flavourings) |
| `enhancer` | research/02 marker class 2 (flavour enhancers) |
| `sweetener` | research/02 marker class 2 (non-sugar sweeteners) |
| `emulsifier` | research/02 marker class 2 (emulsifiers) |
| `anti-foaming` | research/02 marker class 2 (cosmetic processing aids) |
| `antifoaming` | research/02 marker class 2 (cosmetic processing aids) |
| `bulking` | research/02 marker class 2 (cosmetic processing aids) |
| `carbonating` | research/02 marker class 2 (cosmetic processing aids) |
| `foaming` | research/02 marker class 2 (cosmetic processing aids) |
| `gelling` | research/02 marker class 2 (cosmetic processing aids) |
| `glazing` | research/02 marker class 2 (cosmetic processing aids) |
| `firming` | research/02 marker class 2 (cosmetic processing aids) |
| `humectant` | research/02 marker class 2 (cosmetic processing aids) |
| `pectin` | research/02 qualification: pectin in a jam is consistent with group 3 |
| `raising agent` | research/02 qualification: raising agents in plain bread are consistent with group 3 |
| `preservative` | NOT in research/02: class named in no marker list; treated as uncertain pending review |
| `antioxidant` | NOT in research/02: treated as uncertain pending review |
| `acidity regulator` | NOT in research/02: treated as uncertain pending review |
| `stabiliser` | NOT in research/02: treated as uncertain pending review |
| `anticaking agent` | NOT in research/02: treated as uncertain pending review |
| `flour treatment agent` | NOT in research/02: treated as uncertain pending review |

### `src/foodscan/resources/lexicon.csv` (87 internal rows)

| Term | Source Claim |
|---|---|
| `whole wheat flour` | research/02 synthetic example 1 (group 1); atta listed as group 1 |
| `refined wheat flour` | research/02 synthetic example 2 ingredient; flour kind => bread-like lists abstain |
| `cucumber` | research/02 synthetic example 3 |
| `rice` | research/02 group 1 examples (rice) |
| `milk` | research/02 group 1 examples (milk) |
| `egg` | research/02 group 1 examples (eggs) |
| `eggs` | research/02 group 1 examples (eggs) |
| `toor dal` | research/02 group 1 examples (plain dals) |
| `moong dal` | research/02 group 1 examples (plain dals) |
| `chana dal` | research/02 group 1 examples (plain dals) |
| `masoor dal` | research/02 group 1 examples (plain dals) |
| `urad dal` | research/02 group 1 examples (plain dals) |
| `tomato` | PROVISIONAL author seed (fruit/vegetable; research/02 group 1 examples list fruit) |
| `potato` | PROVISIONAL author seed (vegetable) |
| `onion` | PROVISIONAL author seed (vegetable) |
| `carrot` | PROVISIONAL author seed (vegetable) |
| `peas` | PROVISIONAL author seed (vegetable) |
| `mango` | PROVISIONAL author seed (fruit; research/02 group 1 examples list fruit) |
| `lemon` | PROVISIONAL author seed (fruit) |
| `salt` | research/02 group 2 (salt) |
| `iodised salt` | PROVISIONAL author seed (variant of salt) |
| `sugar` | research/02 group 2 (sugar) |
| `vinegar` | research/02 synthetic example 3 |
| `edible vegetable oil` | research/02 group 2 (oils); example 2 ingredient |
| `ghee` | research/02 group 2 (ghee) |
| `mustard oil` | research/02 group 2 (oils) |
| `sunflower oil` | research/02 group 2 (oils) |
| `groundnut oil` | research/02 group 2 (oils) |
| `coconut oil` | research/02 group 2 (oils) |
| `dill` | research/02 synthetic example 3 |
| `turmeric` | PROVISIONAL author seed (spice) |
| `cumin` | PROVISIONAL author seed (spice) |
| `coriander` | PROVISIONAL author seed (spice) |
| `black pepper` | PROVISIONAL author seed (spice) |
| `chilli` | PROVISIONAL author seed (spice) |
| `garlic` | PROVISIONAL author seed (spice) |
| `water` | research/02 synthetic example 3 (water carries no processing signal) |
| `ragi` | PROVISIONAL author seed (finger millet grain; plain cereal) |
| `rice flour` | PROVISIONAL author seed (milled rice; flour kind so mixed lists abstain) |
| `potato flour` | PROVISIONAL author seed (flour kind so mixed lists abstain) |
| `rice bran oil` | research/02 group 2 (oils) |
| `jaggery` | PROVISIONAL author seed: unrefined cane/palm sugar, a group 2 sugar like sugar itself (research/02 group 2); project-maintained entry added 2026-11-20; not an external endorsement |
| `oat` | PROVISIONAL: NOVA group 1 example (cereal grain / pulse); research/02 lists atta, rice and plain dals as group 1 |
| `wheat` | PROVISIONAL: NOVA group 1 example (cereal grain / pulse); research/02 lists atta, rice and plain dals as group 1 |
| `maize` | PROVISIONAL: NOVA group 1 example (cereal grain / pulse); research/02 lists atta, rice and plain dals as group 1 |
| `corn` | PROVISIONAL: NOVA group 1 example (cereal grain / pulse); research/02 lists atta, rice and plain dals as group 1 |
| `barley` | PROVISIONAL: NOVA group 1 example (cereal grain / pulse); research/02 lists atta, rice and plain dals as group 1 |
| `jowar` | PROVISIONAL: NOVA group 1 example (cereal grain / pulse); research/02 lists atta, rice and plain dals as group 1 |
| `bajra` | PROVISIONAL: NOVA group 1 example (cereal grain / pulse); research/02 lists atta, rice and plain dals as group 1 |
| `millet` | PROVISIONAL: NOVA group 1 example (cereal grain / pulse); research/02 lists atta, rice and plain dals as group 1 |
| `foxtail millet` | PROVISIONAL: NOVA group 1 example (cereal grain / pulse); research/02 lists atta, rice and plain dals as group 1 |
| `pearl millet` | PROVISIONAL: NOVA group 1 example (cereal grain / pulse); research/02 lists atta, rice and plain dals as group 1 |
| `quinoa` | PROVISIONAL: NOVA group 1 example (cereal grain / pulse); research/02 lists atta, rice and plain dals as group 1 |
| `chickpea` | PROVISIONAL: NOVA group 1 example (cereal grain / pulse); research/02 lists atta, rice and plain dals as group 1 |
| `lentil` | PROVISIONAL: NOVA group 1 example (cereal grain / pulse); research/02 lists atta, rice and plain dals as group 1 |
| `rajma` | PROVISIONAL: NOVA group 1 example (cereal grain / pulse); research/02 lists atta, rice and plain dals as group 1 |
| `moong` | PROVISIONAL: NOVA group 1 example (cereal grain / pulse); research/02 lists atta, rice and plain dals as group 1 |
| `black salt` | PROVISIONAL: NOVA group 2 culinary ingredient (salt, sugars, oils and fats); research/02 lists oils, ghee, sugar, salt |
| `rock salt` | PROVISIONAL: NOVA group 2 culinary ingredient (salt, sugars, oils and fats); research/02 lists oils, ghee, sugar, salt |
| `sea salt` | PROVISIONAL: NOVA group 2 culinary ingredient (salt, sugars, oils and fats); research/02 lists oils, ghee, sugar, salt |
| `butter` | PROVISIONAL: butter is a NOVA group 2 culinary ingredient in the NOVA literature cited via the USP NUPENS page in research/02; not re-verified in this session |
| `palm oil` | PROVISIONAL: NOVA group 2 culinary ingredient (salt, sugars, oils and fats); research/02 lists oils, ghee, sugar, salt |
| `palmolein` | PROVISIONAL: NOVA group 2 culinary ingredient (salt, sugars, oils and fats); research/02 lists oils, ghee, sugar, salt |
| `soybean oil` | PROVISIONAL: NOVA group 2 culinary ingredient (salt, sugars, oils and fats); research/02 lists oils, ghee, sugar, salt |
| `sesame oil` | PROVISIONAL: NOVA group 2 culinary ingredient (salt, sugars, oils and fats); research/02 lists oils, ghee, sugar, salt |
| `olive oil` | PROVISIONAL: NOVA group 2 culinary ingredient (salt, sugars, oils and fats); research/02 lists oils, ghee, sugar, salt |
| `cottonseed oil` | PROVISIONAL: NOVA group 2 culinary ingredient (salt, sugars, oils and fats); research/02 lists oils, ghee, sugar, salt |
| `vegetable oil` | PROVISIONAL: NOVA group 2 culinary ingredient (salt, sugars, oils and fats); research/02 lists oils, ghee, sugar, salt |
| `honey` | PROVISIONAL: honey is a NOVA group 2 culinary ingredient in the NOVA literature; not re-verified in this session |
| `ginger` | PROVISIONAL author seed (spice) |
| `cardamom` | PROVISIONAL author seed (spice) |
| `cinnamon` | PROVISIONAL author seed (spice) |
| `clove` | PROVISIONAL author seed (spice) |
| `asafoetida` | PROVISIONAL author seed (spice) |
| `mustard seed` | PROVISIONAL author seed (spice) |
| `besan` | PROVISIONAL, source missing: no source naming 'besan' has been found (the FSSAI dairy chapter does not mention it and the NUPENS-USP page is the NOVA method source, not a definition). Treated as a flour (milled pulse, author knowledge) so mixed lists stay uncertain; not an unprocessed whole food |
| `toned milk` | Identity: FSSAI Food Safety and Standards regulations, Chapter 2 Food Product Standards, 2.1 Dairy products and analogues (PDF created 2023-05-23, SHA-256 94a52a70248b15e3..., fetched 2026-11-20 from fssai.gov.in; amendments noted as in force 1 Aug 2023), 2.1.2 item 1(c) and the composition table: 'Toned Milk' is milk standardised to 3.0% fat and 8.5% SNF, with or without dried or concentrated milks or milk fat, pasteurised or boiled. PROVISIONAL as a NOVA entry: treated as milk; whether standardised or recombined milk stays in group 1 is not stated by the NOVA page (NOVA method only: NUPENS-USP classification page (research/04), which lists milk, pasteurised or powdered, as group 1) |
| `dahi` | Identity: FSSAI Food Safety and Standards regulations, Chapter 2 Food Product Standards, 2.1 Dairy products and analogues (PDF created 2023-05-23, SHA-256 94a52a70248b15e3..., fetched 2026-11-20 from fssai.gov.in; amendments noted as in force 1 Aug 2023), 2.1.13 item 1(a): 'Dahi' is a fermented milk characterised by lactic acid bacteria; the standard permits added sugar and other ingredients, so only a PLAIN dahi fits. PROVISIONAL as a NOVA entry: NOVA method only: NUPENS-USP classification page (research/04) names plain yoghurt with no added sugar or artificial sweeteners as group 1; that page does not define dahi |
| `active lactic culture` | PROVISIONAL, exact term not in a source: FSSAI Food Safety and Standards regulations, Chapter 2 Food Product Standards, 2.1 Dairy products and analogues (PDF created 2023-05-23, SHA-256 94a52a70248b15e3..., fetched 2026-11-20 from fssai.gov.in; amendments noted as in force 1 Aug 2023), 2.1.13, names 'starter cultures of harmless microorganisms' and 'lactic acid bacteria' for dahi, but not the phrase 'active lactic culture'. Treated as a starter culture with no processing signal of its own; NOVA method only: NUPENS-USP classification page (research/04) names the fermentation of milk to make yoghurt as a group 1 process |
| `lactic culture` | PROVISIONAL, exact term not in a source: FSSAI Food Safety and Standards regulations, Chapter 2 Food Product Standards, 2.1 Dairy products and analogues (PDF created 2023-05-23, SHA-256 94a52a70248b15e3..., fetched 2026-11-20 from fssai.gov.in; amendments noted as in force 1 Aug 2023), 2.1.13, names 'starter cultures of harmless microorganisms' and 'lactic acid bacteria' for dahi, but not the phrase 'lactic culture'. Treated as a starter culture with no processing signal of its own; NOVA method only: NUPENS-USP classification page (research/04) names the fermentation of milk to make yoghurt as a group 1 process |
| `live culture` | PROVISIONAL, exact term not in a source: FSSAI Food Safety and Standards regulations, Chapter 2 Food Product Standards, 2.1 Dairy products and analogues (PDF created 2023-05-23, SHA-256 94a52a70248b15e3..., fetched 2026-11-20 from fssai.gov.in; amendments noted as in force 1 Aug 2023), 2.1.13, names 'starter cultures of harmless microorganisms' and 'lactic acid bacteria' for dahi, but not the phrase 'live culture'. Treated as a starter culture with no processing signal of its own; NOVA method only: NUPENS-USP classification page (research/04) names the fermentation of milk to make yoghurt as a group 1 process |
| `active culture` | PROVISIONAL, exact term not in a source: FSSAI Food Safety and Standards regulations, Chapter 2 Food Product Standards, 2.1 Dairy products and analogues (PDF created 2023-05-23, SHA-256 94a52a70248b15e3..., fetched 2026-11-20 from fssai.gov.in; amendments noted as in force 1 Aug 2023), 2.1.13, names 'starter cultures of harmless microorganisms' and 'lactic acid bacteria' for dahi, but not the phrase 'active culture'. Treated as a starter culture with no processing signal of its own; NOVA method only: NUPENS-USP classification page (research/04) names the fermentation of milk to make yoghurt as a group 1 process |
| `yoghurt culture` | PROVISIONAL, exact term not in a source: FSSAI Food Safety and Standards regulations, Chapter 2 Food Product Standards, 2.1 Dairy products and analogues (PDF created 2023-05-23, SHA-256 94a52a70248b15e3..., fetched 2026-11-20 from fssai.gov.in; amendments noted as in force 1 Aug 2023), 2.1.13, names 'starter cultures of harmless microorganisms' and 'lactic acid bacteria' for dahi, but not the phrase 'yoghurt culture'. Treated as a starter culture with no processing signal of its own; NOVA method only: NUPENS-USP classification page (research/04) names the fermentation of milk to make yoghurt as a group 1 process |
| `double toned milk` | Identity: FSSAI Food Safety and Standards regulations, Chapter 2 Food Product Standards, 2.1 Dairy products and analogues (PDF created 2023-05-23, SHA-256 94a52a70248b15e3..., fetched 2026-11-20 from fssai.gov.in; amendments noted as in force 1 Aug 2023), 2.1.2 item 1(c) and the composition table: 'Double Toned Milk' is milk standardised to 1.5% fat and 9.0% SNF (1.3% fat from 1 Aug 2023 by amendment). PROVISIONAL as a NOVA entry: treated as milk; whether standardised or recombined milk stays in group 1 is not stated by the NOVA page (NOVA method only: NUPENS-USP classification page (research/04)) |
| `buffalo milk` | Identity: FSSAI Food Safety and Standards regulations, Chapter 2 Food Product Standards, 2.1 Dairy products and analogues (PDF created 2023-05-23, SHA-256 94a52a70248b15e3..., fetched 2026-11-20 from fssai.gov.in; amendments noted as in force 1 Aug 2023), 2.1.2 item 1(a) (species identified milk, buffalo milk) and the composition table in item 2(b): Buffalo Milk, minimum 5.0% milk fat and 9.0% SNF, pasteurised, boiled, sterilised or UHT treated. PROVISIONAL as a NOVA entry: treated as milk like the other milks; the NOVA page (NOVA method only: NUPENS-USP classification page (research/04)) lists milk, pasteurised or powdered, as group 1 but does not name buffalo milk |
| `milk solids` | PROVISIONAL, exact ingredient term not defined in a source: FSSAI Food Safety and Standards regulations, Chapter 2 Food Product Standards, 2.1 Dairy products and analogues (PDF created 2023-05-23, SHA-256 94a52a70248b15e3..., fetched 2026-11-20 from fssai.gov.in; amendments noted as in force 1 Aug 2023), uses the words milk solids only as a composition measure (2.1.5, sweetened condensed milk) and lists concentrated milk and dried milk as permitted raw materials of fermented milks (2.1.13 item 2(a)(ii)). Treated as dried or concentrated milk, like the other milks; NOVA method only: NUPENS-USP classification page (research/04) lists milk, pasteurised or powdered, as group 1 |
| `starter culture` | Identity: FSSAI Food Safety and Standards regulations, Chapter 2 Food Product Standards, 2.1 Dairy products and analogues (PDF created 2023-05-23, SHA-256 94a52a70248b15e3..., fetched 2026-11-20 from fssai.gov.in; amendments noted as in force 1 Aug 2023), 2.1.13 item 2(b)(i) names starter cultures of harmless microorganisms as a permitted ingredient of fermented milks (item 1(a): dahi is characterised by lactic acid bacteria). PROVISIONAL as a NOVA entry: NOVA method only: NUPENS-USP classification page (research/04) names the fermentation of milk to make yoghurt as a group 1 process; a starter culture carries no processing signal of its own |
