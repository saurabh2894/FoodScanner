"""Build src/foodscan/resources/ins_reference.csv from the Codex INS list (CXG 36-1989, 2026 revision).

Usage:
  python scripts/build_ins_reference.py path/to/CXG_036e.pdf [--out PATH]     write the table
  python scripts/build_ins_reference.py path/to/CXG_036e.pdf --verify         cross-check the numerical list against the alphabetical one
Needs `pdftotext` (poppler); no Python dependencies.

How the table is read: `pdftotext -bbox` gives every word with coordinates. The numerical list (Section 3) and the alphabetical list (Section 4), each followed by a supplementary list of
modified starches, are four-column tables
whose cell contents are vertically centred: a code sits in the middle of its name lines and its functional-class
lines (one class per line). Rows have borders, but they are not recoverable from the PDF, so rows are rebuilt from
geometry: within each column the lines are cut into consecutive blocks, one per code in reading order, and the block
sizes are chosen (dynamic programming) so that each block is centred on its code. This is display data only (names and
functional classes). It never decides a NOVA group; decisions live in ins_map.csv.
"""
from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

FOOTNOTE_HEIGHT = 8.2   # table text is 8.7-9.2 pt high on the 2026 layout; footnotes are 7.4 pt
CODE = re.compile(r"^\d{3,4}[a-z]?(?:\([ivxl]+\))*$")
SOURCE = ("Codex CXG 36-1989 Class names and the International Numbering System for food additives, 2026 revision "
          "(FAO and WHO, 2026; https://openknowledge.fao.org/handle/20.500.14283/cd8953en), licence CC BY-NC 4.0")


def read_words(pdf: Path) -> list[list[dict]]:
    xml = subprocess.run(["pdftotext", "-bbox", str(pdf), "-"], check=True, capture_output=True, text=True).stdout
    xml = re.sub(r"<!DOCTYPE[^>]*>", "", xml).replace('xmlns="http://www.w3.org/1999/xhtml"', "")
    pages = []
    for pg in ET.fromstring(xml).findall(".//page"):
        pages.append([{"t": w.text or "", "x0": float(w.get("xMin")), "x1": float(w.get("xMax")),
                       "y0": float(w.get("yMin")), "y1": float(w.get("yMax"))} for w in pg.findall("word")])
    return pages


def find_pages(pages: list[list[dict]], kind: str = "numerical") -> tuple[int, int]:
    """(first, last) 0-based page index of the numerical (Section 3) or alphabetical (Section 4) list.

    Found from the titles "List in numerical order" / "List in alphabetical order". The numerical list
    ends where the alphabetical one starts; the alphabetical list runs to the end of the document. Each includes the
    supplementary modified-starches list that follows it."""
    def heading(i, word):
        # the title is followed by "International numbering system..."; the supplementary lists are followed by "INS No."
        ws = [w["t"] for w in pages[i]]
        return any(ws[k:k + 5] == ["List", "in", word, "order", "International"] for k in range(len(ws) - 4))
    s3 = next(i for i in range(len(pages)) if heading(i, "numerical"))
    s4 = next(i for i in range(s3 + 1, len(pages)) if heading(i, "alphabetical"))
    return (s3, s4 - 1) if kind == "numerical" else (s4, len(pages) - 1)


def text_lines(ws: list[dict]) -> list[tuple[float, str]]:
    """Words of one column grouped into lines (within 2 pt vertically): [(y_mid, text)]."""
    groups: list[list[dict]] = []
    for w in sorted(ws, key=lambda w: (w["y0"], w["x0"])):
        if groups and abs(w["y0"] - groups[-1][0]["y0"]) < 2:
            groups[-1].append(w)
        else:
            groups.append([w])
    return [((g[0]["y0"] + g[0]["y1"]) / 2,
             re.sub(r"\s+", " ", " ".join(x["t"] for x in sorted(g, key=lambda x: x["x0"]))).strip()) for g in groups]


WRAP_GAP = 12.0   # lines of one column closer than this (pt) are one wrapped phrase ("Flour treatment" / "agent")


def phrases(ws: list[dict]) -> list[tuple[float, str]]:
    """Lines merged into phrases: a class or name that wraps onto a second line stays one entry. Measured on the 2026
    layout: wrapped lines sit ~9 pt apart, separate classes of one additive at least ~16 pt apart."""
    out: list[tuple[list[float], list[str]]] = []
    prev_y = None
    for y, t in text_lines(ws):
        if out and prev_y is not None and y - prev_y < WRAP_GAP:
            out[-1][0].append(y)
            out[-1][1].append(t)
        else:
            out.append(([y], [t]))
        prev_y = y
    return [(sum(ys) / len(ys), " ".join(ts)) for ys, ts in out]


