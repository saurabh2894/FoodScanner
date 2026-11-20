import pytest

from foodscan import cli
from foodscan.ocr import OcrUnavailable
from foodscan.pipeline import NOT_ENOUGH, analyse_image, analyse_text

BISCUIT = (
    "Ingredients: Refined wheat flour, sugar, edible vegetable oil (palmolein), "
    "invert syrup, raising agents (INS 500(ii), INS 503(ii)), emulsifier "
    "(INS 471), salt, added flavour (vanilla)."
)


def test_answers_group4_with_drivers_and_ins_sources():
    a = analyse_text(BISCUIT)
    assert a.answered and a.group == 4 and a.drivers
    assert {u.code for u in a.ins_mappings} == {"500(ii)", "503(ii)", "471"}


def test_answers_group1_and_group3():
    assert analyse_text("Ingredients: Whole wheat flour.").group == 1
    assert analyse_text("Ingredients: Cucumber, water, salt, vinegar, dill.").group == 3


def test_truncated_list_abstains_research_example():
    a = analyse_text("Ingredients: Sugar, refined wheat flo")
    assert not a.answered and a.group is None
    assert "truncated" in a.reason and a.headline.startswith(NOT_ENOUGH)


def test_unclosed_bracket_without_marker_abstains():
    a = analyse_text("Ingredients: Cucumber, salt (iodised, vinegar")
    assert not a.answered and "truncated" in a.reason


# --- Option A (user decision): strong marker survives truncation, with a warning ------
def test_truncated_list_with_strong_marker_is_group4_with_warning():
    a = analyse_text("Ingredients: Sugar, maltodextrin, refined wheat flo")
    assert a.answered and a.group == 4
    assert a.warnings and "incomplete" in a.warnings[0]


def test_unclosed_bracket_with_strong_marker_is_group4_with_warning():
    a = analyse_text("Ingredients: Sugar, emulsifier (INS 471, salt")
    assert a.answered and a.group == 4 and "unclosed bracket" in a.warnings[0]


def test_option_a_does_not_loosen_other_truncation_cases():
    assert not analyse_text("Ingredients: Sugar, refined wheat flo").answered       # research example
    assert not analyse_text("Ingredients: Mango, sugar, pectin (INS 440, jam").answered  # weak marker only


def test_complete_list_has_no_warning():
    assert analyse_text(BISCUIT).warnings == []


def test_little_text_abstains():
    a = analyse_text("Salt")
    assert not a.answered and "little text" in a.reason
    assert not analyse_text("").answered


def test_noise_abstains():
    a = analyse_text("#### ~~ 1234 !!!! 5678 ---- //// 9999 ==== ++++ ")
    assert not a.answered


def test_no_ingredient_list_abstains():
    a = analyse_text("Nutrition facts per 100 g: energy 450 kcal, protein 8 g, fat 20 g")
    assert not a.answered and "no ingredient list" in a.reason


def test_uncertain_classification_abstains_with_reason():
    a = analyse_text("Ingredients: Mango, sugar, pectin (INS 440).")
    assert not a.answered and "weak" in a.reason and a.group is None


def test_abstention_never_carries_a_group_or_health_word():
    for t in ["Salt", "Ingredients: Sugar, refined wheat flo", "Ingredients: Dill, turmeric."]:
        a = analyse_text(t)
        assert a.group is None
        assert not any(w in a.headline.lower() for w in ("healthy", "unsafe", "should not"))


def test_image_path_uses_injected_ocr():
    class Fake:
        def extract_text(self, p):
            return "Ingredients: Whole wheat flour."

    assert analyse_image("whatever.jpg", ocr=Fake()).group == 1


def test_ocr_unavailable_propagates_as_error_not_abstention():
    class Broken:
        def extract_text(self, p):
            raise OcrUnavailable("Tesseract OCR is not installed")

    with pytest.raises(OcrUnavailable):
        analyse_image("x.jpg", ocr=Broken())


def test_cli_text_mode(tmp_path, capsys):
    f = tmp_path / "l.txt"
    f.write_text(BISCUIT)
    assert cli.main(["classify", "--text", str(f)]) == 0
    out = capsys.readouterr().out
    assert "NOVA group 4" in out and "Driven by" in out and "INS 471" in out


def test_cli_abstention_output(tmp_path, capsys):
    f = tmp_path / "l.txt"
    f.write_text("Ingredients: Sugar, refined wheat flo")
    cli.main(["classify", "--text", str(f)])
    assert "Not enough information" in capsys.readouterr().out


def test_cli_missing_tesseract_is_clear_error(monkeypatch, tmp_path, capsys):
    import pytesseract
    monkeypatch.setattr(pytesseract, "get_tesseract_version",
                        lambda: (_ for _ in ()).throw(pytesseract.TesseractNotFoundError()))
    from PIL import Image
    img = tmp_path / "a.png"
    Image.new("RGB", (10, 10)).save(img)
    assert cli.main(["classify", str(img)]) == 2
    assert "Tesseract OCR is not installed" in capsys.readouterr().err
