"""WS1 demand miner (scripts/mine_unassessed.py): read-only, ranked, stream-separated inventory of unassessed terms."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest

from scripts import mine_unassessed as mu


def fake_analyse(text: str) -> list[str]:
    # stands in for the classifier: the unrecognised items are the words wrapped in ~...~ in the test inputs
    return [w.strip("~,. ") for w in text.replace("\n", " ").split() if w.startswith("~")]


def build_tree(tmp: Path) -> Path:
    ev = tmp / "evaluation"
    (ev / "fresh_batch_1" / "inputs").mkdir(parents=True)
    (ev / "fresh_batch_2" / "inputs").mkdir(parents=True)
    (ev / "negation_addendum").mkdir()
    (ev / "fresh_batch_1" / "inputs" / "N01.txt").write_text("rice ~zorbium, ~quux", encoding="utf-8")
    (ev / "fresh_batch_2" / "inputs" / "M01.txt").write_text("rice ~zorbium", encoding="utf-8")
    (ev / "negation_addendum" / "manifest.json").write_text(json.dumps({"R1": {"code": "8906010090197"}}), encoding="utf-8")
    # recorded paste results (input record: group is a number) and a summary dict whose `unassessed` lists INPUT IDS (must be ignored)
    (ev / "fresh_batch_1" / "paste.json").write_text(json.dumps({"N01": {"group": None, "unassessed": ["Zorbium (3%)", "Fenugreek", "Mixed Fruit (group name; its contents were assessed separately)"]}}), encoding="utf-8")
    (ev / "fresh_batch_1" / "summary.json").write_text(json.dumps({"changed_inputs": {"group": ["b1/N01"], "unassessed": ["b1/N01", "b2/M01"]}}), encoding="utf-8")
    photo = "x\nNOT ASSESSED\n\nNot in the vocabulary, or a group name whose contents were assessed. These did not affect the group.\n\nZorbium\nblurry sp1ce\nGroup (group name; its contents were assessed separately)\nRaw text analysed"
    (ev / "fresh_batch_2" / "photo.json").write_text(json.dumps([{"id": "M01", "result": photo}, {"image": "/x/img/N_8906010090197.jpg", "result": photo}]), encoding="utf-8")
    return ev


def digest(root: Path) -> dict[str, str]:
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob("*")) if p.is_file()}


def test_term_key_and_noise():
    assert mu.term_key("Zorbium (3%)") == "zorbium"
    assert mu.term_key("Dried Curry Leaves (0.5%)") == "dried curry leaves"
    assert mu.term_key("  Garam   Masala, ") == "garam masala"
    assert mu.is_noise("631") and mu.is_noise("ac") and mu.is_noise("quot") and not mu.is_noise("fenugreek")


def test_parse_not_assessed_skips_the_explainer_and_group_names_and_stops_at_headings():
    text = ("NOT ASSESSED\n\nNot in the vocabulary, or a group name whose contents were assessed. These did not affect the group.\n\n"
            "alpha\nbeta (group name; its contents were assessed separately)\ngamma\nCOMPLETENESS: UNCERTAIN\ndelta")
    assert mu.parse_not_assessed(text) == ["alpha", "gamma"]


def test_parse_not_assessed_skips_current_browser_caption():
    template = (REPO_ROOT / "web_preview" / "template.html").read_text(encoding="utf-8")
    caption = re.search(r'el\("p", \{ "class": "hint", text: "(Not in the vocabulary[^"]+)" \}\)', template)
    assert caption
    assert mu.parse_not_assessed(f"NOT ASSESSED\n\n{caption.group(1)}\n\nSeasoning: Onion\nRaw text analysed") == ["Seasoning: Onion"]


def test_canon_id_covers_keys_file_names_and_negation_codes():
    codes = {"8906010090197": "neg/R1"}
    assert mu.canon_id("b1/N05", None, codes) == "b1/N05"
    assert mu.canon_id("dev/F01", None, codes) == "dev15/F01"
    assert mu.canon_id("Q02", "fresh_batch_3", codes) == "b3/Q02"
    assert mu.canon_id("/tmp/img/M03_8904083302292.jpg", None, codes) == "b2/M03"
    assert mu.canon_id("/tmp/img/N_8906010090197.jpg", None, codes) == "neg/R1"
    assert mu.canon_id("/tmp/img/millet_puff_label.jpg", None, codes) is None


def test_ranking_streams_and_photo_only_flagging(tmp_path):
    ev = build_tree(tmp_path)
    rows = {r["term"]: r for r in mu.finish(mu.mine(ev, fake_analyse), lambda raw: raw.lower() == "fenugreek")}
    z = rows["zorbium"]
    assert z["distinct_paste_inputs"] == 2 and z["input_ids"][:2] == ["b1/N01", "b2/M01"] and z["rank_open"] == 1
    assert z["live_inputs"] == 2 and z["recorded_paste_mentions"] == 1 and z["photo_mentions"] == 2
    assert not z["photo_only"] and not z["recognised_now"]
    assert rows["quux"]["distinct_paste_inputs"] == 1 and rows["quux"]["rank_open"] == 2
    assert rows["fenugreek"]["recognised_now"] and rows["fenugreek"]["rank_open"] is None          # closed gaps stay visible but do not rank
    assert rows["blurry sp1ce"]["photo_only"] and rows["blurry sp1ce"]["rank_open"] is None          # OCR damage is never demand on its own
    assert "mixed fruit" not in rows and "group" not in rows                                          # group-name lines are excluded
    assert not any("b1/N01" == t or "b2/m01" == t for t in rows)                                      # the summary dict's list of input IDs was not read as terms
    assert "neg/R1" in rows["blurry sp1ce"]["input_ids"]


def test_read_only_and_refuses_to_overwrite(tmp_path, monkeypatch):
    ev = build_tree(tmp_path)
    before = digest(ev)
    out = tmp_path / "out"
    monkeypatch.setattr(mu, "default_analysers", lambda: (fake_analyse, lambda raw: False))
    assert mu.main(["--evaluation", str(ev), "--out", str(out)]) == 0
    assert digest(ev) == before                                                                        # nothing under evaluation/ was touched
    assert sorted(p.name for p in out.iterdir()) == ["inventory.csv", "inventory.json"]
    first = (out / "inventory.json").read_text()
    assert mu.main(["--evaluation", str(ev), "--out", str(out)]) == 2                                  # existing inventory: refused
    assert (out / "inventory.json").read_text() == first
    assert mu.main(["--evaluation", str(ev), "--out", str(out), "--force"]) == 0
    assert (out / "inventory.json").read_text() == first                                               # deterministic


def test_real_evidence_has_known_open_and_closed_terms():
    analyse, recognised = mu.default_analysers()
    rows = {r["term"]: r for r in mu.finish(mu.mine(REPO_ROOT / "evaluation", analyse), recognised)}
    assert rows["cocoa solids"]["rank_open"] is not None and rows["cocoa solids"]["distinct_paste_inputs"] >= 5      # an open gap the evidence repeats
    assert rows["fenugreek"]["recognised_now"] and rows["fenugreek"]["distinct_paste_inputs"] >= 5                    # a gap closed by lexicon-1
    assert not any(i.startswith("?") for r in rows.values() if r["distinct_paste_inputs"] for i in r["input_ids"][: r["distinct_paste_inputs"]])
    assert all(r["rank_open"] is None for r in rows.values() if r["photo_only"] or r["noise"] or r["recognised_now"])


@pytest.mark.parametrize("term", [
    "wheat gluten", "whey powder", "hydrolysed vegetable protein",
    "lemon juice concentrate", "apple juice concentrate", "fructose",
])
def test_current_marker_route_closes_historical_vocabulary_gap(term):
    _, recognised = mu.default_analysers()
    assert recognised(term)
    inv = mu.Inventory()
    inv.add(term, "paste_recorded", "b1/N01", "historical.json")
    row, = mu.finish(inv, recognised)
    assert row["recognised_now"] and row["rank_open"] is None
    assert row["recorded_paste_mentions"] == 1 and row["live_inputs"] == 0


@pytest.mark.parametrize("term", [
    "cocoa solids",  # liquid glucose left this list in fardet-markers-24 (now a marker)
     "guar gum", "Synthetic Vinegar",
    "wheat gluten, zorbium", "whey powder, zorbium",
    "lemon juice concentrate (zorbium)",
])
def test_marker_substring_or_group4_answer_does_not_hide_unresolved_content(term):
    _, recognised = mu.default_analysers()
    assert not recognised(term)


def test_real_inventory_has_no_live_gap_closed_by_simple_marker_route():
    analyse, recognised = mu.default_analysers()
    rows = mu.finish(mu.mine(REPO_ROOT / "evaluation", analyse), recognised)
    # Current live context beats historical standalone probes.
    assert not [r["term"] for r in rows if r["live_inputs"] and r["recognised_now"]
                and r["term"] in {"wheat gluten", "whey powder", "hydrolysed vegetable protein",
                                  "lemon juice concentrate", "apple juice concentrate", "fructose", "whey solids"}]
