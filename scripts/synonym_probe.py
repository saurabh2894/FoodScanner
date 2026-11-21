"""Dump, for each term in a file (one per line), the normalised name and whether it is recognised, in the build on PYTHONPATH. One process = one build. Read-only."""
from __future__ import annotations

import json
import sys


def main(argv=None) -> int:
    import foodscan
    from foodscan.classify import is_recognised
    from foodscan.normalise import normalise_ingredient
    sys.stderr.write(f"foodscan from {foodscan.__file__}\n")
    terms = [ln.strip() for ln in open(argv[0], encoding="utf-8") if ln.strip()]
    out = {}
    for t in terms:
        name = normalise_ingredient(t).name
        out[t] = {"name": name, "recognised": bool(is_recognised(name))}
    json.dump(out, open(argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
