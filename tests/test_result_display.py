import json
import subprocess
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from flask import render_template

from foodscan.cli import format_analysis
from foodscan.pipeline import analyse_text
from foodscan.web.app import create_app

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ("Ingredients: Rice 60%, jackfruit seed paste.", None, "complete",
     [("Rice", "(60%)"), ("jackfruit seed paste", None)]),
    ("Ingredients: Noodles: Rice 60%, salt. Masala: Sugar (12.5%), flavour.", 4, "complete",
     [("Rice", "(60%)"), ("salt", None), ("Sugar", "(12.5%)"), ("flavour", None)]),
    ("Ingredients: Rice, flavour. Sugar, vinegar, oil.", 4, "uncertain",
     [("Rice", None), ("flavour", None)]),
    ("Nutrition facts only: energy 450 kcal", None, "uncertain", []),
    ("Rice flour 60%", 1, "complete", [("Rice flour", "(60%)")]),
    ("Wheat flour 50%, Sugar 20%, Salt", None, "complete",
     [("Wheat flour", "(50%)"), ("Sugar", "(20%)"), ("Salt", None)]),
    ("Sugar 20%, Salt", None, "complete", [("Sugar", "(20%)"), ("Salt", None)]),
    ("Ingredients: Cucumber, water, salt, vinegar, dill.", 3, "complete",
     [(name, None) for name in ("Cucumber", "water", "salt", "vinegar", "dill")]),
    ("Rice brown:", None, "uncertain", [("Rice brown:", None)]),
    ("Ingredients: Rice brown: 60%, salt.", 3, "complete",
     [("Rice brown: 60%", None), ("salt", None)]),
    ("Rice 60% salt", None, "uncertain", [("Rice 60% salt", None)]),
    ("Rice 60%", 1, "complete", [("Rice", "(60%)")]),
]


def expected_display(text, group, completeness, ingredients):
    analysis = analyse_text(text, source="text")
    assert analysis.group == group
    assert analysis.completeness["status"] == completeness
    classification = ("Classification: NOVA group assigned." if group is not None else
                      "Classification: no NOVA group assigned.")
    reason = f"Reason: {analysis.reason}" if group is None else None
    return analysis, [classification, reason, f"Text completeness: {completeness}", ingredients]


@pytest.mark.parametrize("text,group,completeness,ingredients", CASES)
def test_python_result_display(text, group, completeness, ingredients):
    analysis, (classification, reason, coverage, _) = expected_display(text, group, completeness, ingredients)
    extracted = analysis.ingredients.copy()
    output = format_analysis(analysis).splitlines()
    assert classification in output
    assert next((line for line in output if line.startswith("Reason: ")), None) == reason
    assert coverage in output
    for number, (name, quantity) in enumerate(ingredients, 1):
        assert f"  {number}. {name}" + (f"  {quantity}" if quantity else "") in output

    with create_app().test_request_context():
        html = render_template("index.html", result=analysis, error=None)
    soup = BeautifulSoup(html, "html.parser")
    assert soup.select_one(".classification-status").get_text() == classification
    reason_element = soup.select_one(".classification-reason")
    assert (reason_element.get_text() if reason_element else None) == reason
    assert soup.select_one(".text-completeness").get_text() == coverage
    items = []
    for name in soup.select(".ingredient-name"):
        tag = name.find_next_sibling(class_="ingredient-quantity")
        items.append((name.get_text(), tag.get_text() if tag else None))
    assert items == ingredients
    assert analysis.ingredients == extracted


def test_short_unheaded_rice_flour_photo_text_shows_abstention_reason():
    analysis = analyse_text("Rice flour 60%", source="ocr")
    assert analysis.group is None
    assert f"Reason: {analysis.reason}" in format_analysis(analysis).splitlines()


def test_browser_result_display_matches_python():
    cases = [[case[0], expected_display(*case)[1]] for case in CASES]
    result = subprocess.run(
        ["node", str(ROOT / "tests/js/result_display.js")],
        input=json.dumps(cases), capture_output=True, text=True, timeout=45,
    )
    assert result.returncode == 0, result.stderr
