# Vocabulary-gap wording and PROVISIONAL soybean row: flip check on the existing frozen paste inputs

Changes: (1) a list that runs on and ends in an item that is not in the vocabulary but does not look cut off is no longer called "truncated"; the result says "ingredients not in the local vocabulary" and names the items; genuine cut-offs (a word fragment such as "flo", the start of a longer term such as "pasteurized toned", an unclosed bracket) keep the truncation wording and gating.
(2) lexicon row "soybean" (PROVISIONAL, FAO 2019 Table 1 Group 1 "legumes such as beans, lentils" without naming soybean) plus spelling and form variants in synonyms.csv.
Method: the 66 untouched pasted inputs (fresh_batch_1 16, fresh_batch_2 15, fresh_batch_3 14, negation_addendum 6, dev_regression_15 15), build 8f682e9 versus this build. No new draws, no OCR. Files: before_8f682e9.json, after.json (group, reason, warnings, completeness status, drivers per input).
Result: **0 of 66 changed group, 0 changed driver lists, 0 changed completeness status.** Display text changed on 5 inputs: reason wording on N08, M02, Q06, Q08 ("looks truncated" became "not in the local vocabulary: <items>"), and one warning dropped on M07.
M07 (Group 4 stands): the old "List may be incomplete (ends mid-word or unrecognised ...)" warning was a false alarm: the list is complete and closed; the typo "lodised" made one item unrecognised. It now shows "the last item is not in the local vocabulary" as a completeness reason, and the item remains listed under Not assessed.
No input contains soybean in its own right, so the soybean row changed nothing here; its behaviour is covered by tests/test_vocab_gap_and_soybean.py only.

## Files and how to re-check them
- `before_8f682e9.json`, `after.json`: per input (66 keys, e.g. `b2/M07`): group, reason, warnings (full text), completeness status, drivers. `groups_before.json`, `groups_after.json`: groups only.
- `diff_summary.json`: counts and key lists of what changed per field, plus the full before/after reason and warning text of every input whose display text changed (including M07's dropped "List may be incomplete" warning).
- Re-check without this repo's code: `python3 -c "import json;b=json.load(open('before_8f682e9.json'));a=json.load(open('after.json'));print({f:sum(b[k][f]!=a[k][f] for k in b) for f in ['group','drivers','status','reason','warnings']})"` prints `{'group': 0, 'drivers': 0, 'status': 0, 'reason': 4, 'warnings': 1}`.
- Test file for this round: `tests/test_vocab_gap_and_soybean.py` (17 tests).
