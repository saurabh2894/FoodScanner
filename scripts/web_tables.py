"""Dump the resource tables as JSON (shared by the web-preview build and the parity check)."""
import json

from foodscan.tables import load_table


def tables() -> dict:
    return {
        "ins_map": [dict(r) for r in load_table("ins_map.csv")],
        "ins_names": [dict(r) for r in load_table("ins_names.csv")],
        "synonyms": [dict(r) for r in load_table("synonyms.csv")],
        "markers": [dict(r) for r in load_table("markers.csv")],
        "lexicon": [dict(r) for r in load_table("lexicon.csv")],
        "descriptors": [dict(r) for r in load_table("descriptors.csv")],
    }


if __name__ == "__main__":
    print(json.dumps(tables()))