def partition(anchor_y: list[float], lines: list[tuple[float, str]], pitch: float, max_block: int = 14,
              carry: bool = False) -> list[list[tuple[float, str]]]:
    """Cut `lines` into len(anchor_y) consecutive blocks so each block is centred on its anchor (dynamic programming).

    Cost of a block of k >= 1 lines = |mean y of the block - anchor y|; an empty block (a group heading with no class)
    costs one line pitch (measured from the page), so lines are only left unassigned when they truly sit nowhere near an
    anchor. With carry=True a free-floating first block is added in front: lines at the top of the page that belong to
    a table row which started on the previous page (its code is not on this page). It is returned as blocks[0]."""
    ys = ([None] if carry else []) + list(anchor_y)
    n, m = len(ys), len(lines)
    INF = float("inf")
    best = [[INF] * (m + 1) for _ in range(n + 1)]
    back = [[0] * (m + 1) for _ in range(n + 1)]
    best[0][0] = 0.0
    CARRY_PENALTY = 3.0                      # small: a line is only carried over when centring the first row needs it
    for i in range(1, n + 1):
        for p in range(m + 1):
            for k in range(0, min(max_block, p) + 1):
                prev = best[i - 1][p - k]
                if prev == INF:
                    continue
                if ys[i - 1] is None:
                    cost = 0.0 if k == 0 else CARRY_PENALTY
                elif k == 0:
                    cost = pitch
                else:
                    cost = abs(sum(l[0] for l in lines[p - k:p]) / k - ys[i - 1])
                if prev + cost < best[i][p]:
                    best[i][p], back[i][p] = prev + cost, k
    blocks, p = [], m
    for i in range(n, 0, -1):
        k = back[i][p]
        blocks.append(lines[p - k:p])
        p -= k
    return blocks[::-1]


def parse_page(words: list[dict], prev_cols):
    # The table header is the words "Name of food additive ... Functional class ... Technological purpose". On the first
    # page of a list it sits below the end of the previous section, so use the LAST such header on the page.
    toks = [w["t"].lower() for w in words]
    starts = [k for k in range(len(toks) - 3) if toks[k:k + 4] == ["name", "of", "food", "additive"]]
    cols, top = prev_cols, 0.0
    if starts:
        nm = words[starts[-1]]
        near = lambda word: next((w for w in words if w["t"].lower() == word and abs(w["y0"] - nm["y0"]) < 4), None)
        fn, tp = near("functional"), near("technological")
        if fn and tp:
            cols = (nm["x0"], fn["x0"], tp["x0"])
            top = max(w["y1"] for w in words if abs(w["y0"] - nm["y0"]) < 4)
    name_x, class_x, purp_x = (c - 4 for c in cols)
    cells = {"code": [], "name": [], "class": []}
    for w in words:
        if w["y0"] <= top - 0.5 or (w["y1"] - w["y0"]) < FOOTNOTE_HEIGHT:
            continue                                   # above the header, or footnote-sized text (7.4 pt vs 8.7-9.2 pt)
        if w["x0"] >= purp_x:
            continue                                   # technological-purpose column: not used (noisy, and display-only data)
        col = "code" if w["x0"] < name_x else "name" if w["x0"] < class_x else "class"
        cells[col].append(w)
    # one anchor per line of the code column ("160a" and "(i)" on one line are joined)
    anchors, anomalies = [], []
    for w in sorted(cells["code"], key=lambda w: (w["y0"], w["x0"])):
        if anchors and abs(w["y0"] - anchors[-1]["y0"]) < 2:
            anchors[-1]["raw"] += w["t"]
            anchors[-1]["y1"] = max(anchors[-1]["y1"], w["y1"])
        else:
            anchors.append({"raw": w["t"], "y0": w["y0"], "y1": w["y1"]})
    for a in anchors:
        a["code"] = re.sub(r"\s+", "", a["raw"]).lower()
        a["yc"] = (a["y0"] + a["y1"]) / 2
        if not CODE.match(a["code"]):
            anomalies.append(f"non-code text in the code column: {a['raw']!r}")
    real = [a for a in anchors if CODE.match(a["code"])]
    ys = [a["yc"] for a in real]
    parts = {}
    if real:
        parts["name"] = partition(ys, phrases(cells["name"]), pitch=WRAP_GAP)
        class_blocks = partition(ys, phrases(cells["class"]), pitch=WRAP_GAP, carry=True)
        carry, parts["class"] = class_blocks[0], class_blocks[1:]
    else:
        carry = []
    out = []
    for i, a in enumerate(real):
        out.append({"code": a["code"], "yc": a["yc"],
                    "name": " ".join(t for _, t in parts["name"][i]),
                    "classes": [re.sub(r"\s+", " ", re.sub(r"[-\u2013]", " ", t.lower())).strip() for _, t in parts["class"][i] if t]})
    carry_classes = [re.sub(r"\s+", " ", re.sub(r"[-\u2013]", " ", t.lower())).strip() for _, t in carry if t]
    return out, cols, anomalies, carry_classes


