/* foodscan: JavaScript port of the Python classifier (parser, normalise, classify, pipeline).
 * Python is the source of truth. scripts/parity_check.py runs both on the same texts and
 * fails on any difference. Tables come from src/foodscan/resources/*.csv (see build script). */
(function (root) {
  "use strict";

  function createEngine(T) {
    const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const collapse = (s) => s.replace(/\s+/g, " ").trim();
    const flatten = (s) => s.toLowerCase().replace(/[-–—_/]/g, " ").replace(/\s+/g, " ").trim();
    const stripChars = (s, chars) => {
      let a = 0, b = s.length;
      while (a < b && chars.includes(s[a])) a++;
      while (b > a && chars.includes(s[b - 1])) b--;
      return s.slice(a, b);
    };

    /* ---------- parser ---------- */
    const HEADING = /(?:ingredients?|सामग्री|अवयव)\s*[:\-–—]?\s*/i;
    const STOP = /\b(?:may\s+contain|contains|allergen(?:s)?(?:\s+information)?|nutrition(?:al)?|manufactured|manufacturer|mfd|marketed|packed\s+by|best\s+before|use\s+by|net\s+(?:wt|weight|qty|quantity)|storage|store\s+in|fssai|customer\s+care)\b/i;
    const OPEN = "([{", CLOSE = ")]}";

    function bracketDepth(text) {
      let depth = 0;
      for (const ch of text) {
        if (OPEN.includes(ch)) depth++;
        else if (CLOSE.includes(ch)) { if (depth === 0) return -1; depth--; }
      }
      return depth;
    }
    function findTerminator(text) {
      let depth = 0;
      for (let i = 0; i < text.length; i++) {
        const ch = text[i];
        if (OPEN.includes(ch)) depth++;
        else if (CLOSE.includes(ch)) depth = Math.max(depth - 1, 0);
        else if (ch === "." && depth === 0) {
          const prevDigit = i > 0 && /\d/.test(text[i - 1]);
          const nextDigit = i + 1 < text.length && /\d/.test(text[i + 1]);
          if (!(prevDigit && nextDigit)) return i;
        }
      }
      return null;
    }
    function splitTopLevel(text) {
      const items = []; let buf = ""; let depth = 0;
      for (const ch of text) {
        if (OPEN.includes(ch)) depth++;
        else if (CLOSE.includes(ch)) depth = depth ? Math.max(depth - 1, 0) : 0;
        if ((ch === "," || ch === ";") && depth === 0) { items.push(buf); buf = ""; }
        else buf += ch;
      }
      items.push(buf);
      return { items: items.map((i) => stripChars(i, " .")).filter((i) => i), unbalanced: bracketDepth(text) !== 0 };
    }
    function parseIngredientList(text) {
      const flat = collapse(text);
      const m = HEADING.exec(flat);
      if (!m) return { found: false };
      let body = flat.slice(m.index + m[0].length);
      let terminated = false; const declarations = [];
      const stop = STOP.exec(body);
      if (stop) {
        const tail = body.slice(stop.index);
        body = body.slice(0, stop.index);
        terminated = true;
        if (/^contains\b/i.test(tail)) {
          const e = findTerminator(tail);
          declarations.push(e !== null ? tail.slice(0, e) : tail);
        }
      }
      const end = findTerminator(body);
      if (end !== null) { body = body.slice(0, end); terminated = true; }
      const { items, unbalanced } = splitTopLevel(body);
      if (!items.length) return { found: false };
      return { found: true, items, terminated, unbalanced, declarations };
    }

    /* ---------- tables ---------- */
    const insTable = {};
    for (const r of T.ins_map) insTable[r.ins.toLowerCase().replace(/\s+/g, "")] = r;
    const synonyms = [...T.synonyms]
      .sort((a, b) => b.from.length - a.from.length)
      .map((r) => ({ re: new RegExp("(?<![a-z])" + esc(r.from.toLowerCase()) + "(?![a-z])", "g"), to: r.to.toLowerCase() }));
    const markers = T.markers.map((r) => ({ re: new RegExp("(?<![a-z])" + esc(flatten(r.term)) + "(?![a-z])"), row: r }));
    const lexicon = {};
    for (const r of T.lexicon) lexicon[flatten(r.term)] = r;
    const isRecognised = (name) => Object.prototype.hasOwnProperty.call(lexicon, name);

    /* ---------- normalise ---------- */
    const CODE = "\\d{3,4}(?:\\s*\\(\\s*[ivx]+\\s*\\))?(?:[a-z](?![a-z]))?";
    const INS_RE = new RegExp("(?<![a-z0-9])(?:ins|e)\\s*[-:.]?\\s*(?<codes>" + CODE + "(?:\\s*(?:,|and|&|/)\\s*" + CODE + ")*)", "g");
    const CODE_RE = new RegExp(CODE, "g");
    const canonicalCode = (c) => c.toLowerCase().replace(/\s+/g, "");

    function extractIns(text) {
      const uses = [];
      let stripped = text.toLowerCase().replace(INS_RE, (...a) => {
        const groups = a[a.length - 1];
        for (const c of groups.codes.match(CODE_RE) || []) {
          const code = canonicalCode(c);
          const row = insTable[code];
          uses.push({ code, name: row ? row.name : null, source: row ? row.source : null });
        }
        return " ";
      });
      for (let i = 0; i < 3; i++) stripped = stripped.replace(/[(\[{]\s*[,;/&]*\s*[)\]}]/g, " ");
      return { stripped, uses };
    }
    function splitBrackets(text) {
      let outside = "", inside = "", depth = 0;
      for (const ch of text) {
        if (OPEN.includes(ch)) { depth++; inside += " "; }
        else if (CLOSE.includes(ch)) { depth = Math.max(depth - 1, 0); inside += " "; }
        else if (depth) inside += ch;
        else outside += ch;
      }
      const clean = (s) => stripChars(s.replace(/\s+/g, " ").trim(), " ,;.:");
      return [clean(outside), clean(inside)];
    }
    function normaliseIngredient(raw) {
      let { stripped: text, uses } = extractIns(raw);
      text = text.replace(/\d+(?:\.\d+)?\s*%/g, " ");
      for (const s of synonyms) text = text.replace(s.re, s.to);
      text = flatten(text);
      const [name, inner] = splitBrackets(text);
      return { raw, name, inner, ins: uses, text: (name + " " + inner).trim() };
    }

    /* ---------- classify ---------- */
    function hitsFor(ing) {
      let hits = [];
      for (const { re, row } of markers) {
        if (re.test(ing.text)) hits.push({ strength: row.strength, marker_class: row.marker_class, detail: `"${row.term}" (${row.marker_class})`, source: row.source });
      }
      for (const use of ing.ins) {
        const row = insTable[use.code];
        if (!row) hits.push({ strength: "unlisted", marker_class: "unlisted_additive", detail: `INS ${use.code} (not in local mapping)`, source: "no source: code absent from ins_map.csv" });
        else hits.push({ strength: row.strength, marker_class: "ins", detail: `INS ${use.code} (${row.name})`, source: row.source });
      }
      if (hits.some((h) => h.strength === "weak_specific"))
        hits = hits.filter((h) => !(h.strength === "strong" && h.marker_class === "cosmetic_additive"));
      return hits;
    }
    function classifyIngredients(ings, declarations) {
      const strong = [], weak = [];
      for (const ing of ings) for (const h of hitsFor(ing)) (h.strength === "strong" ? strong : weak).push({ ingredient: ing.raw, detail: h.detail, source: h.source });
      for (const decl of declarations || []) {
        const text = flatten(decl);
        for (const { re, row } of markers)
          if (row.strength === "strong" && row.marker_class === "cosmetic_additive" && re.test(text))
            strong.push({ ingredient: decl, detail: `declared in "Contains" statement: "${row.term}"`, source: row.source });
      }
      if (strong.length) return { group: 4, drivers: strong, reason: null };
      if (weak.length) {
        const names = [...new Set(weak.map((d) => `${d.ingredient} -> ${d.detail}`))].sort().join("; ");
        return { group: null, drivers: weak, reason: `only weak or unlisted markers present (${names}); not enough to call a group` };
      }
      const unrecognised = ings.filter((i) => !isRecognised(i.name)).map((i) => i.raw);
      if (unrecognised.length) return { group: null, drivers: [], reason: "ingredients not in the local vocabulary, so processing level cannot be judged: " + unrecognised.join(", ") };
      const kinds = ings.map((i) => lexicon[i.name].kind);
      const substantive = ings.map((i, n) => [i, kinds[n]]).filter(([, k]) => k !== "neutral");
      if (ings.length === 1 && (kinds[0] === "whole_food" || kinds[0] === "flour"))
        return { group: 1, drivers: [{ ingredient: ings[0].raw, detail: "single recognised unprocessed food", source: lexicon[ings[0].name].source }], reason: null };
      if (ings.length === 1 && kinds[0] === "culinary")
        return { group: 2, drivers: [{ ingredient: ings[0].raw, detail: "single processed culinary ingredient", source: lexicon[ings[0].name].source }], reason: null };
      if (kinds.includes("flour")) return { group: null, drivers: [], reason: "flour-based list: bakery-fresh versus industrial formulation cannot be told from the ingredient list" };
      const hasFood = substantive.some(([, k]) => k === "whole_food");
      const hasCulinary = substantive.some(([, k]) => k === "culinary");
      if (hasFood && hasCulinary)
        return { group: 3, drivers: substantive.map(([i, k]) => ({ ingredient: i.raw, detail: "recognised " + k.replace(/_/g, " "), source: lexicon[i.name].source })), reason: null };
      return { group: null, drivers: [], reason: "recognised ingredients, but the combination does not match a group 1, 2 or 3 pattern" };
    }

    /* ---------- pipeline ---------- */
    const NOT_ENOUGH = "Not enough information";
    const GROUP_NAMES = { 1: "unprocessed or minimally processed foods", 2: "processed culinary ingredients", 3: "processed foods", 4: "ultra-processed foods" };
    const MIN_CHARS = 20, MIN_ALPHA_RATIO = 0.5;

    function abstain(reason, text, extra) {
      return Object.assign({ answered: false, group: null, reason, ingredients: [], drivers: [], ins: [], text }, extra || {}, { headline: `${NOT_ENOUGH}: ${reason}` });
    }
    function analyseText(text) {
      const compact = text.replace(/\s+/g, "");
      const chars = [...compact];
      if (chars.length < MIN_CHARS) return abstain("OCR produced little text", text);
      if (chars.filter((c) => /\p{L}/u.test(c)).length / chars.length < MIN_ALPHA_RATIO)
        return abstain("extracted text looks like noise, not a readable label", text);
      const parsed = parseIngredientList(text);
      if (!parsed.found) return abstain("no ingredient list found in the text", text);
      const ings = parsed.items.map(normaliseIngredient);
      const common = { ingredients: parsed.items, ins: ings.flatMap((i) => i.ins) };
      if (parsed.unbalanced) return abstain("ingredient list looks truncated (unclosed bracket)", text, common);
      const last = ings[ings.length - 1];
      const recognisable = isRecognised(last.name) || last.ins.length > 0 || hitsFor(last).length > 0;
      if (!parsed.terminated && !recognisable)
        return abstain(`ingredient list looks truncated (ends mid-word or unrecognised: "${parsed.items[parsed.items.length - 1]}")`, text, common);
      const r = classifyIngredients(ings, parsed.declarations);
      if (r.group === null) return abstain(r.reason || "classification uncertain", text, Object.assign({ drivers: r.drivers }, common));
      return Object.assign({ answered: true, group: r.group, reason: null, drivers: r.drivers, text, headline: `NOVA group ${r.group}: ${GROUP_NAMES[r.group]}` }, common);
    }
    return { analyseText, NOT_ENOUGH, GROUP_NAMES };
  }

  root.FoodScan = { createEngine };
  if (typeof module !== "undefined" && module.exports) module.exports = root.FoodScan;
})(typeof window !== "undefined" ? window : globalThis);
