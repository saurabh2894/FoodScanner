"""Out-of-sample harness (scripts/oos_eval.py, scripts/oos_draw.py): mechanics only, on SYNTHETIC strings written for these tests. They are not labels and not evidence."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
for p in (REPO, REPO / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import pytest

import oos_eval as oe


@pytest.mark.parametrize("term, text, hit", [
    ("cumin seed", "Cumin Seeds (2%)", "cumin seeds"), ("cumin seed", "cumin-seed powder", "cumin-seed"), ("coriander leaf", "Coriander leaves", "coriander leaves"),
    ("thyme", "Thyme, sage", "thyme"), ("sage", "sagebrush", None), ("basil", "basilic", None), ("dill weed", "dill weeds", "dill weeds"), ("oregano", "Oregano.", "oregano")])
def test_term_pattern_matches_whole_words_and_plural_forms_only(term, text, hit):
    m = oe.term_pattern(term).search(text)
    assert (m.group(0).lower() if m else None) == hit


def test_judge_classifies_each_mention_after_build():
    before = {"unassessed": ["oregano", "cumin seeds"], "ingredients": ["salt"]}
    after = {"unassessed": ["cumin seeds"], "ingredients": ["salt", "oregano"]}
    j = oe.judge("salt, oregano, cumin seeds, paprika extract", before, after)["mentions"]
    got = {m["mention"]: (m["after"], m["was_unassessed_before"]) for m in j}
    assert got["oregano"] == ("recognised", True) and got["cumin seeds"] == ("NOT recognised", True) and got["paprika"] == ("inside another item", False)


def test_sha_mismatch_stops_the_run_and_never_redraws(tmp_path):
    cache = tmp_path / "cache"
    (cache / "inputs").mkdir(parents=True)
    (cache / "inputs" / "S01.txt").write_text("synthetic text", encoding="utf-8")
    man = {"retrieved": "x", "labels": [{"id": "S01", "code": "0", "target": "thyme", "cache_file": "inputs/S01.txt (gitignored)", "text_sha256": "0" * 64}]}
    with pytest.raises(RuntimeError, match="sha256"):
        oe.evaluate(man, cache, REPO / "src", REPO / "src")


def test_end_to_end_two_fresh_processes_report_no_change_for_identical_builds(tmp_path):
    cache = tmp_path / "cache"
    (cache / "inputs").mkdir(parents=True)
    t = "Ingredients: Wheat flour, salt, thyme, oregano."
    (cache / "inputs" / "S01.txt").write_text(t, encoding="utf-8")
    man = {"retrieved": "x", "labels": [{"id": "S01", "code": "0", "target": "thyme", "cache_file": "inputs/S01.txt (gitignored)", "text_sha256": hashlib.sha256(t.encode()).hexdigest()}]}
    for d in ("a", "b"):
        shutil.copytree(REPO / "src", tmp_path / d / "src", ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
    res = oe.evaluate(man, cache, tmp_path / "a" / "src", tmp_path / "b" / "src")
    r = res["labels"][0]
    assert r["changed_fields"] == [] and r["newly_recognised_items"] == [] and r["newly_unassessed_items"] == []
    assert {m["after"] for m in r["mentions"]} == {"recognised"}


def test_committed_manifest_and_gitignore_keep_database_text_out_of_the_repo():
    ign = (REPO / ".gitignore").read_text()
    assert "data/cache/" in ign
    mf = REPO / "evaluation" / "out_of_sample_herb_spice_1" / "manifest.json"
    if mf.exists():
        m = json.loads(mf.read_text(encoding="utf-8"))
        assert all(set(l) >= {"code", "record", "text_sha256", "terms"} and "ingredients_text" not in l and "text" not in l for l in m["labels"])
        assert not (REPO / "evaluation" / "out_of_sample_herb_spice_1" / "inputs").exists()
    tracked = subprocess.run(["git", "ls-files", "data/cache"], capture_output=True, text=True, cwd=REPO).stdout.strip()
    assert tracked == ""