def build(pdf: Path, kind: str = "numerical") -> tuple[list[dict], list[str]]:
    pages = read_words(pdf)
    first, last = find_pages(pages, kind)
    raw_rows, anomalies, cols = [], [], None
    for i in range(first, last + 1):
        page_rows, cols, bad, carry_classes = parse_page(pages[i], cols)
        anomalies += [f"page {i + 1}: {b}" for b in bad]
        if carry_classes and raw_rows:                  # classes of a row that broke across the page: give them to its code
            raw_rows[-1]["classes"] += carry_classes
        for r in page_rows:
            r.update(page=i + 1)
            raw_rows.append(r)
    rows: dict[str, dict] = {}
    for r in raw_rows:                                  # an additive that continues on the next page appears twice: merge
        if r["code"] in rows:
            old = rows[r["code"]]
            old["classes"] += [c for c in r["classes"] if c not in old["classes"]]
            old["name"] = old["name"] or r["name"]
        else:
            rows[r["code"]] = dict(r, ins=r["code"])
    out = list(rows.values())
    # parent rows ("141 Chlorophylls and chlorophyllins, copper complexes") have no class of their own: take the union
    # of their sub-entries so a bare "INS 141" on a label still has a class list
    for r in out:
        r["is_group"] = not r["classes"]
        if r["is_group"]:
            kids = [k for k in out if k["code"] != r["code"] and (k["code"].startswith(r["code"] + "(") or
                    re.fullmatch(re.escape(r["code"]) + r"[a-z](\([ivxl]+\))?", k["code"]))]
            seen: list[str] = []
            for k in kids:
                seen += [c for c in k["classes"] if c not in seen]
            r["classes"] = seen
    return out, anomalies


def verify(pdf: Path) -> int:
    """Cross-check the numerical list against the alphabetical list: the same additives in a different layout, read by
    the same method. Every code must exist in both with the same set of classes; differences are listed so they can be
    judged as typos in the source or as extraction errors."""
    s3, a3 = build(pdf, "numerical")
    s4, a4 = build(pdf, "alphabetical")
    by3, by4 = {r["ins"]: r for r in s3}, {r["ins"]: r for r in s4}
    leaf3, leaf4 = {c for c, r in by3.items() if not r["is_group"]}, {c for c, r in by4.items() if not r["is_group"]}
    only3, only4 = sorted(set(by3) - set(by4)), sorted(set(by4) - set(by3))
    key = lambda c: (int(re.match(r"\d+", c).group()), c)
    diff = [(c, by3[c]["classes"], by4[c]["classes"]) for c in sorted(set(by3) & set(by4), key=key)
            if sorted(by3[c]["classes"]) != sorted(by4[c]["classes"])]
    print(f"numerical list: {len(by3)} entries ({len(leaf3)} with their own classes) | alphabetical list: {len(by4)} entries "
          f"({len(leaf4)}) | anomalies: {len(a3)} + {len(a4)}")
    print(f"codes only in the numerical list: {len(only3)} {only3[:12]}")
    print(f"codes only in the alphabetical list: {len(only4)} {only4[:12]}")
    print(f"codes whose class set differs between the two lists: {len(diff)} of {len(set(by3) & set(by4))}")
    for c, x, y in diff[:30]:
        print(f"   {c:9} numerical={x}  alphabetical={y}")
    return 0 if not (only3 or only4 or diff or a3 or a4) else 1


def write_csv(rows: list[dict], out: Path) -> None:
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["ins", "name", "functional_classes", "is_group", "reading", "source"])
        for r in rows:
            src = SOURCE + ("; listed only in the alphabetical list of the source text" if r.get("alpha_only") else "")
            w.writerow([r["ins"], r["name"], "; ".join(r["classes"]), "yes" if r["is_group"] else "", r["reading"], src])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--verify", action="store_true", help="cross-check the numerical list against the alphabetical one and exit")
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent.parent / "data/pending/ins_reference.csv")
    args = ap.parse_args()
    if args.verify:
        return verify(args.pdf)
    # Two independent readings of the same additives (numerical and alphabetical lists). An entry ships only where both
    # exist and carry the same set of classes; everything else is withheld and reported, never guessed.
    n_rows, anomalies = build(args.pdf, "numerical")
    a_rows, a_anoms = build(args.pdf, "alphabetical")
    by_a = {r["ins"]: r for r in a_rows}
    rows, withheld = [], []
    for r in n_rows:
        o = by_a.get(r["ins"])
        if not o:
            withheld.append(r["ins"]); continue
        both = sorted(set(o["classes"]) & set(r["classes"]))
        if sorted(o["classes"]) == sorted(r["classes"]) and both:
            r["reading"] = "both lists agree"; rows.append(r)
        elif both:        # the readings differ (a row's text can bleed into its neighbour): keep only what both readings show
            r["classes"] = both; r["reading"] = "partial: only the classes both readings agree on; the source may list more"; rows.append(r)
        else:
            withheld.append(r["ins"])
    withheld += sorted(set(by_a) - {r["ins"] for r in n_rows})
    rows.sort(key=lambda r: (int(re.match(r"\d+", r["ins"]).group()), r["ins"]))
    print(f"withheld (readings disagree or one list lacks the code): {len(withheld)}: {withheld}")
    for a in anomalies:
        print("ANOMALY:", a, file=sys.stderr)
    write_csv(rows, args.out)
    print(f"{len(rows)} INS entries ({sum(1 for r in rows if r['is_group'])} group headings) -> {args.out}; {len(anomalies)} anomalies")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
