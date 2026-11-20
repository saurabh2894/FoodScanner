# Supply sources for vocabulary candidates

Candidate NAMES only. No source here decides a NOVA group, a lexicon `kind` or a row: that needs a verbatim source clause (FAO 2019 Table 1 and the project's exact-term rule), the clause-tier mapping (WS3) and the validation gate (WS4).
The registry is in `scripts/fdc_ingest.py` (`SOURCES`); a source that is not `enabled` cannot be downloaded or normalised.

## USDA FoodData Central (enabled): public domain, CC0 1.0 Universal
Licence statement, as published at https://fdc.nal.usda.gov/ (read 2026-11-20): "USDA FoodData Central data are in the public domain and they are not copyrighted. They are published under CC0 1.0 Universal (CC0 1.0)
No permission is needed for their use, but we request that users list FoodData Central as the source of the data".
**Source listing (the requested attribution):** U.S. Department of Agriculture, Agricultural Research Service, Beltsville Human Nutrition Research Center. FoodData Central. [Internet]. Available from https://fdc.nal.usda.gov/.

Datasets used (files and checksums of the run in `fdc_downloads_1.json`):
| Key | File | Used rows |
|---|---|---|
| foundation | `FoodData_Central_foundation_food_csv_2026-10-29.zip` (https://fdc.nal.usda.gov/fdc-datasets/) | `data_type = foundation_food` only (498 foods). The 4 other data types in that zip (sample_food, sub_sample_food, market_acquisition, agricultural_acquisition) are lab samples, many with brand names, and are not used. |
| sr_legacy | `FoodData_Central_sr_legacy_food_csv_2018-04.zip` | all 7,793 SR Legacy foods |
Registered but disabled: `survey` (FNDDS prepared dishes) and `branded` (brand products).

Download notes (2026-11-20): the slash-less download-page URL redirects to plain http, which the proxy cannot carry, so the downloader uses `https://fdc.nal.usda.gov/download-datasets/`. For the Foundation zip the server answered the same URL
with two different objects on different requests (4,209,875 bytes, ETag 6aff073c, complete; 1,127,612 bytes, ETag 6ae24373, an older object without `food.csv`). The downloader checks Content-Length, the zip integrity and the presence of
`food.csv` and `food_category.csv`, retries until a response is a complete dataset, and never saves anything else. The ETag and Last-Modified of the accepted object are recorded in the manifest.

## IFCT 2017 (Indian Food Composition Tables): NOT used, documented hook only
Licence unverified, so nothing is imported. A future adapter must meet this interface before the registry entry may be enabled: (1) a recorded, verified licence that permits reuse of the names; (2) it writes the same `candidates.csv` columns as
`fdc_ingest.py normalise` (candidate_id, dataset, data_type, source record id, verbatim description, description_norm, parts, category, publication date, dataset release, source URL, licence); (3) per-row provenance back to the source record; (4) the
same gate (WS4) with no shortcut. Until then `scripts/fdc_ingest.py` refuses it ("hook only").

## Open Food Facts: reference only
Open Food Facts remains the source of the frozen evaluation inputs (already in the repo under their stated terms). Nothing is incorporated from it into vocabulary: the ODbL share-alike fit is unresolved. The registry marks it `reference_only`.
