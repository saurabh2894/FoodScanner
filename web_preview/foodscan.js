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
    // Mirrors src/foodscan/parser.py. A full stop does not end the list by itself: a following
    // "Label:" section continues it (unless the label names non-ingredient text), and a line break
    // before a "Label:" starts a new section. See the module docstring there.
    const HEADING = /(?:ingredients?|सामग्री|अवयव)\s*[:\-–—]?\s*/i;
    const STOP = /\b(?:may\s+contain|contains|allergen(?:s)?(?:\s+information)?|nutrition(?:al)?|manufactured|manufacturer|mfd|marketed|packed\s+by|best\s+before|use\s+by|net\s+(?:wt|weight|qty|quantity)|storage|store\s+in|fssai|customer\s+care)\b/i;
    const OPEN = "([{", CLOSE = ")]}";
    const LEAD_IN = /(?:^|[.\n])\s*((?:this\s+|the\s+|our\s+)?product|allerg(?:en|y)\s+advice|[A-Za-z][A-Za-z &'\u2019\/\-]{0,40}:)\s*$/id;
    const LABEL = /^\s*([A-Za-z][A-Za-z&'’\/\-]*(?: [A-Za-z&'’\/\-]+){0,3})(?:\s+(\d+(?:\.\d+)?\s*%))?\s*:\s*(?=\S)/;
    const DENY = /^(?:notes?|directions?|instructions?|cooking instructions|preparation|how to \w+(?: \w+)?|serving suggestions?|warning|caution|tips?|usage|mrp|price|address|batch(?: no)?)$/i;

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
    const normaliseWs = (text) => text.replace(/\r\n?/g, "\n").split("\n")
      .map((ln) => ln.replace(/[ \t ]+/g, " ").trim()).join("\n").replace(/\n{2,}/g, "\n").trim();

    function labelInfo(seg) {
      const m = LABEL.exec(seg);
      if (!m) return null;
      const label = m[1].trim();
      if (DENY.test(label)) return null;
      if (!/^\p{L}/u.test(seg.slice(m[0].length))) return null;
      const flat = flatten(label);
      if (isRecognised(flat)) return null;
      const shown = label + (m[2] ? " " + m[2].replace(/\s+/g, "") : "");   // "Seasoning 12%"
      return { label: shown, off: m[0].length, strip: !CLASS_WORD_RE.test(flat) };
    }
    const MARKER_TERMS = new Set(T.markers.map((r) => flatten(r.term)));
    const knownPhrase = (flat) => isRecognised(flat) || MARKER_TERMS.has(flat);
    function colonAtDepth0(item) {
      let depth = 0;
      for (let i = 0; i < item.length; i++) {
        const ch = item[i];
        if (OPEN.includes(ch)) depth++;
        else if (CLOSE.includes(ch)) depth = Math.max(depth - 1, 0);
        else if (ch === ":" && depth === 0) return i;
      }
      return -1;
    }
    // "Rice Bran Oil Seasoning : Onion" -> [prefix, label, rest]; mirrors parser._peel_label
    function peelLabel(item) {
      const colon = colonAtDepth0(item);
      if (colon <= 0) return null;
      let left = item.slice(0, colon);
      const rest = item.slice(colon + 1).trim();
      if (!/^\p{L}/u.test(rest)) return null;
      let pct = "";
      const mp = /\s+(\d+(?:\.\d+)?\s*%)\s*$/.exec(left);
      if (mp) { pct = mp[1].replace(/\s+/g, ""); left = left.slice(0, mp.index); }
      const words = left.split(/\s+/).filter(Boolean);
      for (let k = words.length - 1; k > 0; k--) {
        const labelWords = words.slice(k);
        if (labelWords.length > 4 || !labelWords.every((w) => /^[A-Za-z&'\u2019\/\-]+$/.test(w))) continue;
        const label = labelWords.join(" "), flat = flatten(label);
        if (DENY.test(label) || isRecognised(flat) || CLASS_WORD_RE.test(flat)) continue;
        const prefix = words.slice(0, k).join(" ");
        if (knownPhrase(flatten(prefix))) return [prefix, label + (pct ? " " + pct : ""), rest];
      }
      return null;
    }
    function suspectSectionItems(items) {
      return items.filter((it) => { const c = colonAtDepth0(it); return c > 0 && !CLASS_WORD_RE.test(flatten(it.slice(0, c))); });
    }
    function nextBoundary(body, start) {
      let depth = 0;
      for (let i = start; i < body.length; i++) {
        const ch = body[i];
        if (OPEN.includes(ch)) depth++;
        else if (CLOSE.includes(ch)) depth = Math.max(depth - 1, 0);
        else if (depth === 0) {
          if (ch === ".") {
            const prevDigit = i > 0 && /\d/.test(body[i - 1]);
            const nextDigit = i + 1 < body.length && /\d/.test(body[i + 1]);
            if (!(prevDigit && nextDigit)) return [i, "stop"];
          } else if (ch === "\n" && labelInfo(body.slice(i + 1)) !== null) return [i, "break"];
        }
      }
      if (depth > 0) {
        // unclosed bracket on the pack: fall back to the first full stop right after a closing bracket
        const m = /[)\]}]\.(?=\s|$)/.exec(body.slice(start));
        if (m) return [start + m.index + m[0].length - 1, "stop"];
      }
      return [body.length, "end"];
    }
    function readSections(body) {
      const sections = []; let pos = 0, ended = false, unread = "";
      for (;;) {
        const info = labelInfo(body.slice(pos));
        let label = null, segStart = pos;
        if (info && info.strip) { label = info.label; segStart = pos + info.off; }
        const [end, kind] = nextBoundary(body, segStart);
        sections.push([label, body.slice(segStart, end)]);
        if (kind === "end") break;
        if (kind === "break") { pos = end + 1; continue; }
        const rest = body.slice(end + 1);
        if (!rest.trim() || labelInfo(rest) === null) { ended = true; unread = rest.trim(); break; }   // kept, not dropped
        pos = end + 1;
      }
      return { sections, ended, unread };
    }
    function parseIngredientList(text, opts) {
      const assumeList = !!(opts && opts.assumeList);
      const norm = normaliseWs(text);
      const m = HEADING.exec(norm);
      let body;
      if (m) body = norm.slice(m.index + m[0].length);
      else if (assumeList) body = norm;
      else return { found: false };
      let terminated = false; const declarations = [];
      const stop = STOP.exec(body);
      if (stop) {
        const tail = collapse(body.slice(stop.index));
        // the stop phrase takes its lead-in with it: a label right before it, or a claim opener (see parser.py)
        const lead = LEAD_IN.exec(body.slice(0, stop.index));
        body = body.slice(0, lead ? lead.indices[1][0] : stop.index);
        terminated = true;
        if (/^contains\b/i.test(tail)) {
          const e = findTerminator(tail);
          declarations.push(e !== null ? tail.slice(0, e) : tail);
        }
      }
      const read = readSections(body);
      terminated = terminated || read.ended;
      const sections = [], items = []; let unbalanced = false;
      for (const [label, content] of read.sections) {
        const r = splitTopLevel(collapse(content));
        unbalanced = unbalanced || r.unbalanced;
        let curLabel = label, cur = [];
        for (const it of r.items) {
          const peeled = peelLabel(it);
          if (peeled) {                       // "Rice Bran Oil Seasoning : Onion": a new section starts mid-line
            cur.push(peeled[0]);
            sections.push({ label: curLabel, items: cur }); items.push(...cur);
            curLabel = peeled[1]; cur = [peeled[2]];
          } else cur.push(it);
        }
        if (cur.length) { sections.push({ label: curLabel, items: cur }); items.push(...cur); }
      }
      if (!items.length) return { found: false };
      return { found: true, items, terminated, unbalanced, declarations, sections, ignored: read.unread ? [collapse(read.unread)] : [] };
    }

    function* bracketGroups(raw) {
      let i = 0;
      while (i < raw.length) {
        if (OPEN.includes(raw[i])) {
          let depth = 0, end = raw.length;
          for (let j = i; j < raw.length; j++) {
            if (OPEN.includes(raw[j])) depth++;
            else if (CLOSE.includes(raw[j])) { depth--; if (depth === 0) { end = j; break; } }
          }
          yield [i, end, raw.slice(i + 1, end)];
          i = end + 1;
        } else i++;
      }
    }
    function splitCompound(raw) {
      for (const [idx, , content] of bracketGroups(raw)) {
        if (!/[A-Za-z]/.test(content)) continue;
        if (idx <= 0) return null;
        const subs = splitTopLevel(content).items;
        if (subs.length < 2) return null;
        return [stripChars(raw.slice(0, idx), " *"), subs];
      }
      return null;
    }

    /* ---------- tables ---------- */
    const insTable = {};
    for (const r of T.ins_map) insTable[r.ins.toLowerCase().replace(/\s+/g, "")] = r;
    const synonyms = [...T.synonyms]
      .sort((a, b) => b.from.length - a.from.length)
      .map((r) => {
        const term = r.from.toLowerCase();   // a term starting or ending with a digit must not match inside a longer alphanumeric run
        const left = /^\d/.test(term) ? "(?<![a-z0-9])" : "(?<![a-z])", right = /\d$/.test(term) ? "(?![a-z0-9])" : "(?![a-z])";
        return { re: new RegExp(left + esc(term) + right, "g"), to: r.to.toLowerCase() };
      });
    const markers = T.markers.map((r) => ({ re: new RegExp("(?<![a-z])" + esc(flatten(r.term)) + "(?![a-z])"), row: r }));
    const lexicon = {};
    for (const r of T.lexicon) lexicon[flatten(r.term)] = r;
    const isRecognised = (name) => Object.prototype.hasOwnProperty.call(lexicon, name);

    /* ---------- normalise ---------- */
    const CODE = "\\d{3,4}(?:\\s*\\(\\s*[ivx]+\\s*\\))?(?:[a-z](?![a-z]))?";
    const INS_RE = new RegExp("(?<![a-z0-9])(?:ins|e)\\s*[-:.]?\\s*(?<codes>" + CODE + "(?:\\s*(?:,|and|&|/)\\s*" + CODE + ")*)", "g");
    const CODE_RE = new RegExp(CODE, "g");
    const canonicalCode = (c) => c.toLowerCase().replace(/\s+/g, "");

    const ADDITIVE_CLASSES = new Set(["cosmetic_additive", "ordinary_additive", "unlisted_additive"]);
    const bareTerms = [...new Set(T.markers.filter((r) => ADDITIVE_CLASSES.has(r.marker_class)).map((r) => r.term.toLowerCase()))]
      .sort((a, b) => b.length - a.length).map(esc).join("|");
    const CLASS_WORD_RE = new RegExp("(?<![a-z])(?:" + bareTerms + ")(?:s|ing|ings)?(?![a-z])");
    // "Flavour Enhancers (627, 631)": bare codes, only right after an additive class word
    const BARE_RE = new RegExp("(?<![a-z])(?:" + bareTerms + ")(?:s|ing|ings)?\\s*\\(\\s*(?<codes>" + CODE + "(?:\\s*(?:,|and|&|/)\\s*" + CODE + ")*)\\s*\\)", "g");

    function extractIns(text) {
      const uses = [];
      const addUse = (c) => {
        const code = canonicalCode(c);
        const row = insTable[code];
        uses.push({ code, name: row ? row.name : null, source: row ? row.source : null });
      };
      const low = text.toLowerCase().replace(BARE_RE, (...a) => {
        const m = a[0], groups = a[a.length - 1];
        for (const c of groups.codes.match(CODE_RE) || []) addUse(c);
        return m.slice(0, m.indexOf(groups.codes)).replace(/[( \t]+$/, "") + " ";
      });
      let stripped = low.replace(INS_RE, (...a) => {
        const groups = a[a.length - 1];
        for (const c of groups.codes.match(CODE_RE) || []) addUse(c);
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
      for (const ing of ings) for (const h of hitsFor(ing)) (h.strength === "strong" ? strong : weak).push({ ingredient: ing.raw, detail: h.detail, source: h.source, section: ing.section ?? null });
      for (const decl of declarations || []) {
        const text = normaliseIngredient(decl).text;
        for (const { re, row } of markers)
          if (row.strength === "strong" && row.marker_class === "cosmetic_additive" && re.test(text))
            strong.push({ ingredient: decl, detail: `declared in "Contains" statement: "${row.term}"`, source: row.source, section: null });
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
        return { group: 1, drivers: [{ ingredient: ings[0].raw, detail: "single recognised unprocessed food", source: lexicon[ings[0].name].source, section: ings[0].section ?? null }], reason: null };
      if (ings.length === 1 && kinds[0] === "culinary")
        return { group: 2, drivers: [{ ingredient: ings[0].raw, detail: "single processed culinary ingredient", source: lexicon[ings[0].name].source, section: ings[0].section ?? null }], reason: null };
      if (kinds.includes("flour")) return { group: null, drivers: [], reason: "flour-based list: bakery-fresh versus industrial formulation cannot be told from the ingredient list" };
      const hasFood = substantive.some(([, k]) => k === "whole_food");
      const hasCulinary = substantive.some(([, k]) => k === "culinary");
      if (hasFood && hasCulinary)
        return { group: 3, drivers: substantive.map(([i, k]) => ({ ingredient: i.raw, detail: "recognised " + k.replace(/_/g, " "), source: lexicon[i.name].source, section: i.section ?? null })), reason: null };
      return { group: null, drivers: [], reason: "recognised ingredients, but the combination does not match a group 1, 2 or 3 pattern" };
    }

    /* ---------- pipeline ---------- */
    const NOT_ENOUGH = "Not enough information";
    const GROUP_NAMES = { 1: "unprocessed or minimally processed foods", 2: "processed culinary ingredients", 3: "processed foods", 4: "ultra-processed foods" };
    const MIN_CHARS = 20, MIN_ALPHA_RATIO = 0.5;

    function abstain(reason, text, extra) {
      return Object.assign({ answered: false, group: null, reason, ingredients: [], drivers: [], ins: [], warnings: [], sections: [], unassessed: [], ignored: [], text }, extra || {}, { headline: `${NOT_ENOUGH}: ${reason}` });
    }
    const recognisableIng = (ing) => isRecognised(ing.name) || ing.ins.length > 0 || hitsFor(ing).length > 0;
    function expand(items, depth, heads) {   // items: [raw, section label] pairs
      const out = [];
      for (const [raw, section] of items) {
        const ing = normaliseIngredient(raw);
        ing.section = section;
        const split = depth < 3 ? splitCompound(raw) : null;
        if (split && !recognisableIng(normaliseIngredient(split[0]))) {
          if (heads) heads.push(split[0]);       // the group name itself is not classified: keep it visible
          out.push(...expand(split[1].map((sub) => [sub, section]), depth + 1, heads));
        }
        else out.push(ing);
      }
      return out;
    }
    const shortText = (t, limit = 100) => (t.length <= limit ? t : t.slice(0, limit - 3) + "...");
    const startsWithDeniedLabel = (seg) => { const m = LABEL.exec(seg); return !!m && DENY.test(m[1].trim()); };
    // unread text after a full stop that could be the rest of the list (mirrors pipeline._looks_like_more_ingredients)
    function looksLikeMoreIngredients(seg) {
      if (/^\s*[*\u2020#]/.test(seg) || startsWithDeniedLabel(seg)) return false;
      const parts = splitTopLevel(collapse(seg)).items;
      return parts.length >= 2 || parts.some((part) => recognisableIng(normaliseIngredient(part)));
    }
    const NO_TEXT = "No text to analyse", NO_INGREDIENTS = "No ingredients found in this text";
    // source "ocr" (default, photo path): short/noisy text is blamed on OCR and the heading is required.
    // source "text" (typed or pasted): no length gate, a heading-less text is the list, messages are about the text.
    function analyseText(text, opts) {
      const source = (opts && opts.source) || "ocr";
      if (source !== "ocr" && source !== "text") throw new Error("source must be 'ocr' or 'text'");
      const compact = text.replace(/\s+/g, "");
      const chars = [...compact];
      const alphaShare = () => chars.filter((c) => /\p{L}/u.test(c)).length / chars.length;
      let parsed;
      if (source === "text") {
        if (!chars.length) return abstain(NO_TEXT, text);
        if (alphaShare() < MIN_ALPHA_RATIO) return abstain(NO_INGREDIENTS, text);
        parsed = parseIngredientList(text, { assumeList: true });
        if (!parsed.found) return abstain(NO_INGREDIENTS, text);
      } else {
        if (chars.length < MIN_CHARS) return abstain("OCR produced little text", text);
        if (alphaShare() < MIN_ALPHA_RATIO) return abstain("extracted text looks like noise, not a readable label", text);
        parsed = parseIngredientList(text);
        if (!parsed.found) return abstain("no ingredient list found in the text", text);
      }
      const heads = [];
      const ings = expand(parsed.sections.flatMap((sec) => sec.items.map((raw) => [raw, sec.label])), 0, heads);
      const unassessed = [...new Set([
        ...ings.filter((i) => !recognisableIng(i)).map((i) => i.raw),
        ...heads.map((h) => `${h} (group name; its contents were assessed separately)`)])];
      const sectionWarnings = suspectSectionItems(parsed.items).map((it) => `"${it}" contains a colon, so a section label may not have been split from the ingredient before it`);
      const unreadLike = parsed.ignored.filter(looksLikeMoreIngredients);
      sectionWarnings.push(...unreadLike.map((seg) => `Text after a full stop was not read as ingredients but looks like more of the list: "${shortText(seg)}"`));
      const common = { ingredients: parsed.items, ins: ings.flatMap((i) => i.ins), warnings: [...sectionWarnings], unassessed, ignored: [...parsed.ignored], sections: parsed.sections.map((sec) => [sec.label, sec.items]) };
      let truncation = null;
      if (parsed.unbalanced) truncation = "ingredient list looks truncated (unclosed bracket)";
      else if (!parsed.terminated && !recognisableIng(ings[ings.length - 1]))
        truncation = `ingredient list looks truncated (ends mid-word or unrecognised: "${parsed.items[parsed.items.length - 1]}")`;
      // unlabelled text after a full stop that looks like more of the list: like truncation, only a strong-marker Group 4 stands
      const unread = unreadLike.length ? `text after a full stop looks like more ingredients and was not read: "${shortText(unreadLike[0])}"` : null;
      const blocking = truncation || unread;
      const r = classifyIngredients(ings, parsed.declarations);
      // Option A (user decision): a strong-marker Group 4 call stands on a possibly incomplete list, with a warning.
      if (blocking && r.group !== 4) return abstain(blocking, text, Object.assign({ drivers: r.drivers }, common));
      if (r.group === null) return abstain(r.reason || "classification uncertain", text, Object.assign({ drivers: r.drivers }, common));
      const warnings = [...sectionWarnings];
      if (truncation) warnings.push("List may be incomplete (" + stripChars(truncation.replace(/^ingredient list looks truncated /, ""), "()") + "). Group 4 stands because the markers found are already enough.");
      return Object.assign({}, common, { answered: true, group: r.group, reason: null, drivers: r.drivers, warnings, text, headline: `NOVA group ${r.group}: ${GROUP_NAMES[r.group]}` });
    }
    return { analyseText, NOT_ENOUGH, GROUP_NAMES };
  }

  root.FoodScan = { createEngine };
  if (typeof module !== "undefined" && module.exports) module.exports = root.FoodScan;
})(typeof window !== "undefined" ? window : globalThis);
