"""Dump the resource tables as JSON (shared by the web-preview build and the parity check)."""
import json

from foodscan.tables import load_table


def ins_reference() -> list:
    """Empty unless the (licence-pending) table has been placed in resources/ on purpose."""
    from foodscan.tables import has_table
    return [dict(r) for r in load_table("ins_reference.csv")] if has_table("ins_reference.csv") else []


def tables() -> dict:
    return {
        "ins_map": [dict(r) for r in load_table("ins_map.csv")],
        "ins_reference": ins_reference(),
        "synonyms": [dict(r) for r in load_table("synonyms.csv")],
        "markers": [dict(r) for r in load_table("markers.csv")],
        "lexicon": [dict(r) for r in load_table("lexicon.csv")],
        "descriptors": [dict(r) for r in load_table("descriptors.csv")],
    }


if __name__ == "__main__":
    print(json.dumps(tables()))
