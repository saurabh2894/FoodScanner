# Category Source Rules: FDC Meat & Poultry Plain Forms (Batch 9)

## 1. Primary Source Authority & Verbatim Quotations

All classification grounding is established strictly from the primary report in the repository:  
**FAO 2019**: Carlos Augusto Monteiro, Geoffrey Cannon, Mark Lawrence, Maria Laura da Costa Louzada, Priscila Pereira Machado. *Ultra-processed foods, diet quality, and health using the NOVA classification system*. Rome: Food and Agriculture Organization of the United Nations, 2019. (Report text `ca5644en.pdf`).

---

### Verbatim Group 1 Definition Clause (Animal Foods)
> **Table 1, Group 1: Unprocessed and minimally processed foods — Definition (p. 11)**  
> *"Unprocessed (or natural) foods are the edible parts of plants (such as fruit, leaves, stems, seeds, roots) or from animals (such as muscle, offal, eggs, milk), and also fungi, algae and water, after separation from nature.*  
> *Minimally processed foods are natural foods altered by industrial processes such as removal of inedible or unwanted parts, drying, powdering, squeezing, crushing, grinding, fractioning, steaming, poaching, boiling, roasting, and pasteurization, chilling, freezing, placing in containers, vacuum packaging, non-alcoholic fermentation, and other methods that do not add salt, sugar, oils or fats or other food substances to the original food."*

---

### Verbatim Group 1 Examples Clause (Meat & Poultry)
> **Table 1, Group 1: Unprocessed and minimally processed foods — Examples (p. 11)**  
> *"...meat, poultry, fish and seafood, whole or in the form of steaks, fillets and other cuts; ..."*

---

### Verbatim Group 2 Reference to Pork
> **Table 1, Group 2: Processed culinary ingredients — Examples (p. 11)**  
> *"Vegetable oils crushed from seeds, nuts or fruit (notably olives); butter and lard obtained from milk and pork; ..."*

---

### Verbatim Group 3 & Group 4 Modification / Marker Clauses
> **Table 1, Group 3: Processed foods — Examples (p. 12)**  
> *"salted, dried, cured, or smoked meats and fish; canned fish (with or without added preservatives); ..."*

> **Table 1, Group 4: Ultra-processed foods — Examples (p. 12)**  
> *"...poultry and fish 'nuggets' and 'sticks', sausages, burgers, hot dogs, and other reconstituted meat products; ..."*

---

## 2. Naming vs. Class-Instance Breakdown

| Category Clause / Item | Verbatim Scope in FAO 2019 | Inference Level | Status & Notes |
|---|---|---|---|
| **Meat (general class)** | Table 1 Group 1 p. 11: *"meat"* | **Exact-named** | Overarching class named verbatim |
| **Poultry (general class)** | Table 1 Group 1 p. 11: *"poultry"* | **Exact-named** | Overarching class named verbatim |
| **Steaks, fillets and cuts** | Table 1 Group 1 p. 11: *"steaks, fillets and other cuts"* | **Exact-named** | Physical cutting/butchering is an explicit verbatim Group 1 cut form |
| **Offal** | Table 1 Group 1 p. 11: *"muscle, offal, eggs, milk"* | **Exact-named** | Offal (liver, heart, kidney, tongue, etc.) named verbatim in definition |
| **Pork** | Table 1 Group 2 p. 11: *"obtained from milk and pork"* | **Exact-named** | Pork named directly as an animal source food |
| **Beef** | Table 1 Group 1 p. 11: *"meat"* | **Class-instance** | Specific mammalian livestock species (cattle / *Bos taurus*) is an instance of `meat` |
| **Lamb** | Table 1 Group 1 p. 11: *"meat"* | **Class-instance** | Specific mammalian livestock species (sheep / *Ovis aries*) is an instance of `meat` |
| **Veal** | Table 1 Group 1 p. 11: *"meat"* | **Class-instance** | Young cattle meat is an instance of `meat` |
| **Chicken** | Table 1 Group 1 p. 11: *"poultry"* | **Class-instance** | Specific avian livestock species (*Gallus gallus*) is an instance of `poultry` |
| **Turkey** | Table 1 Group 1 p. 11: *"poultry"* | **Class-instance** | Specific avian livestock species (*Meleagris gallopavo*) is an instance of `poultry` |
| **Duck** | Table 1 Group 1 p. 11: *"poultry"* | **Class-instance** | Specific avian livestock species (*Anas platyrhynchos*) is an instance of `poultry` |
| **Goose** | Table 1 Group 1 p. 11: *"poultry"* | **Class-instance** | Specific avian livestock species (*Anser anser*) is an instance of `poultry` |
| **Smoked / Cured / Bacon / Ham** | Table 1 Group 3 p. 12: *"cured, or smoked meats"* | **Exact-named** | Processed meats; rejected |
| **Nuggets / Sausages / Reconstituted** | Table 1 Group 4 p. 12: *"poultry... 'nuggets'... sausages... reconstituted"* | **Exact-named** | Ultra-processed formulations; rejected |

---

## 3. Silence on Specific Terms (`SOURCE-SILENT`) & Guard Policy

Where the FAO 2019 report text does not name or define a term or category, it is recorded strictly as **SOURCE-SILENT**:
- **Goat / Mutton**: **SOURCE-SILENT** in the FAO 2019 text (*Capra hircus* is unmentioned by name in the FAO text; queued under `queue_game_rare_species`).
- **Game meats** (venison/deer, elk, bison, buffalo, wild boar, rabbit, squirrel, pheasant, quail, wild duck, grouse, Canada goose): **SOURCE-SILENT** in Group 1 domestic examples (queued under `queue_game_rare_species`).
- **Ground / minced meat forms without composition details**: **SOURCE-SILENT** in Group 1 examples (mincing alters structural integrity; unstated if binders/solutions added; queued under `ground_form_unstated`).
- **Animal backfat and separable fat** (pure backfat, seam fat, external fat, subcutaneous fat, intermuscular fat, suet, leaf fat, skin-only): named in Table 1 Group 2 as culinary ingredients; queued under `queue_animal_fat` (deferred to fats and oils review).
- **Fried / Pan-fried cooking methods**: Frying or pan-frying cannot establish plain status without added cooking oil/fat from source name alone; queued under `queue_cooking_added_fat`.
- **Mechanically separated / deboned meat**: **SOURCE-SILENT** in Group 1; industrial reconstituted processing (rejected under `mechanically_separated`).
- **Skipped Category**: `Sausages and Luncheon Meats` (Category ID 7, 185 records: 167 SR Legacy + 18 Foundation) is skipped from baseline staging due to ubiquitous curing salts, nitrites, and industrial formulations.
