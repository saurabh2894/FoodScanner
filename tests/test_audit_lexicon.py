import importlib.util
import json
import subprocess
import sys
from pathlib import Path


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
