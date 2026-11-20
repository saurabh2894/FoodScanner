"""Render the synthetic example lists from research/02 as PNGs (plumbing smoke test only).

These are NOT real labels; accuracy on them says nothing about real packs.
Usage: python scripts/make_synthetic.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "data" / "synthetic" / "samples"
EXAMPLES = {
    "syn_group1_atta.png": "Ingredients: Whole wheat flour.",
    "syn_group4_biscuit.png": (
        "Ingredients: Refined wheat flour, sugar, edible vegetable oil (palmolein), invert syrup, "
        "raising agents (INS 500(ii), INS 503(ii)), emulsifier (INS 471), salt, added flavour (vanilla)."
    ),
    "syn_group3_pickle.png": "Ingredients: Cucumber, water, salt, vinegar, dill.",
    "syn_truncated.png": "Ingredients: Sugar, refined wheat flo",
}


def wrap(text, width=48):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    return lines + [cur]


OUT.mkdir(parents=True, exist_ok=True)
font = ImageFont.load_default(size=34)
for name, text in EXAMPLES.items():
    lines = wrap(text)
    img = Image.new("RGB", (1300, 70 + 50 * len(lines)), "white")
    d = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        d.text((30, 30 + 50 * i), line, fill="black", font=font)
    img.save(OUT / name)
    print("wrote", OUT / name)
