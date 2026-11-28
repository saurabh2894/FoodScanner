# Product-form words (parser._PRODUCT_FORM_WORDS, JS PRODUCT_FORM_WORDS) and their sources

A tail word (singular or plural, any case, curly apostrophes read as straight) that is in this set blocks the peel. Pinned by `tests/test_peel_product_form.py::test_product_form_words_are_each_traceable_to_a_source`.

| Word(s) | Source |
|---|---|
| seasoning, mix, sauce, paste, blend, extract, syrup | `data/ingest/clause_tier1_herbs_spices.json` `processed_words` (names a compound or processed product, outside the whole-or-powdered clause) |
| seasoning, sauce, soup, noodles, puff, topping, sprinkler, masala, tastemaker, coating, oleoresin | section labels found by parsing the saved real labels (frozen 66, out-of-sample 32) and the parity corpus (seasoning 55 sections; noodles 6; puff 4; sprinkler mix (topping) 3; masala tastemaker 3; coating, sauce, oleoresin, masala 1-2 each); "oleoresin" occurs only in synthetic corpus cases |
| garnish, filling, glaze, dressing, base, concentrate, premix | reviewer-listed; not found in the data (kept because they name product forms; no lexicon row ends in them except `tomato concentrate`) |
Not used: flavour/flavor (already additive class words, blocked earlier), descriptor and form words (already blocked by the existing form-word guard).
Allowlist `_KNOWN_LABEL_WORDS`: empty. Extending it needs a cited real label whose same-line label word is not a product form.
