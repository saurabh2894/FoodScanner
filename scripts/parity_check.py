"""Run the Python pipeline and the JS port on the same texts; fail on any difference.

Usage: python scripts/parity_check.py     (needs node)
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from web_tables import tables  # noqa: E402

from foodscan.pipeline import analyse_text  # noqa: E402

BISCUIT = ("Ingredients: Refined wheat flour, sugar, edible vegetable oil (palmolein), invert syrup, "
           "raising agents (INS 500(ii), INS 503(ii)), emulsifier (INS 471), salt, added flavour (vanilla).")
CORPUS = [
    BISCUIT,
    "Ingredients: Whole wheat flour.",
    "Ingredients: Cucumber, water, salt, vinegar, dill.",
    "Ingredients: Sugar, refined wheat flo",
    "Ingredients: Rice, maltodextrin.", "Ingredients: Rice, dextrose.", "Ingredients: Rice, modified starch.",
    "Ingredients: Rice, soy protein isolate.", "Ingredients: Rice, high fructose corn syrup.",
    "Ingredients: Rice, interesterified vegetable oil.", "Ingredients: Rice, edible vegetable oil (hydrogenated).",
    "Ingredients: Water, sweetener (INS 950), salt.", "Ingredients: Water, colour (INS 150d), sugar.",
    "Ingredients: Milk, flavour enhancer (INS 621).", "Ingredients: Rice, added flavour (vanilla).",
    "Ingredients: Cucumber, salt. Contains permitted natural colour.",
    "Ingredients: Sugar, cocoa. Contains permitted natural colour. May contain nuts.",
    "Ingredients: Sugar. May contain nuts and other things here.",
    "Ingredients: Mango, sugar, pectin (INS 440).", "Ingredients: Mango, sugar, gelling agent (pectin INS 440).",
    "Ingredients: Mango, sugar, gelling agent (INS 407).",
    "Ingredients: Whole wheat flour, raising agents (INS 500(ii)).",
    "Ingredients: Cucumber, salt, preservative (INS 211).", "Ingredients: Cucumber, salt, INS 999.",
    "Ingredients: Sugar, gelatin substitute (INS 171).", "Ingredients: Water, colour (E171), salt.",
    "Ingredients: Cucumber, tomato, onion, carrot, salt, vinegar, dill, turmeric, cumin, garlic, water.",
    "Ingredients: Sugar, maltodextrin.", "Ingredients: Whole wheat flour, water, salt, yeast.",
    "Ingredients: Rice, jackfruit seed paste.", "Ingredients: Salt.", "Ingredients: Salt, sugar and more things.",
    "Ingredients: Dill, turmeric, black pepper.", "Ingredients: Milk, sugar, cardamom flavouring.",
    "Ingredients: Sugar, emulsifier (INS 471, salt", "Ingredients: Sugar, emulsifier (INS 471",
    "Salt", "", "#### ~~ 1234 !!!! 5678 ---- //// 9999 ==== ++++ ",
    "Nutrition facts per 100 g: energy 450 kcal, protein 8 g, fat 20 g",
    "INGREDIENTS:\nWheat flour,\nsalt,\nsugar.\nNutrition per 100g",
    "Ingredients: Rice, salt Manufactured by XYZ Foods", "Ingredients: Sugar (12.5%), salt, rice flour.",
    "सामग्री: चावल, नमक, चीनी और अन्य सामग्री", "Ingredients:   ",
    "Ingredients: Atta, salt.", "Ingredients: Atta.", "Ingredients: Toor dal.", "Ingredients: Eggs.",
    "Ingredients: Raising agents (INS 500(ii), 503(ii)), whole wheat flour.",
    "Ingredients: Refined wheat flour, sugar, raising agent (INS 500i(ii)), salt.",
    "Ingredients: Milk, sugar, stabilizer (INS 466), thickener (INS 407).",
    "Ingredients: Sugar, Glucose-Fructose Syrup, water, carbonating agent.",
    "Ingredients: Water, sugar, acidity regulator (INS 330), antioxidant (INS 300), preservative (E211).",
    "Ingredients: Tomato, edible vegetable oil (palmolein), salt, anti-foaming agent (INS 900a).",
    "Ingredients: Mango, sugar, lemon, colour (INS 102 and 110), flavour",
    "Ingredients: Peas (60%), water, salt.", "Ingredients: Potato, sunflower oil, iodised salt, chilli, turmeric.",
    # real chips label (see tests/test_real_label.py): as printed, and as tesseract read it
    "INGREDIENTS: Potato (83%), Edible Vegetable Oil*, *Seasoning (Sugar, Iodised Salt, Milk Solids (1.2%), Spices and Condiments, Maltodextrin, Flavour (Natural and Nature Identical Flavouring Substances), Cheese Powder (0.3%), Hydrolysed Vegetable Protein, Flavour Enhancers (627, 631), Edible Vegetable Oil (Palm, Coconut). *As flavouring agent. ALLERGEN ADVICE: Contains Soy, Milk",
    'INGREDIENTS: Potato (83%), Edible Vegetable Or",\n"Seasoning (Suger, lodised Salt, Mik Solids (1.2%), Spices\nand Comiments, Maltodextrin, Flavour (Natural and Nature\nidentical Raxvouring Substances}, Cheese Powler (0.3%),\nHydrolysed Vegetable Protein, Flavour Enhancers (627,\n631), Edible Vegetadie OF (Paim, Coconut).\n\n"AS favouring agent.',
    # Option A and compound expansion
    "Ingredients: Sugar, maltodextrin, refined wheat flo", "Ingredients: Sugar, emulsifier (INS 471, salt",
    "Ingredients: Cucumber, salt (iodised, vinegar", "Ingredients: Mango, sugar, pectin (INS 440, jam",
    "Ingredients: Potato, edible vegetable oil (palm, coconut), salt.",
    "Ingredients: Potato, raising agents (INS 500(ii), INS 503(ii)), salt.",
    "Ingredients: Potato, seasoning (salt, sugar, turmeric), oil.",
    "Ingredients: Potato, seasoning (salt, sugar, colour (INS 150d)), edible vegetable oil.",
    "Ingredients: Rice, masala (spices, salt, dextrose).", "Ingredients: *(salt, sugar), rice.",
    "Ingredients: Rice, mix (a (b, c), d (e, f)), salt.",
    "Ingredients: Potato, flavour enhancers (627, 631), salt.", "Ingredients: Potato, Flavour Enhancer (627).",
    "Ingredients: Potato, raising agents (500(ii), 503(ii)), salt.", "Ingredients: Water, colours (102, 110), sugar.",
    "Ingredients: Potato, salt (500), sugar (1200).", "Ingredients: Water, sweeteners (950 and 955), citric acid.",
    "Ingredients: Potato, flavouring (627), salt.", "Ingredients: Water, emulsifiers (471, 472e), sugar.",
    "Ingredients: Potato, *Seasoning (Sugar, Salt, Edible Vegetable Oil (Palm, Coconut). *As flavouring agent.",
    "Ingredients: Potato, *Seasoning (Sugar, Maltodextrin, Edible Vegetable Oil (Palm, Coconut). *As flavouring agent.",
    "Ingredients: Rice, salt (iodised. Contains soy",
    "ingredients: PEAS, WATER, SALT", "Ingredients : Rice ; salt ; sugar.", "Ingredient: Rice, salt, sugar, ghee",
]


def py_result(text):
    a = analyse_text(text)
    return {
        "answered": a.answered, "group": a.group, "reason": a.reason, "headline": a.headline,
        "ingredients": a.ingredients, "warnings": a.warnings,
        "drivers": [{"ingredient": d.ingredient, "detail": d.detail, "source": d.source} for d in a.drivers],
        "ins": [{"code": u.code, "name": u.name, "source": u.source} for u in a.ins_mappings],
    }


NODE = """
const fs = require('fs');
const E = require(process.argv[2]).createEngine(JSON.parse(fs.readFileSync(process.argv[3], 'utf8')));
const corpus = JSON.parse(fs.readFileSync(process.argv[4], 'utf8'));
const pick = (a) => ({answered: a.answered, group: a.group, reason: a.reason, headline: a.headline,
  ingredients: a.ingredients, warnings: a.warnings, drivers: a.drivers, ins: a.ins});
process.stdout.write(JSON.stringify(corpus.map((t) => pick(E.analyseText(t)))));
"""


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / "tables.json").write_text(json.dumps(tables()))
        (td / "corpus.json").write_text(json.dumps(CORPUS))
        (td / "run.js").write_text(NODE)
        out = subprocess.run(
            ["node", str(td / "run.js"), str(ROOT / "web_preview" / "foodscan.js"), str(td / "tables.json"), str(td / "corpus.json")],
            capture_output=True, text=True)
        if out.returncode:
            print(out.stderr)
            return 2
        js = json.loads(out.stdout)
    bad = 0
    for text, j in zip(CORPUS, js):
        p = py_result(text)
        if p != j:
            bad += 1
            print("MISMATCH:", repr(text))
            for k in p:
                if p[k] != j[k]:
                    print(f"  {k}:\n    py: {p[k]!r}\n    js: {j[k]!r}")
    print(f"{len(CORPUS) - bad}/{len(CORPUS)} texts identical between Python and JS")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
