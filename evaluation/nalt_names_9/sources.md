# Source ledger, checked November 22, 2026

## NOVA placement and form scope

- Martinez Steele et al., J Nutr 2023, primary classification method and Table1: https://pmc.ncbi.nlm.nih.gov/articles/PMC10127522/ . Used for the vegetable/fruit class, definition paragraph naming drying/grinding/roasting, and separate culinary-addition Group3 class. High confidence in the quoted class; each food is a class-instance, not exact-named evidence.
- Best practices for applying the Nova food classification system, Nature Food, Table1, primary method guidance. https://www.nature.com/articles/s43016-023-00779-w/tables/1?code=07eb9f35-c8a1-4896-98fb-7286dbbde085&error=cookies_not_supported . Independently read for edible plant parts, preserved matrix, named minimal processes and limits. Not used to force unspecified powders or extracts.

## Current USDA NALT product identity, CC BY4.0

These official taxonomy pages establish identities/categories and explicit English synonyms only, not NOVA groups. Current page text was read. High confidence for the recorded term; no generalization from a botanical name to an unspecified derivative.

- https://lod.nal.usda.gov/nalt/16190 . Names checked: bean sprouts.
- https://lod.nal.usda.gov/nalt/16720 . Names checked: bergamot oranges.
- https://lod.nal.usda.gov/nalt/17102 . Names checked: sour oranges, bigarades, bitter oranges, seville oranges.
- https://lod.nal.usda.gov/nalt/260606 . Names checked: microgreens, microgreen plants.
- https://lod.nal.usda.gov/nalt/26520 . Names checked: tangors, king oranges.
- https://lod.nal.usda.gov/nalt/26563 . Names checked: tangelos, uglifruit.
- https://lod.nal.usda.gov/nalt/26572 . Names checked: satsumas, satsuma mandarins, satsuma oranges.
- https://lod.nal.usda.gov/nalt/278221 . Names checked: buckwheat sprouts.
- https://lod.nal.usda.gov/nalt/30550 . Names checked: winter squashes.
- https://lod.nal.usda.gov/nalt/43829 . Names checked: sorrel.
- https://lod.nal.usda.gov/nalt/43831 . Names checked: sweet potato greens.
- https://lod.nal.usda.gov/nalt/6633 . Names checked: pearl onions.
- https://lod.nal.usda.gov/nalt/6636 . Names checked: japanese bunching onions, japanese leeks, welsh onions.
- https://lod.nal.usda.gov/nalt/98404 . Names checked: grain sprouts.

Vegetable ancestry cross-checks:
- https://lod.nal.usda.gov/nalt/en/page/98404 , sprouts (food), explicitly a vegetable product with bean/buckwheat sprouts below it and grain sprouts as a synonym.
- https://lod.nal.usda.gov/nalt/en/page/12570 , vegetables.
- https://lod.nal.usda.gov/nalt/30549 , squashes, under vegetables and including winter squashes.

Held identity checks:
- https://lod.nal.usda.gov/nalt/8334 , cashew fruit/apple. Identity is verified but present normalization is unsafe for admission.
- https://lod.nal.usda.gov/nalt/35846 , fungal truffles. Does not disambiguate all bare-label confection uses.

## Validation-data recovery, separate from placement

- http://openfoodfacts.github.io/documentation/docs/Product-Opener/api/ and https://openfoodfacts.github.io/documentation/docs/Product-Opener/v2/products/get-product-by-code/ . Official read-only endpoint, identifying User-Agent and current 15-product-reads/minute limit. Recovery uses at most one read every five seconds.
- https://world.openfoodfacts.org/terms-of-use . Database ODbL, individual contents DbCL, attribution/third-party-rights limits. No OFF text is copied into this repository or candidate evidence zip. Original frozen hashes, not a new label draw, govern recovery.
