# Fresh batch 1 (never used in development)

Written before any run. Selection rule (fixed in advance): Open Food Facts products from India (code prefix 890), English ingredients text,
an ingredient-panel photo on record; page 2 and 3 of each category sorted by scan count, in this category order: biscuits-and-cakes,
instant-noodles, salty-snacks, chocolates, dairies, pickles, sauces, breakfast-cereals, spreads, beverages; the first two qualifying products per category
with a brand not already chosen; products whose code was ever listed during development were skipped; 4 further products were dropped before
reading any label because their brand/product family overlaps a development product (Yippee, Saffola, Thums Up, Yoga Bar). N04 (a Kurkure variant)
was excluded before scoring for the same reason once its label was read. Photos are not copied into the repository (URLs in manifest.json).
Pasted input = the untouched Open Food Facts `ingredients_text` (`inputs/Nnn.txt`). The references (`reference.json`, `references.md`) were written by an
LLM from the photos before anything was run; they are provisional and need the owner's spot-check.
