"""Rotated-retry fallback (pipeline.analyse_image) and retake guidance. The OCR engine is faked: no tesseract needed."""
import pytest

from foodscan import pipeline
from foodscan.pipeline import RETAKE_GUIDANCE, analyse_image

NOISE = "Ee a TT Re ee Ts Cpt\n8 Es 3 or SEE aa Rs PE A a Sins BO iE\n"
GOOD = "Ingredients: Rice, Salt, Sugar, Water, Cumin\n"
CODES = "Ingredients: Water, Sugar, Acidity Regulator (INS 330), Preservative (INS 211)\n"


class Fake:
    def __init__(self, first=NOISE, alt=NOISE, rot=None):
        self.first, self.alt, self.rot, self.calls = first, alt, rot or {}, []

    def extract_text(self, p):
        self.calls.append("first"); return self.first

    def extract_text_alt(self, p):
        self.calls.append("alt"); return self.alt

    def extract_text_rotated(self, p, deg):
        self.calls.append(deg); return self.rot.get(deg, NOISE)


@pytest.fixture
def rotations_on(monkeypatch):
    monkeypatch.setattr(pipeline, "ROTATIONS", (90, 270, 180))      # the retries ship OFF; these tests cover the code path when enabled


def test_rotated_retry_runs_only_when_no_list_and_finds_the_sideways_list(rotations_on):
    e = Fake(rot={270: GOOD})
    a = analyse_image("x.jpg", e)
    assert e.calls == ["first", "alt", 90, 270]            # 90 tried first, 270 found the list, 180 not needed
    assert a.ingredients and a.retake is None
    assert any("turning the photo 270 degrees" in w for w in a.warnings)


def test_no_rotated_retry_when_the_first_reading_found_a_list(rotations_on):
    e = Fake(first="Ingredients: Rice, xyzgum", alt="Ingredients: Rice, xyzgum", rot={90: GOOD})     # a list is found but not clean: second pass yes, rotation no
    a = analyse_image("x.jpg", e)
    assert "alt" in e.calls and not any(isinstance(c, int) for c in e.calls)
    assert a.ingredients and not any("turning the photo" in w for w in a.warnings)


def test_a_clean_first_reading_triggers_no_second_or_rotated_pass():
    e = Fake(first=GOOD)
    analyse_image("x.jpg", e)
    assert e.calls == ["first"] or e.calls == ["first", "alt"]       # unchanged behaviour: second pass only when not clean
    assert not any(isinstance(c, int) for c in e.calls)


def test_still_no_list_gives_concrete_retake_guidance_and_tries_all_rotations(rotations_on):
    e = Fake()
    a = analyse_image("x.jpg", e)
    assert [c for c in e.calls if isinstance(c, int)] == [90, 270, 180]
    assert not a.answered and a.retake == RETAKE_GUIDANCE
    for word in ("flat surface", "good even light", "straight-on", "close"):
        assert word in a.retake


def test_retake_guidance_is_not_attached_to_a_found_list_or_to_pasted_text():
    assert analyse_image("x.jpg", Fake(first=GOOD)).retake is None
    assert pipeline.analyse_text("Ingredients:", source="text").retake is None


def test_a_rotated_reading_is_used_only_when_it_beats_the_current_one(rotations_on):
    # first reading finds a partial list; rotation is never tried because a list was found
    e = Fake(first="Ingredients: Rice, xyzgum", alt="Ingredients: Rice, xyzgum", rot={90: GOOD})
    a = analyse_image("x.jpg", e)
    assert 90 not in e.calls and a.ingredients


def test_engine_without_rotation_support_keeps_working_when_rotations_are_on(rotations_on):
    class Plain:
        def extract_text(self, p): return NOISE
        def extract_text_alt(self, p): return NOISE
    a = analyse_image("x.jpg", Plain())
    assert not a.answered and a.retake == RETAKE_GUIDANCE


def test_rotation_ships_off_and_retake_guidance_stays():
    assert pipeline.ROTATIONS == ()
    e = Fake(rot={90: GOOD, 270: GOOD, 180: GOOD})
    a = analyse_image("x.jpg", e)
    assert not any(isinstance(c, int) for c in e.calls)               # no rotated reading is taken
    assert not a.answered and a.retake == RETAKE_GUIDANCE
    assert "even after" not in a.retake and "90" not in a.retake


def test_retake_guidance_also_for_engines_without_a_second_pass():
    class Plain:
        def extract_text(self, p): return NOISE
    assert analyse_image("x.jpg", Plain()).retake == RETAKE_GUIDANCE
