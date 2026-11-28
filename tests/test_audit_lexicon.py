import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_lexicon.py"
spec = importlib.util.spec_from_file_location("audit_lexicon", SCRIPT)
audit_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_module)


def head(term, kind="fruit", source="fixture"):
    return {"term": term, "kind": kind, "source": source}


def alias(source, target, citation="fixture"):
    return {"from": source, "to": target, "source": citation}


def test_collisions_candidates_duplicates_and_categories():
    heads = [head("Apple"), head("apple", "vegetable"), head("apples"),
             head("yoghurt"), head("yogurt"), head("pear"), head("pear")]
    aliases = [alias("Pear", "apple"), alias("pear", "yogurt"),
               alias("pear", "yogurt"), alias("a-b", "apple"), alias("a b", "apple")]
    report = audit_module.audit(heads, aliases, {"lexicon": heads, "synonyms": aliases})
    assert "pear: 2 rows" in report["duplicate_entries"]
    assert "alias pear -> yogurt: 2 rows" in report["duplicate_entries"]
    assert "apple: Apple, apple" in report["normalised_head_keys"]
    assert "a b: a b, a-b" in report["normalised_alias_keys"]
    assert any("multiple targets" in item and "pear" in item for item in report["alias_collisions"])
    assert any("also head: pear" in item for item in report["alias_collisions"])
    assert "apple: Apple, apple, apples" in report["near_duplicate_head_candidates"]
    assert "yogurt: yoghurt, yogurt" in report["near_duplicate_head_candidates"]
    assert "apple: fruit, vegetable" in report["inconsistent_categories"]
    assert report["counts_per_category"] == {"fruit": 6, "vegetable": 1}
    assert report["counts_per_nova_group"] is None


def test_missing_malformed_fields_and_browser_differences():
    heads = [head("apple"), {"term": "", "kind": "", "source": "", None: ["extra"]},
             head("pear", "unknown")]
    aliases = [alias("pomme", "apple"), {"from": "!!!", "to": "", "source": None}]
    browser = {"lexicon": [head("apple"), head("orange")],
               "synonyms": [alias("pomme", "pear")]}
    report = audit_module.audit(heads, aliases, browser)
    issues = "\n".join(report["missing_or_malformed_fields"])
    assert "lexicon row 3: missing or empty term" in issues
    assert "lexicon row 3: missing or empty kind" in issues
    assert "lexicon row 3: extra CSV fields" in issues
    assert "unknown kind 'unknown'" in issues
    assert "synonyms row 3: malformed from" in issues
    assert "synonyms row 3: missing or empty source" in issues
    differences = report["python_browser_differences"]
    assert "heads Python only: pear" in differences
    assert "heads browser only: orange" in differences
    assert "aliases Python only: pomme -> apple" in differences
    assert "aliases browser only: pomme -> pear" in differences


def test_failed_browser_generation_is_not_reported_as_parity():
    report = audit_module.audit([head("apple")], [], None, "missing source")
    assert report["python_browser_differences"] == [
        "Unavailable: browser table generation failed: missing source"
    ]


def csv_report(tmp_path, text):
    path = tmp_path / "lexicon.csv"
    path.write_text(text, encoding="utf-8", newline="")
    heads = audit_module.read_csv(path)
    return heads, audit_module.audit(heads, [], {"lexicon": heads, "synonyms": []})


@pytest.mark.parametrize(
    ("row", "legacy", "malformed"),
    [
        ("apple,fruit,citation,fdc_sr_legacy:123;cofid:14-249,batch-1", 1, 0),
        ("apple,fruit,citation", 0, 0),
        ("apple,fruit,citation,unexpected", 0, 1),
        ("apple,fruit,citation,fdc:123,batch-1,unexpected", 0, 1),
        ("apple,fruit,citation,unexpected,batch-1", 0, 1),
        ("apple,fruit,citation,fdc:123", 0, 1),
    ],
)
def test_legacy_provenance_and_other_column_counts(tmp_path, row, legacy, malformed):
    _, report = csv_report(tmp_path, "term,kind,source\n" + row + "\n")
    assert len(report["legacy_unheaded_provenance_columns"]) == legacy
    assert len(report["missing_or_malformed_fields"]) == malformed
    assert report["finding_counts"]["total"] == legacy + malformed
    if legacy:
        assert "apple" in report["legacy_unheaded_provenance_columns"][0]
        assert "fdc_sr_legacy:123" in report["legacy_unheaded_provenance_columns"][0]


def test_named_extra_column_is_reported(tmp_path):
    _, report = csv_report(tmp_path, "term,kind,source,unexpected\napple,fruit,citation,x\n")
    assert "unexpected" in report["missing_or_malformed_fields"][0]
    assert not report["legacy_unheaded_provenance_columns"]


def test_quoted_multiline_source_is_one_record_not_whitespace(tmp_path):
    heads, report = csv_report(
        tmp_path, 'term,kind,source\r\napple,fruit,"first line, quoted\r\nsecond line"\r\n'
        'pear,fruit,citation\r\n',
    )
    assert [row["term"] for row in heads] == ["apple", "pear"]
    assert heads[0]["source"] == "first line, quoted\r\nsecond line"
    assert report["finding_counts"]["total"] == 0


@pytest.mark.parametrize(
    ("row", "field"),
    [
        (",fruit,citation", "term"),
        ("apple,,citation", "kind"),
        ("apple,fruit,", "source"),
        (" ,fruit,citation", "term"),
        ("apple, ,citation", "kind"),
        ("apple,fruit, ", "source"),
    ],
)
def test_empty_and_whitespace_only_values_remain_findings(tmp_path, row, field):
    _, report = csv_report(tmp_path, "term,kind,source\n" + row + "\n")
    assert any(f"missing or empty {field}" in item
               for item in report["missing_or_malformed_fields"])
    if " " in row:
        assert any(f"malformed {field}" in item for item in report["whitespace_in_values"])


@pytest.mark.parametrize(("term", "kind", "source", "expected"), [
    ("apple", "fruit", "citation ", "trailing"),
    (" apple", "fruit", "citation", "leading"),
    ("apple", "fruit", "citation", None),
])
def test_whitespace_section_reports_only_value_edges(tmp_path, term, kind, source, expected):
    _, report = csv_report(tmp_path, f'term,kind,source\n"{term}",{kind},"{source}"\n')
    findings = report["whitespace_in_values"]
    assert len(findings) == (expected is not None)
    if expected:
        assert expected in findings[0]
        assert "apple" in findings[0]


def test_unknown_kind_and_duplicate_rows_remain_findings(tmp_path):
    _, report = csv_report(tmp_path, "term,kind,source\napple,unknown,citation\n"
                           "apple,unknown,citation\n")
    assert len([item for item in report["missing_or_malformed_fields"]
                if "unknown kind" in item]) == 2
    assert report["duplicate_entries"] == ["apple: 2 rows"]
    assert report["finding_counts"]["total"] == 3


def test_cli_plain_and_json_use_actual_generated_tables():
    plain = subprocess.run([sys.executable, "-B", str(SCRIPT)], cwd=ROOT,
                           check=True, capture_output=True, text=True).stdout
    result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--json"], cwd=ROOT,
                            check=True, capture_output=True, text=True).stdout
    report = json.loads(result)
    assert "Counts per category:" in plain
    assert "Near duplicate head candidates:" in plain
    assert report["counts_per_category"]["whole_food"] > 0
    assert report["python_browser_differences"] == []
