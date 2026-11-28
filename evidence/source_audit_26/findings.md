# Source-Provenance Audit Findings (`lexicon.csv`)

Base commit: `origin/main` at `4fe693a5a19d28fa37aa958089df52a5a369787b` (newer than `de1d9192bea3e50536e6bd82d01f3cd59fadb71c` by 1 commit: `general-26a`).
Audited file: `src/foodscan/resources/lexicon.csv` (833 data rows; 177 rows with 2 extra unheaded cells `extra_ids` and `batch_tag`, 803 rows marked `PROVISIONAL`, 30 non-provisional rows).

## 1. Trailing whitespace in `source` cell (3 rows, not fixed)

Three rows end their `source` cell with a trailing space (`' '`), at CSV lines 813–815 (1-based data row numbers 812–814):

- **CSV line 813 (data row 812)** — `wheat bran` (`flour`):
  `"...FSSAI 2.4 mentions bran only as the part removed in milling, not as a defined product. "`
- **CSV line 814 (data row 813)** — `oat bran` (`flour`):
  `"...FSSAI 2.4 mentions bran only as the part removed in milling, not as a defined product. "`
- **CSV line 815 (data row 814)** — `rice bran` (`flour`):
  `"...FSSAI 2.4 mentions bran only as the part removed in milling, not as a defined product. "`

## 2. Duplicate aliases in `src/foodscan/resources/synonyms.csv` (7 pairs)

| Alias (`from`) | Canonical target (`to`) | Data row numbers (1-based) | CSV line numbers |
|---|---|---|---|
| `aubergine` | `eggplant` | 178, 365 | 179, 366 |
| `brinjal` | `eggplant` | 180, 364 | 181, 365 |
| `black eyed peas` | `cowpeas` | 195, 390 | 196, 391 |
| `broad beans` | `broadbeans` | 201, 357 | 202, 358 |
| `fava beans` | `broadbeans` | 204, 355 | 205, 356 |
| `black-eyed peas` | `cowpeas` | 256, 389 | 257, 390 |
| `water chestnuts` | `waterchestnuts` | 308, 396 | 309, 397 |

## 3. Summary table by `kind` and `class`

| `kind` | `placement+identity` | `identity-only` | `placement-only` | `provisional` | `missing-source` | `synthetic` | `not-attempted` | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `culinary` | 10 | 1 | 0 | 63 | 0 | 1 | 0 | **75** |
| `culture` | 0 | 0 | 0 | 6 | 0 | 0 | 0 | **6** |
| `flour` | 3 | 0 | 0 | 18 | 1 | 2 | 0 | **24** |
| `food_powder` | 0 | 0 | 0 | 3 | 0 | 0 | 0 | **3** |
| `fruit` | 0 | 0 | 0 | 154 | 0 | 2 | 0 | **156** |
| `fruit_juice` | 0 | 0 | 0 | 4 | 0 | 0 | 0 | **4** |
| `herb_spice` | 0 | 1 | 0 | 71 | 0 | 1 | 0 | **73** |
| `legume` | 5 | 0 | 0 | 32 | 0 | 3 | 0 | **40** |
| `named_water` | 1 | 0 | 0 | 0 | 0 | 0 | 0 | **1** |
| `neutral` | 1 | 0 | 0 | 0 | 0 | 0 | 0 | **1** |
| `nut_seed` | 0 | 0 | 0 | 27 | 0 | 0 | 0 | **27** |
| `unplaced` | 0 | 0 | 0 | 6 | 0 | 0 | 0 | **6** |
| `vegetable` | 0 | 1 | 0 | 173 | 0 | 5 | 0 | **179** |
| `whole_food` | 4 | 0 | 0 | 218 | 0 | 16 | 0 | **238** |
| **Total** | **24** | **3** | **0** | **775** | **1** | **30** | **0** | **833** |

## 4. Verification counts (`citation_checked`)

- **Rows audited:** `833 / 833` (100% — all 177 extra-cell rows and 803 `PROVISIONAL` rows audited first, followed by the remaining 30 rows in file order).
- `verified`: **791**
- `not-found`: **25** (21 `PROVISIONAL author seed` rows with no external citation, 1 `PROVISIONAL, source missing` (`besan`), `jaggery` in `research/02`, `soybean` in `ca5644en.pdf`, `split pulse urad flour` in `PMC10127522`)
- `could-not-open`: **17** (rows whose cited URL returned HTTP 0 / 403 / 503 during fetch, e.g. `dpd.gov.in`, `mpns.science.kew.org`, `feedipedia.review.fao.org`, `hort.purdue.edu`, `extension.umn.edu`, `indiaflora-ces.iisc.ac.in`, `loneitu.nic.in`, `my.ucanr.edu`, `wgbis.ces.iisc.ac.in`)
- `not-attempted`: **0**
