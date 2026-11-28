# Source-Provenance Audit (`evidence/source_audit_26`)

## Scope and Base Commit

- **Target file:** `src/foodscan/resources/lexicon.csv` (833 data rows; 177 rows carry two unheaded trailing cells for `extra_ids` and `batch_tag`).
- **Base commit:** `origin/main` at `4fe693a5a19d28fa37aa958089df52a5a369787b` (1 commit newer than `de1d9192bea3e50536e6bd82d01f3cd59fadb71c`).
- **Scope:** Read-only evidence audit; no edits to `src/`, `tests/`, `data/`, `scripts/`, or `lexicon.csv`.

## Method

1. Parsed `src/foodscan/resources/lexicon.csv` with both `csv.DictReader` and raw `csv.reader` so the 177 rows with unheaded 4th (`extra_ids`) and 5th (`batch_tag`) columns were preserved intact.
2. Audited the 177 extra-cell rows and 803 `PROVISIONAL` rows first and completely, then the remaining 30 rows in file order, outputting all 833 rows ordered by `row_number` (1–833) to `rows.csv`.
3. Verified citations directly against opened primary sources:
   - **FAO (2019)** *Ultra-processed foods, diet quality, and health using the NOVA classification system* (`ca5644en.pdf`, 48 PDF pages extracted with `pypdf`, matching verbatim clauses and printed page numbers).
   - **USDA FoodData Central** (`data/cache/candidates.csv`, 8,291 Foundation and SR Legacy records) for `fdc:`, `fdc_sr_legacy:`, and `fdc_foundation:` IDs.
   - **FSSAI Compendium PDFs** (Chapters 2.1, 2.2, 2.4, 2.6, 2.8) extracted with `pypdf`.
   - **PMC10127522** (Martinez Steele et al. 2023) and **PMC8453454** (Khandpur et al. 2021) fetched via `curl`.
   - **Local `research/` files** (`research/02-research-nova-and-ingredients.txt`, etc.).
   - **187 unique cited URLs** fetched via `curl` (HTTP 200 content checked for term/quote presence; non-200 or unreachable URLs recorded as `could-not-open`).

## Tool Versions

- Python `3.12.10` (`csv`, `json`, `re`, `collections`)
- `pypdf` (via `uv run --with pypdf`)
- `curl` (Windows `curl.exe`)

## Regenerate Counts from `rows.csv`

```bash
python3 -c "import csv;r=list(csv.DictReader(open('evidence/source_audit_26/rows.csv',encoding='utf-8')));print(len(r))"
```

```bash
python3 -c "import csv,collections;r=list(csv.DictReader(open('evidence/source_audit_26/rows.csv',encoding='utf-8')));print('class:',dict(collections.Counter(x['class'] for x in r)));print('citation_checked:',dict(collections.Counter(x['citation_checked'] for x in r)))"
```
