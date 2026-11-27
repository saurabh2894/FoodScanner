import importlib.util
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_lexicon.py"
spec = importlib.util.spec_from_file_location("audit_lexicon", SCRIPT)
audit_lexicon = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_lexicon)


@pytest.fixture
def resources(tmp_path):
    def write(lexicon="", synonyms=""):
        (tmp_path / "lexicon.csv").write_text("term,kind,source\n" + lexicon, encoding="utf-8")
        (tmp_path / "synonyms.csv").write_text("from,to,source\n" + synonyms, encoding="utf-8")
        return tmp_path

    return write


def test_duplicates_normalised_collisions_and_kinds(resources):
    directory = resources(
        "black-bean,legume,source\n"
        "black-bean,vegetable,source\n"
        "Black bean,legume,source\n",
        "black-bean,bean,source\nBlack bean,pea,source\n",
    )
    findings = audit_lexicon.audit(directory)
    duplicates = "\n".join(findings["Duplicate entries"])
    collisions = "\n".join(findings["Normalised key collisions"])
    categories = "\n".join(findings["Inconsistent categories"])
    assert "lexicon.csv: 'black-bean' at lines [2, 3]" in duplicates
    assert "across tables: 'black-bean'" in duplicates
    assert "lexicon.csv: 'black bean'" in collisions
    assert "across tables: 'black bean'" in collisions
    assert "'legume' (line 2)" in categories and "'vegetable' (line 3)" in categories
    assert "conflicting targets" in categories


def test_malformed_records_are_reported_and_later_rows_are_checked(resources):
    directory = resources(
        'apple,fruit,"bad "quote" here"\n'
        "pear,,source\n"
        "pear,invalid,source\n"
        "extra,fruit,source,unexpected\n"
        "extra,vegetable,source\n"
        "missing,fruit\n"
        "plum,fruit,\n",
    )
    findings = audit_lexicon.audit(directory)
    malformed = "\n".join(findings["Empty or malformed fields"])
    assert "lexicon.csv:2: malformed CSV" in malformed
    assert "lexicon.csv:3: empty kind" in malformed
    assert "lexicon.csv:5: expected 3 fields, got 4" in malformed
    assert "lexicon.csv:7: expected 3 fields, got 2" in malformed
    assert "lexicon.csv:8: empty source" in malformed
    assert "'pear' at lines [3, 4]" in "\n".join(findings["Duplicate entries"])
    assert "'extra' at lines [5, 6]" in "\n".join(findings["Duplicate entries"])
    assert "unknown kind 'invalid'" in "\n".join(findings["Inconsistent categories"])
    assert "lexicon.csv: 'extra':" in "\n".join(findings["Inconsistent categories"])


def test_valid_multiline_source_and_curly_apostrophe(resources):
    directory = resources(
        'lady’s-finger,vegetable,"source on\nmultiple lines"\n'
        "lady's finger,vegetable,source\n",
    )
    findings = audit_lexicon.audit(directory)
    assert findings["Empty or malformed fields"] == []
    assert "lady's finger" in findings["Normalised key collisions"][0]
    assert "(line 3)" in findings["Normalised key collisions"][0]


def test_summary_and_missing_file_error(resources, tmp_path, capsys):
    directory = resources("rice,whole_food,source\n")
    assert audit_lexicon.main(["--resources", str(directory)]) == 0
    output = capsys.readouterr().out
    assert "Duplicate entries: 0" in output
    assert "Normalised key collisions: 0" in output
    assert "Empty or malformed fields: 0" in output
    assert "Inconsistent categories: 0" in output
    assert audit_lexicon.main(["--resources", str(tmp_path / "missing")]) == 1
    assert "Cannot read lexicon" in capsys.readouterr().err
