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
COLON_DRIVER_LABEL = "Ingredients: Rice flour: 60 g."
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
    ("Ingredients: Sugar: 12%, salt.", None, "complete",
     [("Sugar: 12%", None), ("salt", None)]),
    (COLON_DRIVER_LABEL, 1, "complete", [("Rice flour: 60 g", None)]),
    ("Ingredients: Rice: 60% wheat, salt.", None, "uncertain",
     [("Rice: 60% wheat", None), ("salt", None)]),
    ("Rice 60% salt", None, "uncertain", [("Rice 60% salt", None)]),
    ("Rice 60%", 1, "complete", [("Rice", "(60%)")]),
]


# The web views split colon quantities while the CLI keeps their original spelling.
WEB_INGREDIENTS = {
    "Ingredients: Rice brown: 60%, salt.": [("Rice brown", "(60%)"), ("salt", None)],
    "Ingredients: Sugar: 12%, salt.": [("Sugar", "(12%)"), ("salt", None)],
    COLON_DRIVER_LABEL: [("Rice flour", "(60 g)")],
}


def expected_display(text, group, completeness, ingredients):
    analysis = analyse_text(text, source="text")
    assert analysis.group == group
    assert analysis.completeness["status"] == completeness
    classification = ("Classification: NOVA group assigned." if group is not None else
                      "Classification: no NOVA group assigned.")
    reason = f"Reason: {analysis.reason}" if group is None else None
    assessment = None
    if analysis.completeness["words"]["in_list"]:
        counts = analysis.completeness["assessed"]
        assessment = ("This product could not be assigned a NOVA group." if group is None else
                      f'{counts["not_assessed"]} of {counts["items"]} items are not fully assessed.')
    return analysis, [classification, reason, f"Text completeness: {completeness}",
                      WEB_INGREDIENTS.get(text, ingredients), assessment]


@pytest.mark.parametrize("text,group,completeness,ingredients", CASES)
def test_python_result_display(text, group, completeness, ingredients):
    analysis, (classification, reason, coverage, web_ingredients, assessment) = expected_display(text, group, completeness, ingredients)
    extracted = analysis.ingredients.copy()
    if text in WEB_INGREDIENTS:
        assert extracted == [name for name, _ in ingredients]
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
    assert items == web_ingredients
    caption_element = soup.select_one(".coverage-caption")
    if assessment is None:
        assert caption_element is None
    else:
        caption = caption_element.get_text()
        assert assessment in caption
        if group is None:
            assert "fully assessed" not in caption
    assert analysis.ingredients == extracted


def test_short_unheaded_rice_flour_photo_text_shows_abstention_reason():
    analysis = analyse_text("Rice flour 60%", source="ocr")
    assert analysis.group is None
    assert f"Reason: {analysis.reason}" in format_analysis(analysis).splitlines()


@pytest.mark.parametrize(("text", "group", "caption"), [
    ("Ingredients: Sugar: 12%, salt.", None,
     "3 words read as ingredients (100% of the list region); 0 not read, "
     "0 unaccounted, 0 set aside after the list, 0 declared. "
     "This product could not be assigned a NOVA group."),
    (COLON_DRIVER_LABEL, 1,
     "4 words read as ingredients (100% of the list region); 0 not read, "
     "0 unaccounted, 0 set aside after the list, 0 declared; 0 of 1 items outside the vocabulary."),
])
def test_cli_coverage_caption(text, group, caption):
    analysis = analyse_text(text, source="text")
    assert analysis.group == group
    displayed = next(line for line in format_analysis(analysis).splitlines()
                     if "words read as ingredients" in line)
    assert displayed == (
        caption + " All recognised text spans accounted for. "
        "This is not a guarantee that characters, digits or the list are complete or correct."
    )


def test_colon_quantity_in_cli_and_flask_driver():
    analysis = analyse_text(COLON_DRIVER_LABEL, source="text")
    assert analysis.group == 1
    driver, = analysis.drivers
    assert driver.ingredient == "Rice flour: 60 g"
    cli = format_analysis(analysis).splitlines()
    assert cli[cli.index("Driven by:") + 1] == (
        f"  - Rice flour  (60 g): {driver.detail}  [{driver.source}]"
    )

    with create_app().test_request_context():
        html = render_template("index.html", result=analysis, error=None)
    soup = BeautifulSoup(html, "html.parser")
    driver_item = soup.find("h3", string="Driven by").find_next_sibling("ul").li
    assert driver_item.select_one(".driver-name").get_text() == "Rice flour"
    assert driver_item.select_one(".ingredient-quantity").get_text() == "(60 g)"
    assert driver.ingredient == "Rice flour: 60 g"


def test_browser_result_display_matches_python():
    cases = [
        [case[0], expected_display(*case)[1],
         ["Rice flour", "(60 g)"] if case[0] == COLON_DRIVER_LABEL else None]
        for case in CASES
    ]
    result = subprocess.run(
        ["node", str(ROOT / "tests/js/result_display.js")],
        input=json.dumps(cases), capture_output=True, text=True, timeout=45,
    )
    assert result.returncode == 0, result.stderr
