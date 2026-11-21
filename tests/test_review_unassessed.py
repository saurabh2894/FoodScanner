"""'Not assessed': what the classifier could not judge is shown instead of staying invisible.

Review finding: once any strong marker is found, ingredients outside the vocabulary (khaand, amchur, ...)
vanished from the output; a compound head dropped during expansion left no trace either. This changes
what is SHOWN only. No classification rule changes.
"""
from foodscan import cli
from foodscan.pipeline import analyse_text
from test_review_labels import MILLET_PUFF


def test_group4_result_still_lists_what_was_not_assessed():
    a = analyse_text(MILLET_PUFF, source="text")
    assert a.group == 4
    for leaf in ("Amchur", "Tamarind"):                       # still outside the vocabulary
        assert leaf in a.unassessed, leaf
    # ordinary staples the vocabulary layer now recognises (they used to be listed here): coverage grew, so they are assessed
    for leaf in ("Jowar", "Foxtail Millet", "Corn", "Raw Sugar", "Rice", "Salt"):
        assert leaf not in a.unassessed, leaf
    assert not any("Flavours" in u for u in a.unassessed)                      # a marker is assessed


def test_expanded_group_names_are_listed_not_dropped():
    a = analyse_text(MILLET_PUFF, source="text")
    heads = [u for u in a.unassessed if "group name" in u]
    assert any(h.startswith("Supergrain Blend") for h in heads)
    assert any(h.startswith("Vegetables and Spices") for h in heads)


def test_unglued_head_with_unknown_prefix_is_visible():
    a = analyse_text("Ingredients: Rice, Mystery Seasoning : Dehydrated Vegetables(Garlic, Onion, Tomato), flavour.")
    assert a.group == 4
    assert any(u.startswith("Mystery Seasoning : Dehydrated Vegetables") and "group name" in u for u in a.unassessed)
    assert any("section label" in w for w in a.warnings)


def test_abstentions_carry_the_list_too():
    a = analyse_text("Ingredients: Rice, jackfruit seed paste, jaggery syrup.")
    assert not a.answered
    assert a.unassessed == ["jackfruit seed paste", "jaggery syrup"]


def test_fully_recognised_list_has_nothing_unassessed():
    assert analyse_text("Ingredients: Cucumber, water, salt, vinegar, dill.").unassessed == []
    assert analyse_text("Ingredients: Milk", source="text").unassessed == []


def test_duplicates_are_listed_once():
    # FIXTURE INTENT: generic unknown handling, so the token is unmistakably synthetic (real food names keep turning into vocabulary: jackfruit did in class-bulk-3). Subject unchanged: a repeated unassessed item is listed once.
    a = analyse_text("Ingredients: Rice, XQ9, XQ9, flavour.")
    assert a.unassessed == ["XQ9"]


def test_additives_and_markers_count_as_assessed():
    a = analyse_text("Ingredients: Rice, preservative (INS 211), emulsifier (INS 471), maltodextrin, INS 999.")
    assert a.unassessed == []


def test_cli_prints_not_assessed(tmp_path, capsys):
    f = tmp_path / "l.txt"
    f.write_text(MILLET_PUFF)
    cli.main(["classify", "--text", str(f)])
    out = capsys.readouterr().out
    assert "Not assessed" in out and "Amchur" in out and "NOVA group 4" in out


def test_cli_omits_the_line_when_everything_was_assessed(tmp_path, capsys):
    f = tmp_path / "l.txt"
    f.write_text("Ingredients: Cucumber, water, salt, vinegar, dill.")
    cli.main(["classify", "--text", str(f)])
    assert "Not assessed" not in capsys.readouterr().out
