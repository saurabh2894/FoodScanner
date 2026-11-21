# Gate report: plural-policy-1

**Verdict: READY_FOR_REVIEW**

Nothing was merged. `synonyms_candidate_rows.csv` is in synonyms.csv layout.

| Check | Result |
|---|---|
| candidate synonyms | 37 |
| dropped (already covered) | 0 |
| terms probed before/after for drift (all lexicon terms and synonyms) | 300 |
| negative controls (identity, or unrecognised for processed forms) | 27 checked, 0 failing |
| flip check (66 frozen inputs, separate fresh processes) | group 0, drivers 0, status 0, reason 0, warnings 0, ingredients 0, unassessed 0, ins_mappings 0 |
| harness proof | synonym rows 37; all 37 terms recognised after; 0 before |

## Candidate synonyms

- `cumin seeds` -> `cumin` (seed-plural)
- `caraway seeds` -> `caraway` (seed-plural)
- `fenugreek seeds` -> `fenugreek` (seed-plural)
- `anise seeds` -> `aniseed` (seed-plural)
- `ajwain seeds` -> `ajwain` (seed-plural)
- `basil leaves` -> `basil` (leaf-form)
- `basil leaf` -> `basil` (leaf-form)
- `oregano leaves` -> `oregano` (leaf-form)
- `oregano leaf` -> `oregano` (leaf-form)
- `parsley leaves` -> `parsley` (leaf-form)
- `parsley leaf` -> `parsley` (leaf-form)
- `mint leaves` -> `mint` (leaf-form)
- `mint leaf` -> `mint` (leaf-form)
- `sage leaves` -> `sage` (leaf-form)
- `sage leaf` -> `sage` (leaf-form)
- `thyme leaves` -> `thyme` (leaf-form)
- `thyme leaf` -> `thyme` (leaf-form)
- `rosemary leaves` -> `rosemary` (leaf-form)
- `rosemary leaf` -> `rosemary` (leaf-form)
- `tarragon leaves` -> `tarragon` (leaf-form)
- `tarragon leaf` -> `tarragon` (leaf-form)
- `marjoram leaves` -> `marjoram` (leaf-form)
- `marjoram leaf` -> `marjoram` (leaf-form)
- `chervil leaves` -> `chervil` (leaf-form)
- `chervil leaf` -> `chervil` (leaf-form)
- `savory leaves` -> `savory` (leaf-form)
- `savory leaf` -> `savory` (leaf-form)
- `peppermint leaves` -> `peppermint` (leaf-form)
- `peppermint leaf` -> `peppermint` (leaf-form)
- `spearmint leaves` -> `spearmint` (leaf-form)
- `spearmint leaf` -> `spearmint` (leaf-form)
- `coriander leaves` -> `coriander leaf` (leaf-plural)
- `dill leaves` -> `dill weed` (leaf-form)
- `dill leaf` -> `dill weed` (leaf-form)
- `bay leaves` -> `bay leaf` (leaf-plural)
- `chillis` -> `chilli` (plural-spelling)
- `red chilis` -> `red chili` (plural-spelling)

## Dropped


## Negative controls (must stay exactly as before the batch)

- `fenugreek leaves`: before {'name': 'fenugreek leaves', 'recognised': False} / after {'name': 'fenugreek leaves', 'recognised': False}
- `basil seeds`: before {'name': 'basil seeds', 'recognised': False} / after {'name': 'basil seeds', 'recognised': False}
- `basil seed`: before {'name': 'basil seed', 'recognised': False} / after {'name': 'basil seed', 'recognised': False}
- `chilli seeds`: before {'name': 'chilli seeds', 'recognised': False} / after {'name': 'chilli seeds', 'recognised': False}
- `turmeric leaves`: before {'name': 'turmeric leaves', 'recognised': False} / after {'name': 'turmeric leaves', 'recognised': False}
- `ginger leaves`: before {'name': 'ginger leaves', 'recognised': False} / after {'name': 'ginger leaves', 'recognised': False}
- `garlic leaves`: before {'name': 'garlic leaves', 'recognised': False} / after {'name': 'garlic leaves', 'recognised': False}
- `mustard leaves`: before {'name': 'mustard leaves', 'recognised': False} / after {'name': 'mustard leaves', 'recognised': False}
- `cardamom leaves`: before {'name': 'cardamom leaves', 'recognised': False} / after {'name': 'cardamom leaves', 'recognised': False}
- `pepper leaves`: before {'name': 'pepper leaves', 'recognised': False} / after {'name': 'pepper leaves', 'recognised': False}
- `cumin leaves`: before {'name': 'cumin leaves', 'recognised': False} / after {'name': 'cumin leaves', 'recognised': False}
- `sage seeds`: before {'name': 'sage seeds', 'recognised': False} / after {'name': 'sage seeds', 'recognised': False}
- `mint seeds`: before {'name': 'mint seeds', 'recognised': False} / after {'name': 'mint seeds', 'recognised': False}
- `oregano seeds`: before {'name': 'oregano seeds', 'recognised': False} / after {'name': 'oregano seeds', 'recognised': False}
- `peppermint seeds`: before {'name': 'peppermint seeds', 'recognised': False} / after {'name': 'peppermint seeds', 'recognised': False}
- `thyme seeds`: before {'name': 'thyme seeds', 'recognised': False} / after {'name': 'thyme seeds', 'recognised': False}
- `paprika leaves`: before {'name': 'paprika leaves', 'recognised': False} / after {'name': 'paprika leaves', 'recognised': False}
- `saffron leaves`: before {'name': 'saffron leaves', 'recognised': False} / after {'name': 'saffron leaves', 'recognised': False}
- `clove leaves`: before {'name': 'clove leaves', 'recognised': False} / after {'name': 'clove leaves', 'recognised': False}
- `cinnamon leaves`: before {'name': 'cinnamon leaves', 'recognised': False} / after {'name': 'cinnamon leaves', 'recognised': False}
- `dill seed leaves`: before {'name': 'dill seed leaves', 'recognised': False} / after {'name': 'dill seed leaves', 'recognised': False}
- `cuminseeds`: before {'name': 'cuminseeds', 'recognised': False} / after {'name': 'cuminseeds', 'recognised': False}
- `oreganoleaves`: before {'name': 'oreganoleaves', 'recognised': False} / after {'name': 'oreganoleaves', 'recognised': False}
- `coriander leaf extract`: before {'name': 'coriander leaf extract', 'recognised': False} / after {'name': 'coriander leaf extract', 'recognised': False}
- `oregano leaf extract`: before {'name': 'oregano leaf extract', 'recognised': False} / after {'name': 'oregano extract', 'recognised': False}
- `mint leaf extract`: before {'name': 'mint leaf extract', 'recognised': False} / after {'name': 'mint extract', 'recognised': False}
- `basil leaf oil`: before {'name': 'basil leaf oil', 'recognised': False} / after {'name': 'basil oil', 'recognised': False}
