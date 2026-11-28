# FSSAI Standardised Product Names Extraction (Chapters 2.7, 2.9, 2.10)

- **Pinned `origin/main` SHA:** `1e27863c63a2256eaee5b3e36bbc70cefabc35c8`
- **Date:** 2026-11-28
- **Branch:** `antigravity/fssai-names-26`
- **Extraction tool:** `pypdf` (via `uv run --with pypdf`) on Python `3.12.10`; PDFs fetched directly from `fssai.gov.in` via `curl.exe`.

## Method

1. Opened the FSSAI compendium navigation page (`https://www.fssai.gov.in/food-law/regulations/compendium/food-products-standards`, HTTP 200) and downloaded the three chapter PDFs directly (`2.7`, `2.9`, `2.10`, all HTTP 200).
2. Extracted page-by-page text with `pypdf`, verified each printed chapter title and clause number, and copied each verbatim defining sentence into `candidates.csv` (`chapter, clause, name, verbatim_sentence, page, url, in_lexicon_today`).
3. Populated `in_lexicon_today` by case-insensitive, trimmed matching against `src/foodscan/resources/lexicon.csv` (`term` -> `exact`) and `src/foodscan/resources/synonyms.csv` (`from` -> `alias`, otherwise `no`) at the pinned SHA.
4. Table-only product matrices (`2.7.6(2)(b)`, `2.7.7(1)(d)`) and `[Omitted]` clauses (`2.9.25`, `2.9.30(2)-(3)`, `2.10.5`) were recorded by reading the PDFs and listed under `Not extracted / uncertain` in the chapter files.

## Counts

All counts below were computed by `python evidence/fssai_names_26/check_lexicon.py` (omitted/table-only items were counted by reading the PDFs):

| Chapter | Printed Title | Extracted | `exact` | `alias` | `no` |
|---|---|---:|---:|---:|---:|
| `2.7` | `2.7. SWEETS & CONFECTIONERY:` | 24 | 1 | 0 | 23 |
| `2.9` | `2.9: SALT, SPICES, CONDIMENTS AND RELATED PRODUCTS` | 78 | 3 | 0 | 75 |
| `2.10` | `2.10: BEVERAGES, (Other than Dairy and Fruits & Vegetables based)` | 32 | 2 | 1 | 29 |
| **Total** | | **134** | **6** | **1** | **127** |
