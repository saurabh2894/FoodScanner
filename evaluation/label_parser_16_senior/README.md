# label_parser_16 senior integration (PROPOSAL; merge stops with the owner)

Branch claude/label-parser-16-senior off main a6cacbc00fe3f8543a78f002b952a9a64375c4fd (origin/main verified at the start of this work). Junior commit cherry-picked: 91bd74e0e8d526f8a00a0bd78fcec6790c277463 (the only commit above a6cacbc on antigravity/label-parser-16; its STATUS.md names `cccb3e98fedd89994efc444540b98dd55fd15d70`, which does not exist in the repository: the STATUS SHA is stale, the branch tip is 91bd74e). Senior commits: a4a1cc9b7f9a3649bae6ba6dc5ccb59f0e6c1a53 (code, tests, gates) and the README commit on top.

## 1. What the junior change does (kept)
Trailing footnote marks removal in `normalise_ingredient`; `&`- or `and`-joined pairs inside a bracket split when both sides are recognised with their shared modifier (`Rice and Oat (22.3%)`); culinary-blend guard (`_names_two_oils`) and shared code-list guard kept. No lexicon, synonym, marker or policy change. One existing negative control (`Rice and Oat` whole) became `Rice or Oat` in `tests/test_ampersand_split_1.py` because 'and' pairs now split by design; that is the junior's deliberate change and is kept.

## 2. Blocking defect found in review and corrected here
`strip_footnotes` / `stripFootnotes` removed a mark before ANY whitespace, so punctuation inside a multi-word phrase was discarded and abstentions became answers (measured on a6cacbc + the junior commit): `Rice<closing quote> Flour` Group 1, `Sunflower<closing quote> Oil` Group 2, `Skimmed<closing quote> Milk Powder` Group 1, `Rice# Flour` Group 1 (all abstained before).
Correction (`normalise.py`, mirrored in `foodscan.js`): a mark (#, ##, ###, *, **, ***, dagger, double dagger, closing quote U+201D) is removed only when it follows a letter, digit or closing bracket AND is followed, after optional spaces, by the end of the text, `) ] } , ; : .`, `&`, an opening bracket (percentage or sub-list) or the connector words `and` / `or`. A mark inside a multi-word phrase stays and the item abstains as before. The raw input is never changed; a text holding a quoted phrase keeps its closing quote (junior rule kept). Measured after the fix: the four cases above abstain again; `Vitamins# and Minerals##`, `Vitamins<closing quote> and Minerals**` and `Vitamins<closing quote> & Minerals**` still resolve as two separate unplaced entries (Vitamins, Minerals); `Rice* (23%)` and `Rice#, Sugar` keep their answers.

## 3. Gates (committed tree vs main a6cacbc; separate fresh processes)
| check | result |
|---|---|
| lexicon / synonyms / markers | 433 -> 433, nothing changed |
| frozen 66 | changed 0; unexplained 0; abstain->4 0 |
| out-of-sample 32 | changed 2, both intended parser effects with no group change: S16 (herbal blend written `Cardamom* (17%)`, `fennel*`, `coriander*`, ...: the organic-asterisk items become recognised, group stays abstain, reason changes); S13 (`Nutmeg and Black Pepper` bracket pair splits; group 4 unchanged); attributed, unexplained 0 |
| drift (583 terms/synonyms probed) | 0 differences |
| descriptor (866) / salted (168) / powder (579) surfaces | 0 changed |
| suite | **2086 passed, 5 xfailed** (rerun here; the junior's 2061 passed / 6 skipped is superseded) |
| parity | **871/871** identical (main 859 + 12 added entries, 0 removed; reason and driver compared) |

## 4. Tests and one repository fix
`tests/test_label_parser_16_senior.py` (new, 20 cases): mark inside a phrase is not removed and the item abstains (closing quote, #, *, ##, dagger, quoted `and`); marks at the end or before a percentage are removed with the raw input kept; Vitamins/Minerals with marks stay two unplaced entries; boundary-mark lists keep their groups; quoted phrases keep the quote. `tests/test_mine_unassessed.py` failed once the junior's `evaluation/label_parser_16/matrix_comparison.json` existed: the evidence miner reads every evaluation JSON with `unassessed` lists and the file has no input ids (four terms flagged '?'). The file is kept as evidence but renamed `matrix_comparison.json.txt` (README reference updated), so the miner does not read it.

## 5. Not done here
Priority 2 (abstention headline aggregation), Priority 3 (animal-kind and process guard), and the real-photo UI retest of the multigrain label. No Task 15 prose or claims imported.

## 6. Exact diff vs main a6cacbc (12 paths, `git diff --name-only a6cacbc HEAD` on the committed tree)
- `evaluation/label_parser_16/README.md`
- `evaluation/label_parser_16/STATUS.md`
- `evaluation/label_parser_16/matrix_comparison.json.txt`
- `evaluation/label_parser_16_senior/README.md`
- `evaluation/label_parser_16_senior/applied_gate/applied_gate.json`
- `scripts/parity_check.py`
- `src/foodscan/normalise.py`
- `src/foodscan/pipeline.py`
- `tests/test_ampersand_split_1.py`
- `tests/test_label_parser_16.py`
- `tests/test_label_parser_16_senior.py`
- `web_preview/foodscan.js`
