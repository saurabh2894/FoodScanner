# Sweetener class word with a bracket of named foods: flip check on the existing frozen paste inputs

Change: an entry whose own name is only "sweetener" (optionally "natural"), with a bracket that names only recognised foods and no INS code ("Sweeteners (Jaggery Powder, Dates Powder)"), is not read as an added sweetener class; the result says so (warning, or an abstention reason when nothing else decides).
Basis: FAO 2019 (Monteiro et al., https://www.fao.org/3/ca5644en/ca5644en.pdf, pp. 9-10) lists ARTIFICIAL sweeteners among the Group 4 classes; jaggery, honey and dates are foods. A new PROVISIONAL lexicon row "dates" was needed to recognise the bracket (research/04).
Method: the 66 untouched pasted inputs (fresh_batch_1 16, fresh_batch_2 15, fresh_batch_3 14, negation_addendum 6, dev_regression_15 15), build before versus after. No new draws, no OCR.
Result: **0 of 66 changed group; 0 changed driver lists.** Only two inputs mention sweeteners (M13: INS 955 and 950; Q13: aspartame, acesulfame K): both are real additive sweeteners and keep their sweetener driver (controls).
This change has no real-label evidence of its own beyond the user's "THE GOOD PRO MIX" label (Group 4 stays, now only through "Nature Identical Flavour"; the sweetener driver is gone and a warning explains why).
