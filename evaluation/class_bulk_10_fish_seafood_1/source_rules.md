# Category Source Rules: FDC Plain Fish & Seafood (Batch 10)

## 1. Primary Source Authority & Verbatim Quotations

All classification grounding is established strictly from the primary report in the repository:  
**FAO 2019**: Carlos Augusto Monteiro, Geoffrey Cannon, Mark Lawrence, Maria Laura da Costa Louzada, Priscila Pereira Machado. *Ultra-processed foods, diet quality, and health using the NOVA classification system*. Rome: Food and Agriculture Organization of the United Nations, 2019. (Report text `ca5644en.pdf`).

---

### Verbatim Group 1 Definition Clause (Animal Foods)
> **Table 1, Group 1: Unprocessed and minimally processed foods — Definition (p. 11, left column)**  
> *"Unprocessed (or natural) foods are the edible parts of plants (such as fruit, leaves, stems, seeds, roots) or from animals (such as muscle, offal, eggs, milk), and also fungi, algae and water, after separation from nature.*  
> *Minimally processed foods are natural foods altered by industrial processes such as removal of inedible or unwanted parts, drying, powdering, squeezing, crushing, grinding, fractioning, steaming, poaching, boiling, roasting, and pasteurization, chilling, freezing, placing in containers, vacuum packaging, non-alcoholic fermentation, and other methods that do not add salt, sugar, oils or fats or other food substances to the original food."*

---

### Verbatim Group 1 Examples Clause (Fish & Seafood Whole Cuts)
> **Table 1, Group 1: Unprocessed and minimally processed foods — Examples (p. 11, right column)**  
> *"meat, poultry, fish and seafood, whole or in the form of steaks, fillets and other cuts"*

*Note on Examples Clause Scope*: The continuous examples clause in Table 1 Group 1 p. 11 contains neither leading thermal qualifiers (*"fresh, chilled or frozen"*) nor trailing offal text (*"or offal"*). Whole fish and seafood cuts (steaks, fillets, whole fish, shucked mollusks, crab/lobster meat) are grounded directly in this continuous clause.

---

### Verbatim Group 3 & Group 4 Modification / Marker Clauses
> **Table 1, Group 3: Processed foods — Examples (p. 12)**  
> *"salted, dried, cured, or smoked meats and fish; canned fish (with or without added preservatives)"*

> **Table 1, Group 4: Ultra-processed foods — Examples (p. 12)**  
> *"...poultry and fish 'nuggets' and 'sticks', sausages, burgers, hot dogs, and other reconstituted meat products"*

---

## 2. Naming vs. Class-Instance Breakdown

| Category Clause / Item | Verbatim Scope in FAO 2019 | Inference Level | Status & Notes |
|---|---|---|---|
| **Fish (general class)** | Table 1 Group 1 p. 11: *"fish"* | **Exact-named** | Overarching class named verbatim in examples clause |
| **Seafood (general class)** | Table 1 Group 1 p. 11: *"seafood"* | **Exact-named** | Overarching class named verbatim in examples clause (covers crustaceans, mollusks) |
| **Steaks, fillets and other cuts** | Table 1 Group 1 p. 11: *"steaks, fillets and other cuts"* | **Exact-named** | Physical butchering/filleting cuts named verbatim in examples clause |
| **Finfish species** (salmon, tuna, cod, trout, mackerel, etc.) | Table 1 Group 1 p. 11: *"fish"* | **Class-instance** | Individual fish species are not named in FAO 2019; they are biological class-instances of `fish` |
| **Crustaceans** (crab, lobster, shrimp) | Table 1 Group 1 p. 11: *"seafood"* | **Class-instance** | Crustacean species are biological class-instances of `seafood` |
| **Mollusks** (oyster, mussel, scallop, octopus) | Table 1 Group 1 p. 11: *"seafood"* | **Class-instance** | Mollusk species are biological class-instances of `seafood` |
| **Canned / Tinned fish** | Table 1 Group 3 p. 12: *"canned fish"*; p. 9: *"tinned fish preserved in oil"* | **Exact-named** | Processed foods; rejected |
| **Smoked / Kippered / Salted fish** | Table 1 Group 3 p. 12: *"salted... or smoked... fish"* | **Exact-named** | Processed foods; rejected |
| **Fish sticks / nuggets / surimi** | Table 1 Group 4 p. 12: *"fish 'nuggets' and 'sticks'"* | **Exact-named** | Ultra-processed formulations; rejected |

---

## 3. Silence on Specific Terms (`SOURCE-SILENT`) & Species Identity Policy

Where the FAO 2019 report text does not name or define a term or category, it is recorded strictly as **SOURCE-SILENT**:
- **Specific biological species**: **SOURCE-SILENT** in the FAO text (no species like *Salmo salar*, *Thunnus albacares*, or *Callinectes sapidus* is named individually; all are biological class-instances).
- **Unit of Candidate Generation**: The required unit is **source-stated biological species identity**. Biologically distinct species are never merged under broad culinary categories (e.g. Atlantic salmon, Chinook salmon, Coho salmon, and Sockeye salmon are staged as separate species candidates).
- **Generic / Unspecified Identities**: FDC records that only state generic family, genus, or common market terms without specific species resolution (e.g. `Fish, pollock, raw`, `Crustaceans, shrimp, raw`, `Lobster, tail only`, `Fish, catfish, farm raised`, `Halibut, frozen`, `Snapper, frozen`, `Squid, frozen`, `Mollusks, conch`, `Fish, tilapia, raw`, `Fish, carp, raw`, `Fish, tilefish, raw`) are queued under `queue_generic_unspecified_identity`. No generic identity is invented or passed as a specific biological species.
- **Mixed or Multiple Species**: Where an FDC record states `mixed species` or multiple species (e.g. `Mollusks, clam, mixed species`, `Fish, flatfish (flounder and sole species)`), species identity cannot be established; these are preserved explicitly and queued under `queue_mixed_species`.
- **Fish roe / Caviar**: **SOURCE-SILENT** in Group 1 examples (queued under `queue_roe_special`).
- **Fried cooking methods**: Cooking methods stating `fried` or `pan-fried` without establishing lack of added cooking oil/fat are queued under `queue_cooking_added_fat`.
- **Surimi / fish paste**: **SOURCE-SILENT** in Group 1; industrial reconstituted seafood formulation (rejected under `surimi_imitation`).
- **Fish oils / cod-liver oils**: **SOURCE-SILENT** in Group 2 culinary ingredients; queued under `queue_fish_oil` (deferred to fats review).
