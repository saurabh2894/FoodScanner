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
    const HEADING = /(?:ingredient[s5]?|सामग्री|अवयव)\s*[:\-–—]?\s*/i;
    const HEADING_WORDS = ["ingredients", "ingredient"];
    const OCR_DIGITS = { "5": "s", "1": "i", "0": "o", "3": "e" };       // digits OCR often puts where letters are
    function lev(a, b) {
      let prev = Array.from({ length: b.length + 1 }, (_, j) => j);
      for (let i = 1; i <= a.length; i++) {
        const cur = [i];
        for (let j = 1; j <= b.length; j++) cur.push(Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] !== b[j - 1] ? 1 : 0)));
        prev = cur;
      }
      return prev[prev.length - 1];
    }
    // a damaged "INGREDIENTS": cropped at an edge ("REDIENTS", "INGREDIEN") or off by up to two OCR letters
    function headingLike(tok) {
      const t = tok.toLowerCase().replace(/[5103]/g, (d) => OCR_DIGITS[d]);
      if (t.length < 6) return false;
      if (HEADING_WORDS.some((w) => w.endsWith(t) || w.startsWith(t))) return true;
      return t.length >= 8 && HEADING_WORDS.some((w) => lev(t, w) <= 2);
    }
    // {end, kind, text}: "exact", or "fuzzy" for a damaged heading, which must start a line or be followed by a colon/dash
    // The word must sit in heading position and form (start of text, line or sentence, or followed by a colon or dash).
    function headingPositionOk(norm, m) {
      const before = norm.slice(0, m.index);
      if (/(?:^|[\s(])(?:active|inactive|cooking)\s*$/i.test(before)) return false;
      const atStart = /(?:^|\n)[\s*\u2022|\-]*$/.test(before) || /[.!?]\s*$/.test(before);
      return atStart || /[:\-\u2013\u2014]/.test(m[0]);
    }
    function findHeading(norm) {
      const hre = new RegExp(HEADING.source, "gi"); let m;
      while ((m = hre.exec(norm))) {
        if (headingPositionOk(norm, m)) return { end: m.index + m[0].length, kind: "exact", text: stripChars(m[0], " :-–—") };
        if (m[0].length === 0) hre.lastIndex++;
      }
      const re = /[A-Za-z0-9]{6,}/g; let t;
      while ((t = re.exec(norm))) {
        if (!headingLike(t[0]) || HEADING_WORDS.includes(t[0].toLowerCase())) continue;     // the exact word was already judged by its position
        const before = norm.slice(0, t.index), after = norm.slice(t.index + t[0].length);
        if (/^\s*[:\-–—]/.test(after) || /(?:^|\n)[\s*•\-]*$/.test(before)) {
          return { end: t.index + t[0].length + /^\s*[:\-–—]?\s*/.exec(after)[0].length, kind: "fuzzy", text: t[0] };
        }
      }
      return null;
    }
    const STOP = /\b(?:may\s+contain|(?:does|do)\s+not\s+contain|contains|allergen(?:s)?(?:\s+information)?|nutrition(?:al)?|manufactured|manufacturer|mfd|marketed|packed\s+by|best\s+before|use\s+by|net\s+(?:wt|weight|qty|quantity)|storage|store\s+in|fssai|customer\s+care)\b/i;
    const OPEN = "([{", CLOSE = ")]}";
    const LEAD_IN = /(?:^|[.\n])\s*((?:this\s+|the\s+|our\s+)?product|allerg(?:en|y)\s+advice|[A-Za-z][A-Za-z &'\u2019\/\-]{0,40}:)\s*$/id;
    const LABEL = /^\s*([A-Za-z][A-Za-z&'’\/\-]*(?: [A-Za-z&'’\/\-]+){0,3})(\s*\([A-Za-z][A-Za-z ]{0,18}\))?(?:\s+(\d+(?:\.\d+)?\s*%)|\s*\(\s*(\d+(?:\.\d+)?\s*%)\s*\))?\s*:\s*(?=\S)/;
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
    const CODE_ITEM = /^(?:(?:ins|e)\s*[-:.]?\s*)?\d{3,4}[a-z]?(?:\([ivxl]+\))*$/i;
    const PCT_GROUP = /\(\s*\d+(?:\.\d+)?\s*%\s*\)\s*[\[{(].*[A-Za-z].*[\]})]\s*$/;
    // Plain split on commas/semicolons outside brackets, plus two general rules (see parser.py _split_top_level).
    function splitTopLevel(text) {
      let pieces = [], seps = [], buf = "", depth = 0;
      for (const ch of text) {
        if (OPEN.includes(ch)) depth++;
        else if (CLOSE.includes(ch)) depth = depth ? Math.max(depth - 1, 0) : 0;
        if ((ch === "," || ch === ";") && depth === 0) { pieces.push(buf); seps.push(ch); buf = ""; }
        else buf += ch;
      }
      pieces.push(buf);
      if (seps.includes(";")) {
        const chunks = []; let cur = [pieces[0]];
        seps.forEach((sep, k) => { if (sep === ";") { chunks.push(cur); cur = [pieces[k + 1]]; } else cur.push(pieces[k + 1]); });
        chunks.push(cur);
        pieces = [];
        for (const chunk of chunks) {
          const head = chunk.slice(0, -1);
          if (chunk.length >= 2 && PCT_GROUP.test(chunk[chunk.length - 1]) && head.every((p) => !/[(\[{]/.test(p)) && head.reduce((n, p) => n + p.split(/\s+/).filter(Boolean).length, 0) <= 6) pieces.push(chunk.join(","));
          else pieces.push(...chunk);
        }
      }
      const items = [];
      for (let p of pieces) {
        p = stripChars(p, " .");
        if (!p) continue;
        if (items.length && CODE_ITEM.test(p)) items[items.length - 1] += ", " + p;
        else items.push(p);
      }
      return { items, unbalanced: bracketDepth(text) !== 0 };
    }
    function suspectAdjacentClassItems(items) {
      const out=[];
      for (const item of items) {
        let depth=0;
        for (let n=0;n<item.length;n++) {
          const c=item[n];
          if ("([{".includes(c)) depth++;
          else if (")]}".includes(c)) {
            depth=Math.max(0,depth-1);
            if (depth || CLASS_WORD_RE.test(flatten(item.slice(0,n+1)).replace(/stabiliz/g,"stabilis").replace(/emulsifying/g,"emulsifier").replace(/thickening/g,"thickener"))) continue;
            const m=/^\s+([a-z ]+?)\s*\(/i.exec(item.slice(n+1));
            if (m) {const f=flatten(m[1]), hit=CLASS_WORD_RE.exec(f);if(hit && hit.index===0 && hit[0].length===f.length){out.push(item);break;}}
          }
        }
      }
      return out;
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
      const shown = label + (m[2] ? " " + m[2].trim() : "") + ((m[3] || m[4]) ? " " + (m[3] || m[4]).replace(/\s+/g, "") : "");   // "Sprinkler Mix (Topping)", "Seasoning 12%", "Noodles (88.5%):"
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
    // a candidate label that holds a descriptor or form word is an ingredient name, never a section label; mirrors parser._label_has_form_word
    const FORM_WORDS_EXTRA = new Set(["flake", "flakes", "extract", "extracts", "paste", "pastes", "mix", "mixes", "blend", "blends", "syrup", "cooked", "canned", "pickled", "prepared"]);
    const labelHasFormWord = (label) => (label.toLowerCase().match(/[a-z]+/g) || []).some((t) => allDescriptorWords.has(t) || FORM_WORDS_EXTRA.has(t));
    // "Rice Bran Oil Seasoning : Onion" -> [prefix, label, rest]; mirrors parser._peel_label
    function peelLabel(item) {
      const colon = colonAtDepth0(item);
      if (colon <= 0) return null;
      let left = item.slice(0, colon);
      const rest = item.slice(colon + 1).trim();
      if (!/^\p{L}/u.test(rest)) return null;
      let pct = "";
      const mp = /\s+(\d+(?:\.\d+)?\s*%)\s*$/.exec(left) || /\s*\(\s*(\d+(?:\.\d+)?\s*%)\s*\)\s*$/.exec(left);
      if (mp) { pct = mp[1].replace(/\s+/g, ""); left = left.slice(0, mp.index); }
      const words = left.split(/\s+/).filter(Boolean);
      for (let k = words.length - 1; k > 0; k--) {
        const labelWords = words.slice(k);
        if (labelWords.length > 4 || !labelWords.every((w) => /^[A-Za-z&'\u2019\/\-]+$/.test(w))) continue;
        const label = labelWords.join(" "), flat = flatten(label);
        if (DENY.test(label) || isRecognised(flat) || CLASS_WORD_RE.test(flat) || labelHasFormWord(label)) continue;
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
        if (info && info.strip) {
          label = info.label; segStart = pos + info.off;
          for (;;) {      // "Seasoning: Masala Mix: ...": a second label right after the first names the same section
            const nxt = labelInfo(body.slice(segStart));
            if (!nxt || !nxt.strip) break;
            label = label + ": " + nxt.label; segStart += nxt.off;
          }
        }
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
    const ALLERGEN_LABEL = /^(?:allerg(?:en|y)[a-z ]*|note)\s*:\s*/i;
    // every "Contains ..." sentence of the text after the list ("May contain" never matches); see parser._contains_sentences
    function containsSentences(tail) {
      const out = []; let buf = "", depth = 0;
      for (let i = 0; i < tail.length; i++) {
        const ch = tail[i];
        if (OPEN.includes(ch)) depth++; else if (CLOSE.includes(ch)) depth = Math.max(depth - 1, 0);
        const isStop = ch === "." && depth === 0 && !(i > 0 && /\d/.test(tail[i - 1]) && i + 1 < tail.length && /\d/.test(tail[i + 1]));
        if (isStop || (ch === "\n" && depth === 0)) { out.push(buf); buf = ""; } else buf += ch;
      }
      out.push(buf);
      return out.flatMap((seg) => positiveSpans(collapse(seg).replace(ALLERGEN_LABEL, "")));
    }
    // See parser._positive_spans: only POSITIVE spans of a "contains"/negator sentence are declarations; negation is scoped to its span.
    const POLARITY = /(?<maybe>\bmay\s+contain\b)|(?<neg>\b(?:does\s+not\s+contain|do\s+not\s+contain|contains?\s+(?:no|nil|none|without)|free\s+(?:from|of)|without|nil|none|no|not)\b)|(?<pos>\bcontains?\b)/gi;
    function positiveSpans(seg) {
      const ms = [...seg.matchAll(POLARITY)];
      if (!ms.length || ms[0].index !== 0 || ms[0].groups.maybe) return [];
      const out = [];
      ms.forEach((m, k) => {
        if (!m.groups.pos) return;
        const end = k + 1 < ms.length ? ms[k + 1].index : seg.length;
        const text = stripChars(seg.slice(m.index + m[0].length, end), " ,;:-");
        if (text) out.push(m[0] + " " + text);          // the label's own keyword and casing
      });
      return out;
    }
    const NEG_CLAIM = /(?:^|[.\n])\s*((?:no|nil|without|free\s+from)\s+(?:added|artificial|preservatives?|colou?rs?|flavou?rs?|sweeteners?)\b)/i;
    // "a and b" / "a & b" at bracket depth 0; the caller decides whether both sides are ingredients
    function splitTopLevelAnd(raw) { return splitTopLevelAndEx(raw)[0]; }
    function splitTopLevelAndEx(raw) {
      const cuts = []; let depth = 0, m;
      const re = /[(\[{)\]}]|\s+(?:and|&)\s+/gi;
      while ((m = re.exec(raw))) {
        const tok = m[0];
        if (tok.length === 1 && OPEN.includes(tok)) depth++;
        else if (tok.length === 1 && CLOSE.includes(tok)) depth = Math.max(depth - 1, 0);
        else if (depth === 0) cuts.push([m.index, m.index + tok.length]);
      }
      const parts = [], connectors = []; let last = 0;
      for (const [a, b] of cuts) { parts.push(raw.slice(last, a).trim()); connectors.push(raw.slice(a, b).trim()); last = b; }
      parts.push(raw.slice(last).trim());
      const kept = parts.filter(Boolean);
      return kept.length > 1 && kept.length === parts.length ? [kept, connectors] : [[raw], []];
    }
    const countWords = (t) => (t.match(/[\p{L}\p{N}]+/gu) || []).length;
    const MILK_COMPOSITION = /^\s*((?:(?:pasteurized|pasteurised)\s+)?(?:buffalo milk|cow milk|goat milk|toned milk|double toned milk|milk))\s+(Fat\s*\d+(?:\.\d+)?\s*%\s*Min(?:imum)?\.?\s*,\s*SNF\s*\d+(?:\.\d+)?\s*%\s*Min(?:imum)?\.?)\s*$/i;
    function parseIngredientList(text, opts) {
      const assumeList = !!(opts && opts.assumeList);
      const norm = normaliseWs(text);
      const hf = findHeading(norm);
      let body, headingKind, headingText;
      if (hf) { body = norm.slice(hf.end); headingKind = hf.kind; headingText = hf.text; }
      else if (assumeList) { body = norm; headingKind = "assumed"; headingText = ""; }
      else return { found: false };
      let terminated = false; const declarations = [];
      const regionWords = countWords(body);
      let stop = STOP.exec(body);
      const claim = NEG_CLAIM.exec(body);
      if (claim) { const cs = claim.index + claim[0].length - claim[1].length; if (!stop || cs < stop.index) stop = { index: cs }; }   // a negation claim after the list is not an ingredient
      const bodyWithTail = stop ? body.slice(stop.index) : "";
      if (stop) {
        const tail = collapse(body.slice(stop.index));
        // the stop phrase takes its lead-in with it: a label right before it, or a claim opener (see parser.py)
        const lead = LEAD_IN.exec(body.slice(0, stop.index));
        body = body.slice(0, lead ? lead.indices[1][0] : stop.index);
        terminated = true;
        declarations.push(...containsSentences(bodyWithTail));
      }
      const composition = [];
      const cm = MILK_COMPOSITION.exec(body);
      if (cm) { composition.push(collapse(cm[2])); terminated = terminated || body.trimEnd().endsWith("."); body = cm[1]; }
      const keptWords = countWords(body);
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
      return { found: true, items, terminated, unbalanced, declarations, sections, composition, ignored: read.unread ? [collapse(read.unread)] : [], headingKind, headingText, regionWords, keptWords, tailWords: regionWords - keptWords };
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
    const insRef = {};     // display names only (ins_names.csv): "Recognised code, no processing rule yet"; never feeds a decision
    for (const r of T.ins_names) insRef[r.ins.toLowerCase().replace(/\s+/g, "")] = r;

    const synonyms = [...T.synonyms]
      .sort((a, b) => b.from.length - a.from.length)
      .map((r) => {
        const term = r.from.toLowerCase();   // a term starting or ending with a digit must not match inside a longer alphanumeric run
        const left = /^\d/.test(term) ? "(?<![a-z0-9])" : "(?<![a-z])", right = /\d$/.test(term) ? "(?![a-z0-9])" : "(?![a-z])";
        // an alias for a "... dal" term also absorbs a following "dal" (see normalise.py)
        let tail = r.to.toLowerCase().endsWith(" dal") && !term.endsWith(" dal") ? "(?:\\s+dal(?![a-z]))?" : "";
        // target-safe rewrite (mirrors normalise.py): an alias that is a strict word-prefix of its own target absorbs the remaining target words when they follow
        const toFlat = flatten(r.to);
        if (toFlat.startsWith(term + " ")) tail = "(?:\\s+" + esc(toFlat.slice(term.length + 1)).replace(/ /g, "\\s+") + "(?![a-z]))?";
        return { re: new RegExp(left + esc(term) + right + tail, "g"), to: r.to.toLowerCase() };
      });
    const markers = T.markers.map((r) => ({ re: new RegExp("(?<![a-z])(?<!no )(?<!no added )(?<!non )(?<!non-)(?<!without )(?<!free from )(?<!free of )(?<!source of )(?<!rich in )(?<!high in )" + esc(flatten(r.term)) + "(?![a-z])(?![ -]free(?![a-z]))"), row: r }));
    const claimMarkers = T.markers.filter((r) => r.strength === "strong").map((r) => ({ re: new RegExp("(?<![a-z])(?:source of|rich in|high in) " + esc(flatten(r.term)) + "(?![a-z])(?![ -]free(?![a-z]))"), row: r }));
    const lexicon = {};
    for (const r of T.lexicon) lexicon[flatten(r.term)] = r;
    const descriptors = new Set(T.descriptors.filter((r) => !(r.kinds || "").trim()).map((r) => r.word.toLowerCase()));
    const allDescriptorWords = new Set(T.descriptors.map((r) => r.word.toLowerCase()));      // every descriptors.csv row, incl. kind-scoped ones: label form words and the truncation test (mirrors parser._form_words and pipeline._vocab)
    const scopedDescriptors = {};          // kind-scoped descriptors ('toasted': whole_food;flour), mirrors classify._scoped_descriptors
    for (const r of T.descriptors) if ((r.kinds || "").trim()) scopedDescriptors[r.word.toLowerCase()] = new Set(r.kinds.split(";").map((k) => k.trim()).filter(Boolean));
    const singular = (t) => {
      if (t.length > 3 && t.endsWith("ies")) return t.slice(0, -3) + "y";
      if (t.length > 4 && t.endsWith("oes")) return t.slice(0, -2);
      if (t.length > 3 && t.endsWith("s") && !/(ss|us|is)$/.test(t)) return t.slice(0, -1);
      return t;
    };
    const singularPhrase = (p) => p.split(" ").map(singular).join(" ");
    const lexIndex = {};
    for (const term of Object.keys(lexicon)) { const k = singularPhrase(term); if (!(k in lexIndex)) lexIndex[k] = lexicon[term]; }
    const has = (o, k) => Object.prototype.hasOwnProperty.call(o, k);
    // 'toasted' (per-form-1, owner amendment 2): dropped only when the remaining name is one of the 23 terms Batch 4 placed and carries no other qualifier (mirrors classify._scoped_lookup)
    const SCOPED_TERMS = { toasted: new Set(["barley", "black rice", "buckwheat", "millet", "parboiled rice", "red rice", "rice", "sorghum", "wild rice", "amaranth flour", "barley flour", "buckwheat flour", "cornmeal", "millet flour", "oat flour", "quinoa flour", "rice flour", "rye flour", "semolina", "sorghum flour", "spelt flour", "wheat flour", "whole wheat flour"]) };
    const SCOPED_BENIGN = new Set(["unsalted", "organic", "whole", "plain", "pure", "white", "brown", "red", "common", "edible"]);
    function scopedLookup(name) {
      const words = name.split(" ").filter((t) => has(scopedDescriptors, t));
      const others = name.split(" ").filter((t) => t && !has(scopedDescriptors, t));
      for (const cand of [others.join(" "), others.filter((t) => !SCOPED_BENIGN.has(t)).join(" ")]) {
        const row = has(lexicon, cand) ? lexicon[cand] : has(lexIndex, singularPhrase(cand)) ? lexIndex[singularPhrase(cand)] : null;
        if (row && words.every((w) => scopedDescriptors[w].has(row.kind) && SCOPED_TERMS[w] && SCOPED_TERMS[w].has(row.term))) return row;
      }
      return null;
    }
    // mirrors classify.lookup: exact, singular, then both again without descriptor words
    function lookup(name) {
      if (has(lexicon, name)) return lexicon[name];
      if (has(lexIndex, singularPhrase(name))) return lexIndex[singularPhrase(name)];
      let toks = name.split(" ").filter(Boolean);
      while (toks.length && descriptors.has(toks[0])) {       // leading descriptors first: "pasteurised double toned milk" -> "double toned milk"
        toks = toks.slice(1);
        const lead = toks.join(" ");
        if (has(lexicon, lead)) return lexicon[lead];
        if (has(lexIndex, singularPhrase(lead))) return lexIndex[singularPhrase(lead)];
      }
      const kept = name.split(" ").filter((t) => t && !descriptors.has(t)).join(" ");
      if (kept && kept !== name) {
        if (has(lexicon, kept)) return lexicon[kept];
        if (has(lexIndex, singularPhrase(kept))) return lexIndex[singularPhrase(kept)];
      }
      if (name.split(" ").some((t) => has(scopedDescriptors, t))) return scopedLookup(name);   // kind- and TERM-scoped descriptor ('toasted'); mirrors classify._scoped_lookup
      return null;
    }
    const isRecognised = (name) => lookup(name) !== null;
    // headline aggregation (mirrors classify.other_open_items): names the other ACTIVE blockers of an abstention headed by weak markers, a colour note or a sweetener-foods entry
    function otherOpenItems(ings, skip) {
      const parts = [];
      const ings0 = ings;
      ings = ings.filter((i) => !skip.has(i.raw));
      const unrec = ings.filter((i) => !isRecognised(i.name)).map((i) => i.raw);
      if (unrec.length) parts.push("not in the local vocabulary: " + unrec.join(", "));
      const rec = ings.filter((i) => isRecognised(i.name)).map((i) => [i, lookup(i.name).kind]);
      const unpl = rec.filter(([, k]) => k === "unplaced").map(([i]) => i.raw);
      if (unpl.length) parts.push("recognised by name only, no source read places " + unpl.join(", "));
      const waters = ings.flatMap(i => namedWaterUnresolved(i, ings0.length === 1));
      if (waters.length) parts.push("a named water's plain form or standalone scope is not established: " + waters.join(", "));
      const juices = rec.filter(([i,k]) => k === "fruit_juice" && !(ings0.length === 1 && plainJuiceStated(i))).map(([i]) => i.raw).concat(ings.flatMap(nestedJuiceUnresolved));
      if (juices.length) parts.push("a named juice's processing and composition are not established: " + juices.join(", "));
      const pw = rec.filter(([i, k]) => fatPowder(i, k) || ((k === "food_powder" || powderRouted(i, k)) && !(ings0.length === 1 && powderCompositionStated(i)))).map(([i]) => i.raw);
      if (pw.length) parts.push("a powder is named and its composition is not established: " + pw.join(", "));
      return parts.length ? "; other open items: " + parts.join("; ") : "";
    }

    /* ---------- declared role (mirrors roles.py): the class the SCANNED label names for the entry a code sits in; display only ---------- */
    const ROLE_FILLER = new Set(["contains", "contain", "permitted", "natural", "synthetic", "artificial", "nature", "identical", "added", "food", "class", "i", "ii", "iii", "1", "2", "substance", "substances", "and", "&", "the", "of"]);
    const roleRows = [...T.declared_roles].sort((a, b) => b.term.length - a.term.length).map((r) => ({ re: new RegExp("(?<![a-z])" + esc(r.term) + "s?(?![a-z])"), row: r }));
    const markerFlat = (t) => t.toLowerCase().replace(/[-–—_/]/g, " ").replace(/\s+/g, " ").trim();
    const markerPats = T.markers.map((r) => ({ re: new RegExp("(?<![a-z])" + esc(markerFlat(r.term)) + "(?![a-z])"), strength: r.strength }));
    const countedAsMarker = (role) => { const text = role.toLowerCase().replace(/[-–—_/]/g, " "); return markerPats.some((m) => m.re.test(text) && m.strength === "strong"); };
    function declaredRoles(name) {
      let text = name.toLowerCase().replace(/[,;&/]/g, " ");
      const found = [];
      for (const { re, row } of roleRows) {
        const m = re.exec(text);
        if (m) { found.push(row.role); text = text.slice(0, m.index) + " " + text.slice(m.index + m[0].length); }
      }
      const left = (text.match(/[a-z0-9]+/g) || []).filter((t) => !ROLE_FILLER.has(t));
      if (left.length || !found.length) return [];
      return [...new Set(found)];
    }
    function labelPhrase(raw) {
      let out = "", depth = 0;
      for (const ch of raw) {
        if ("([{".includes(ch)) depth++;
        else if (")]}".includes(ch)) depth = Math.max(depth - 1, 0);
        else if (!depth) out += ch;
      }
      const s = stripChars(out.replace(/\s+/g, " ").trim(), " ,;.:*-");
      return s.replace(/^contains\s*:?\s*/i, "").trim();
    }
    function declaredRoleNotes(roles, phrase) {
      if (!roles.length) return [];
      const notes = [`Declared on the label as: "${phrase}".`];
      if (/(?:emulsifying|stabili[sz]ing)\s+(?:&\s*)?(?:and\s+)?(?:stabili[sz]ing\s+)?agent/i.test(phrase)) notes.push("That wording is mapped to the class by a provisional role-phrase mapping (no source names the phrase).");
      if (roles.length > 1) notes.push("The codes listed with it share this entry, so the label does not say which code has which of these roles.");
      for (const role of roles) {
        const r = roleRows.find((x) => x.row.role === role).row, src = r.cite;
        if (r.nova_status === "group4_listed")
          notes.push(`Declared as ${role}: the NOVA source lists ${r.source_wording} among the additive classes of ultra-processed foods (${src}). ` + (countedAsMarker(role) ? "This tool counts that class on the label as a Group 4 marker." : "This tool does not count this class as a marker yet, so it leaves the result uncertain."));
        else if (r.nova_status === "group3_allowed")
          notes.push(`Declared as ${role}: no Group 4 marker detected for this role per ${src}: it is not among the additive classes the source says are used only in ultra-processed foods. The source says processed (Group 3) foods may contain such additives (${r.source_wording}) and also mentions them in its Group 4 definition, so this role does not by itself separate the groups.`);
        else
          notes.push(`Declared as ${role}: this class is not named in the NOVA source read (${src}); ` + (countedAsMarker(role) ? "this tool counts it as a marker on the basis of research/02, not of that source." : "this tool does not use it to decide a group."));
      }
      return notes;
    }

    /* ---------- normalise ---------- */
    const CODE = "\\d{3,4}(?:\\s*\\(\\s*[ivx]+\\s*\\))?(?:[a-z](?![a-z]))?";
    const INS_RE = new RegExp("(?<![a-z0-9])(?:ins|e)\\s*[-:.]?\\s*(?<codes>" + CODE + "(?:\\s*(?:,|and|&|/)\\s*" + CODE + ")*)", "g");
    const CODE_RE = new RegExp(CODE, "g");
    const canonicalCode = (c) => c.toLowerCase().replace(/\s+/g, "");

    const ADDITIVE_CLASSES = new Set(["cosmetic_additive", "ordinary_additive", "unlisted_additive"]);
    const bareClasses = new Set(T.markers.filter((r) => ADDITIVE_CLASSES.has(r.marker_class)).map((r) => r.term.toLowerCase()));
    const bareAliases = T.synonyms.filter((r) => bareClasses.has(r.to.toLowerCase())).map((r) => r.from.toLowerCase());
    const bareTerms = [...new Set([...bareClasses, ...bareAliases])]
      .sort((a, b) => b.length - a.length).map(esc).join("|");
    const classTerms = [...bareClasses].sort((a, b) => b.length - a.length).map(esc).join("|");
    const CLASS_WORD_RE = new RegExp("(?<![a-z])(?:" + classTerms + ")(?:s|ing|ings)?(?![a-z])");
    // "Flavour Enhancers (627, 631)": bare codes, only right after an additive class word
    const BARE_RE = new RegExp("(?<![a-z])(?:" + bareTerms + ")(?:s|ing|ings)?(?:\\s+of\\s+[a-z]+(?:\\s+[a-z]+){0,2})?\\s*[(\\[{]\\s*(?<codes>" + CODE + "(?:\\s*(?:,|and|&|/)\\s*" + CODE + ")*)\\s*[)\\]}]", "g");

    function isAdditiveAbsenceClaim(raw) {
      const low = stripChars(raw.toLowerCase(), " ,;:.");
      if (!/^(?:no|not|without|free\s+(?:from|of)|does\s+not\s+contain|do\s+not\s+contain)\b/.test(low)
          && !/\b(?:free|absent|not\s+(?:added|used|present))$/.test(low)) return false;
      return new RegExp("(?<![a-z])(?:" + bareTerms + ")(?:s|ing|ings)?(?![a-z])").test(low);
    }
    function extractIns(text) {
      if (isAdditiveAbsenceClaim(text)) return {stripped:text.toLowerCase(), uses:[]};
      const uses = [];
      const addUse = (c) => {
        const code = canonicalCode(c);
        const row = insTable[code];
        const classes = row ? (row.functional_class || "").split(";").map((x) => x.trim()).filter(Boolean) : [];
        const ref = row ? null : insRef[code];
        uses.push({ code, name: row ? row.name : null, source: row ? row.source : null, classes, strength: row ? row.strength : null, ingredient: null, section: null,
          ref_name: ref ? ref.name : null, ref_classes: ref ? (ref.functional_classes || "").split(";").map((x) => x.trim()).filter(Boolean) : [], ref_partial: !!(ref && (ref.reading || "").startsWith("partial")), ref_source: ref ? (ref.source || null) : null, declaration_only:false, declared: null, declared_roles: [], role_notes: [] });
      };
      const low = text.toLowerCase().replace(BARE_RE, (...a) => {
        const m = a[0], groups = a[a.length - 1];
        for (const c of groups.codes.match(CODE_RE) || []) addUse(c);
        return m.slice(0, m.indexOf(groups.codes)).replace(/[([{ \t]+$/, "") + " ";
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
    // footnote marks are removed only at item / sub-item / connector / percentage / bracket boundaries (mirrors normalise.strip_footnotes); a mark inside a multi-word phrase is left untouched
    const FOOT_BOUNDARY = "(?=\\s*(?:$|[)\\]},;:.]|&|\\(|\\b(?:and|or)\\b))";
    const FOOTNOTE_RE = new RegExp("(?<=[a-zA-Z0-9)\\]}])\\s*(?:#{1,3}|\\*{1,3}|[\\u2020\\u2021]|\\u201D)" + FOOT_BOUNDARY, "gu");
    const FOOTNOTE_NO_QUOTE_RE = new RegExp("(?<=[a-zA-Z0-9)\\]}])\\s*(?:#{1,3}|\\*{1,3}|[\\u2020\\u2021])" + FOOT_BOUNDARY, "gu");
    function stripFootnotes(text) {
      if (text.includes("\u201D") && (text.includes("\u201C") || text.includes('"'))) return text.replace(FOOTNOTE_NO_QUOTE_RE, "");
      return text.replace(FOOTNOTE_RE, "");
    }
    function normaliseIngredient(raw) {
      let { stripped: text, uses } = extractIns(raw);
      text = text.replace(/\d+(?:\.\d+)?\s*%/g, " ");
      text = stripFootnotes(text);
      for (const s of synonyms) text = text.replace(s.re, s.to);
      text = flatten(text);
      let [name, inner] = splitBrackets(text);
      name = stripFootnotes(name);
      inner = stripFootnotes(inner);
      const roles = declaredRoles(name), phrase = roles.length ? labelPhrase(raw) : null, notes = declaredRoleNotes(roles, phrase || "");
      uses.forEach((u) => { u.ingredient = raw; u.declared = phrase; u.declared_roles = roles;
        u.class_conflict = !!(u.classes.length && roles.length && !u.classes.some((c) => roles.includes(c)));
        u.role_notes = u.class_conflict ? [`This entry declares ${roles.join(" & ")}, but at least one code has a different class in this project mapping. The mismatch is unresolved, not proof the label is wrong or that a code has no other function. No marker evidence from this entry is used.`] : notes; });
      if (uses.some((u) => u.class_conflict)) {
        const conflictNotes = uses.find((u) => u.class_conflict).role_notes;
        uses.forEach((u) => {u.class_conflict = true; u.role_notes = conflictNotes;});
      }
      return { raw, name, inner, ins: uses, text: (name + " " + inner).trim() };
    }

    /* ---------- classify ---------- */
    // A colour word that is only a short bracketed function note on a named ingredient ("Turmeric (Colouring & Spices)") is not a declared ADDED colour.
    const MILK_TERMS = ["milk", "toned milk", "double toned milk", "buffalo milk", "milk solids", "cow milk", "goat milk"];   // milk context of the milk-plus-culture rule
    const NOTE_PREFIX = "(?:(?:for|as|used|a|an|the|to|give|added|natural|permitted|food|synthetic|artificial) )*", NOTE_COLOUR = "colou?r(?:ant)?(?: agent)?", NOTE_OTHER = "(?:spices?|seasoning|flavou?rs?)";
    const COLOUR_NOTE = new RegExp(`^${NOTE_PREFIX}(?:${NOTE_COLOUR}(?: (?:and|&) ${NOTE_OTHER})?|${NOTE_OTHER} (?:and|&) ${NOTE_COLOUR})$`);
    const isColourNote = (inner) => COLOUR_NOTE.test(inner.trim());
    const colourNoteOnly = (ing) => !!ing.name && isColourNote(ing.inner) && !markers.some(({ re }) => re.test(ing.name));
    // mirrors classify.sweetener_foods_only: the entry's own name is only "sweetener" and its bracket names only recognised foods, no INS code
    function sweetenerFoodsOnly(ing) {
      if (ing.ins.length || !ing.inner || (ing.name !== "sweetener" && ing.name !== "natural sweetener")) return false;
      const parts = ing.inner.split(/\s*(?:,|;|&|\band\b)\s*/).map((p) => p.trim()).filter(Boolean);
      return parts.length > 0 && parts.every((p) => { const r = lookup(p); return r !== null && (r.kind === "whole_food" || r.kind === "legume" || r.kind === "vegetable" || r.kind === "fruit" || r.kind === "culinary"); });
    }
    // item-level condition for the nut/seed rows (mirrors classify.nut_added_salt_or_sugar)
    const NUT_ADDED = new Set(["salt", "salted", "sugar", "sugared", "sweetened", "candied", "caramelised", "caramelized", "honey", "glazed", "jaggery", "syrup"]);
    // legume rows (kind legume): the same item-level condition plus brine (mirrors classify.legume_added_salt_sugar_or_brine)
    const BRINE_KINDS = ["legume", "vegetable", "fruit"];
    const GUARDED_KINDS = BRINE_KINDS.concat(["nut_seed"]);   // nut-guard-1: the canned/brine/bracket guards also apply to kind nut_seed
    const LEGUME_ADDED = new Set([...NUT_ADDED, "brine", "brined"]);
    // FAO Table 1 permits vitamin/mineral additions to Group 1 foods.
    // Other recognition-only bracket items still have no NOVA placement.
    const NUTRIENT_LABELS = new Set(["vitamins and minerals", "vitamins & minerals", "vitamins", "minerals"]);
    function nestedUnplaced(ing) {
      const out = [];
      for (const part of (ing.inner || "").split(/\s*(?:,|;|&|\band\b)\s*/)) {
        const row = lookup(part.trim());
        if (row && row.kind === "unplaced" && !NUTRIENT_LABELS.has(row.term)) out.push(part.trim() + " (inside " + ing.raw + ")");
      }
      return [...new Set(out)];
    }
    function addedIn(ing, words) {
      // Exact existing fruit name, not an added-sugar declaration. Keep two tokens.
      const text = ing.text.toLowerCase().replace(/\bsugar\s+(apples?)\b/g, "fruit $1");
      const toks = text.match(/[a-z]+/g) || [];
      for (let i = 0; i < toks.length; i++) {
        if (words.has(toks[i])) {
          if (toks.slice(Math.max(0, i - 2), i).some((x) => ["no", "without", "non", "free"].includes(x)) || (i + 1 < toks.length && toks[i + 1] === "free")) continue;
          return true;
        }
      }
      return false;
    }
    // unknown additions on the same item are never laundered (mirrors classify.bracket_residual)
    const BRACKET_BENIGN = new Set(["with", "without", "skin", "peel", "added", "no", "non", "free", "of", "in", "from", "as", "the", "a", "an", "natural", "cooked", "organic", "whole", "percent", "less", "than", "only", "pure", "plain", "ins", "e"]);
    // species-of-origin provenance (mirrors classify.bracket_residual): cow/buffalo/goat is benign only in a bracket that holds 'milk' and only on a milk head item
    const SPECIES_WORDS = new Set(["cow", "buffalo", "goat"]);
    const MILK_PROVENANCE_WORDS = new Set(["milk", "toned", "double", "solids"]);
    function bracketResidual(ing) {
      if (!ing.inner) return [];
      const ok = (t) => descriptors.has(t) || BRACKET_BENIGN.has(t) || LEGUME_ADDED.has(t) || LEGUME_PRESERVED.has(t);
      const head = lookup(ing.name);
      const headIsMilk = !!head && head.kind === "whole_food" && MILK_TERMS.includes(head.term) && head.term !== "milk solids";
      const residual = [];
      for (const part of ing.inner.split(/\s*(?:,|;|&|\band\b)\s*/)) {
        const toks = part.match(/[a-z]+/g) || [];
        if (toks.some((t) => SPECIES_WORDS.has(t)) && !headIsMilk) { residual.push(part.trim()); continue; }       // per-form-2b: a species-milk part is benign only on a plain milk head item
        if (!toks.length || isRecognised(part.trim()) || toks.every(ok)) continue;
        if (headIsMilk && toks.includes("milk") && toks.some((t) => SPECIES_WORDS.has(t)) && toks.every((t) => ok(t) || SPECIES_WORDS.has(t) || MILK_PROVENANCE_WORDS.has(t))) continue;
        residual.push(part.trim());
      }
      return residual;
    }
    const LEGUME_PRESERVED = new Set(["canned", "tinned", "bottled", "jarred", "preserved", "pickled"]);
    const legumePreservedForm = (ing) => addedIn(ing, LEGUME_PRESERVED);
    // whole-food-guard-1 (mirrors classify.whole_food_observed / whole_food_nested): abstention only; explicit same-food equivalences, no taxonomy
    const SAME_MILK_PARTS = new Set(["milk", "cow milk", "buffalo milk", "goat milk"]);
    function wholeFoodObserved(ing, kind) {
      // scoped-flour-4: mirror the bounded added-condition check, not a raw-food mixture ban.
      if (!["whole_food", "flour"].includes(kind)) return [];
      // Keep the existing supported Group 3 salted-grain route and prior culinary exclusions.
      if (kind === "flour" && grainAddedSalt(ing, kind)) return (ing.inner || "").split(/\s*(?:,|;|&|\band\b)\s*/).map((p) => p.trim().toLowerCase()).filter((p) => lookup(p) && SOURCE_PLACED_CULINARY.has(lookup(p).term));
      let obs = Array.from(new Set(nutAddedObserved(ing).concat(Array.from(LEGUME_PRESERVED).sort().filter((w) => addedIn(ing, new Set([w]))))));
      if (grainAddedSalt(ing, kind)) {
        const saltRows = new Set(T.lexicon.filter((r) => r.kind === "culinary" && (r.term === "salt" || r.term.endsWith(" salt"))).map((r) => r.term));
        obs = obs.filter((o) => o !== "salt" && o !== "salted" && !(lookup(o) && saltRows.has(lookup(o).term)));
      }
      return obs;
    }
    function wholeFoodNested(ing, kind) {
      const head = lookup(ing.name);
      if (kind !== "whole_food" || !head || !ing.inner) return [];
      return ing.inner.split(/\s*(?:,|;|&|\band\b)\s*/).map((p) => p.trim()).filter((p) => {
        const row = p ? lookup(p) : null;
        if (!row || ["neutral", "culture", "culinary"].includes(row.kind)) return false;
        const ht = head.term, pt = row.term;
        return !(pt === ht || (["egg", "eggs"].includes(ht) && ["egg", "eggs"].includes(pt)) || (MILK_TERMS.includes(ht) && ht !== "milk solids" && SAME_MILK_PARTS.has(pt)) || (ht === "dehydrated vegetable" && row.kind === "vegetable"));
      });
    }
    // descriptor "powder" routing (mirrors classify.powder_routed): whole_food, legume and vegetable items carrying the word follow the food_powder behaviour
    const POWDER_WORDS = new Set(["powder", "powdered"]);
    const POWDER_ROUTED = ["whole_food", "legume", "vegetable", "fruit", "nut_seed"];
    function powderCompositionStated(ing) {
      const ownRaw = splitBrackets(ing.raw)[0], ownToks = ownRaw.toLowerCase().match(/[a-z]+/g) || [];
      const row = lookup(ing.name), claims = [ownRaw];
      const base = lookup(flatten(ing.name.replace(/\b(?:powder|powdered)\b/g, " ")));
      const qualityWords = new Set(["whole", "pure", "plain", "powder", "powdered", "percent", "natural", "organic", "only"]);
      for (const part of rawBracketParts(ing.raw)) {
        const toks = part.toLowerCase().match(/[a-z]+/g) || [];
        if (toks.every((t) => qualityWords.has(t))) { claims.push(part); continue; }
        const child = normaliseIngredient(part), childRow = lookup(child.name);
        if (childRow && ((base && childRow.term === base.term) || (row && childRow.term === row.term))) {
          const childOwn = splitBrackets(part)[0], childToks = childOwn.toLowerCase().match(/[a-z]+/g) || [];
          if (/(?<![\d.])100(?:\.0+)?\s*%/.test(childOwn.toLowerCase())) return true;
          if (childToks.includes("whole") && !childToks.includes("milk") && !MILK_TERMS.includes(childRow.term)) return true;
        }
      }
      if (claims.some((part) => /(?<![\d.])100(?:\.0+)?\s*%/.test(part.toLowerCase()))) return true;
      const toks = claims.join(" ").toLowerCase().match(/[a-z]+/g) || [];
      return toks.includes("whole") && !ownToks.includes("milk") && !(row && MILK_TERMS.includes(row.term));
    }
    // powdered milk is placed by name (FAO Table 1 Group 1 'fresh, powdered or pasteurized milk'): mirrors classify.milk_powder_named
    const MILK_POWDER_ROWS = ["milk", "toned milk", "double toned milk", "buffalo milk", "cow milk", "goat milk", "sheep milk", "camel milk"];
    const MILK_POWDER_WORDS = new Set(["milk", "toned", "double", "buffalo", "cow", "goat", "sheep", "camel", "whole", "skimmed", "skim", "powder", "powdered"]);
    function milkPowderNamed(ing) {
      const row = lookup(ing.name);
      const toks = ing.text.toLowerCase().match(/[a-z]+/g) || [];
      return !!row && MILK_POWDER_ROWS.includes(row.term) && (toks.includes("powder") || toks.includes("powdered")) && toks.every((t) => MILK_POWDER_WORDS.has(t));
    }
    // culinary-guard-1 (mirrors classify.is_fat_row / fat_powder)
    const FAT_LAST_WORDS = new Set(["oil", "fat", "butter", "ghee", "lard", "palmolein", "olein"]);
    const FAT_ROWS = new Set(["refined oil", "edible vegetable oil", "vegetable oil"]);
    const isFatRow = (row) => !!row && row.kind === "culinary" && (FAT_LAST_WORDS.has(row.term.split(" ").slice(-1)[0]) || FAT_ROWS.has(row.term));
    // animal-guard-1 (mirrors classify.is_animal_row / animal_dried / animal_powder)
    const ANIMAL_MARK = "meat, poultry, fish and seafood, whole or in the form of steaks, fillets and other cuts";
    const ANIMAL_DRIED = new Set(["dried", "dehydrated"]);
    const isAnimalRow = (row) => !!row && row.kind === "whole_food" && row.source.includes(ANIMAL_MARK);
    const DRIED_SCOPES = ["DRIED-G3-SCOPE: meat", "DRIED-G3-SCOPE: finfish"];
    // cheese-g3-1 (mirrors classify.is_cheese_row / _CHEESE_ABSTAIN)
    const CHEESE_ABSTAIN = new Set(["powder", "powdered", "processed", "smoked", "spread", "sauce", "flavour", "flavor", "flavoured", "flavored", "analogue", "analog", "substitute", "dip", "grated", "shredded", "dried", "dehydrated", "canned", "tinned", "pickled", "breaded", "fried", "baked", "melted", "sliced", "blend"]);
    // canned-fish-g3-1 (mirrors classify.is_canned_fish_row / canned_fish_verdict)
    const CANNED_SIBLINGS = new Set(["water", "salt", "olive oil", "sunflower oil", "vegetable oil", "soybean oil", "refined oil", "edible vegetable oil"]);
    const CANNED_INNER_OK = new Set(["oil", "olive oil", "sunflower oil", "vegetable oil", "salt", "water", "brine"]);
    const CANNED_ABSTAIN = new Set([...CHEESE_ABSTAIN].filter((w) => w !== "canned" && w !== "tinned"));
    const isCannedFishRow = (row) => !!row && row.kind === "whole_food" && row.source.includes("CANNED-FISH-G3");
    const cannedFishVerdict = (ings) => {
      const idx = ings.map((i, n) => (isCannedFishRow(lookup(i.name)) ? n : -1)).filter((n) => n >= 0);
      if (!idx.length) return null;
      if (idx.length !== 1) return [null, "more than one canned fish item is listed, so the combination is not established"];
      const t = ings[idx[0]];
      const others = ings.filter((_, n) => n !== idx[0]);
      if (others.some((o) => !CANNED_SIBLINGS.has((lookup(o.name) || {}).term) || o.inner)) return [null, "the list holds something besides the canned fish and water, salt or a plain oil, so no source read here places the combination"];
      const parts = (t.inner || "").replace(/^\s*(?:in|packed in)\s+/i, "").split(/\s*(?:,|;|&|\band\b)\s*/).map((p) => p.trim().toLowerCase()).filter(Boolean);
      if (parts.some((p) => !CANNED_INNER_OK.has(p)) || addedIn(t, CANNED_ABSTAIN)) return [null, "the item's bracket or wording holds something besides oil, salt, water or brine, or a stated form, so no source read here places it"];
      return [3, "canned fish (Brazil Dietary Guidelines Group 3 and PAHO NP Model Panel A: 'canned sardine and tuna')"];
    };
    // tomato-g3-1 (mirrors classify.is_tomato_conc_row / tomato_conc_verdict)
    const TOMATO_OK_TERMS = new Set(["salt", "sugar", "iodised salt"]);
    const TOMATO_INNER_OK = new Set(["tomato", "tomatoes", "salt", "sugar"]);
    const isTomatoConcRow = (row) => !!row && row.kind === "whole_food" && row.source.includes("TOMATO-CONC-G3");
    const tomatoConcVerdict = (ings) => {
      const idx = ings.map((i, n) => (isTomatoConcRow(lookup(i.name)) ? n : -1)).filter((n) => n >= 0);
      if (!idx.length) return null;
      if (idx.length !== 1) return [null, "more than one tomato concentrate item is listed, so the combination is not established"];
      const t = ings[idx[0]];
      const others = ings.filter((_, n) => n !== idx[0]);
      if (others.some((o) => !TOMATO_OK_TERMS.has((lookup(o.name) || {}).term) || o.inner)) return [null, "the list holds something besides the tomato concentrate and salt or sugar, so no source read here places the combination"];
      const parts = (t.inner || "").split(/\s*(?:,|;|&|\band\b)\s*/).map((p) => p.trim().toLowerCase()).filter(Boolean);
      if (parts.some((p) => !TOMATO_INNER_OK.has(p)) || addedIn(t, CHEESE_ABSTAIN)) return [null, "the concentrate's bracket or wording holds something besides tomato, salt or sugar, so no source read here places it"];
      const stated = others.length > 0 || parts.some((p) => p === "salt" || p === "sugar");
      if (!stated) return [null, "salt or sugar is not stated, and the Brazil Group 3 clause covers tomato concentrates only 'with salt and/or sugar'"];
      return [3, "tomato concentrate with stated salt or sugar (Brazil Dietary Guidelines Group 3: 'tomato extract or concentrates (with salt and/or sugar)')"];
    };
    const isCheeseRow = (row) => !!row && row.kind === "whole_food" && row.source.includes("CHEESE-G3");
    // cured-meat-g3-1 (mirrors classify.is_cured_meat_row / _CURED_ABSTAIN)
    const CURED_ABSTAIN = new Set([...CHEESE_ABSTAIN, "raw", "uncooked", "bits", "bit", "meatless", "vegan", "vegetarian", "plant", "turkey", "chicken", "beef", "pork", "style", "salad", "loaf", "sausage", "stick", "sticks", "cured", "brined", "honey", "water", "added"]);
    // yoghurt-g1-1 (mirrors classify.is_yoghurt_row / _YOGHURT_ABSTAIN)
    const YOGHURT_ABSTAIN = new Set([...CHEESE_ABSTAIN, "sweetened", "sugar", "sugared", "fruit", "fruity", "low", "fat", "drinking", "drink", "frozen", "probiotic", "greek", "strawberry", "mango", "vanilla", "honey", "dried", "freeze"]);
    const isYoghurtRow = (row) => !!row && row.kind === "whole_food" && row.source.includes("YOGHURT-G1");
    // smoked-fish-g3-1 (mirrors classify.is_smoked_fish_row / _SMOKED_FISH_ABSTAIN)
    const SMOKED_FISH_ABSTAIN = new Set([...CHEESE_ABSTAIN].filter((w) => w !== "smoked").concat(["raw", "uncooked", "salted", "brined", "pate", "mousse", "cakes", "cake", "sauce", "pie", "salad", "soup", "paste", "fillet", "fillets"]));
    const isSmokedFishRow = (row) => !!row && row.kind === "whole_food" && row.source.includes("SMOKED-FISH-G3");
    const isCuredMeatRow = (row) => !!row && row.kind === "whole_food" && row.source.includes("CURED-MEAT-G3");
    const animalDried = (ing, kind) => { const row = lookup(ing.name); return kind === "whole_food" && isAnimalRow(row) && DRIED_SCOPES.some((m) => row.source.includes(m)) && addedIn(ing, ANIMAL_DRIED); };
    const animalDriedUnscoped = (ing, kind) => { const row = lookup(ing.name); return kind === "whole_food" && isAnimalRow(row) && !DRIED_SCOPES.some((m) => row.source.includes(m)) && addedIn(ing, ANIMAL_DRIED); };
    const animalPowder = (ing, kind) => kind === "whole_food" && isAnimalRow(lookup(ing.name)) && addedIn(ing, POWDER_WORDS);
    // direct-culinary-2: no blanket culinary or raw-food guard expansion.
    const SOURCE_PLACED_CULINARY = new Set(["corn starch", "baking powder", "baking soda"]);
    const fatBracketResidual = (ing) => {
      const head = lookup(ing.name);
      if (!head || !(isFatRow(head) || SOURCE_PLACED_CULINARY.has(head.term)) || !ing.inner) return [];
      const ok = (t) => descriptors.has(t) || BRACKET_BENIGN.has(t) || LEGUME_ADDED.has(t) || LEGUME_PRESERVED.has(t);
      const out = [];
      for (const part of ing.inner.split(/\s*(?:,|;|&|\band\b)\s*/)) {
        const p = part.trim(), toks = p.toLowerCase().match(/[a-z]+/g) || [];
        if (!toks.length) continue;
        if (isFatRow(head) && ["oil", "fat"].some((w) => isFatRow(lookup(p.toLowerCase() + " " + w)))) continue;
        if (head.term === "corn starch" && ["corn", "maize"].includes(p.toLowerCase())) continue;
        const row = lookup(p);
        if (row) { if (row.kind !== "culinary") out.push(p); }
        else if (!toks.every(ok)) out.push(p);
      }
      return out;
    };
    const fatPowderStated = (ing) => /(?<![\d.])100(?:\.0+)?\s*%/.test(ing.raw.toLowerCase().replace(/[(\[{][^)\]}]*[)\]}]/g, ""));
    const PLAIN_CONDITION_CULINARY = new Set(["cocoa powder", "coconut cream", "milk cream", "unsweetened baking chocolate", "gelatin powder"]);
    const plainCulinaryResidual = (ing) => {
      const head = lookup(ing.name);
      if (!head || !PLAIN_CONDITION_CULINARY.has(head.term) || !ing.inner) return [];
      const out = [];
      for (const part of ing.inner.split(/\s*(?:,|;|&|\band\b)\s*/)) {
        const p = part.trim(), toks = p.toLowerCase().match(/[a-z]+/g) || [];
        if (!toks.length) continue;
        if (toks.length === 1 && toks[0] === "unsweetened") continue;
        out.push(p);
      }
      return out;
    };
    const fatPowder = (ing, kind) => kind === "culinary" && isFatRow(lookup(ing.name)) && addedIn(ing, POWDER_WORDS) && !fatPowderStated(ing);
    function powderRouted(ing, kind) {
      if (!POWDER_ROUTED.includes(kind)) return false;
      // A named child is not a powder form of its parent.
      let powderNamed = addedIn({ raw: ing.raw, name: ing.name, inner: "", text: ing.name }, POWDER_WORDS);
      for (const part of (ing.inner || "").split(/\s*(?:,|;|&|\band\b)\s*/)) {
        const toks = part.match(/[a-z]+/g) || [];
        if (!lookup(part.trim()) && toks.length && toks.every((t) => descriptors.has(t) || BRACKET_BENIGN.has(t)))
          powderNamed = powderNamed || addedIn({ raw: part, name: part, inner: "", text: part }, POWDER_WORDS);
      }
      if (!powderNamed) return false;
      if (kind === "whole_food" && milkPowderNamed(ing)) return false;
      if (GUARDED_KINDS.includes(kind) && (legumeAddedSaltSugarOrBrine(ing) || legumePreservedForm(ing))) return false;
      return true;
    }
    function rawBracketParts(raw) {
      const groups = [], parts = [];
      let depth = 0, start = 0;
      for (let n = 0; n < raw.length; n++) {
        const ch = raw[n];
        if (OPEN.includes(ch)) { if (!depth) start = n + 1; depth++; }
        else if (CLOSE.includes(ch)) { if (depth === 1) groups.push(raw.slice(start, n)); depth = Math.max(depth - 1, 0); }
      }
      if (depth) groups.push(raw.slice(start));
      for (const group of groups) {
        depth = 0; start = 0;
        for (const m of group.matchAll(/[()\[\]{},;&]|\band\b/gi)) {
          const token = m[0];
          if (OPEN.includes(token)) depth++;
          else if (CLOSE.includes(token)) depth = Math.max(depth - 1, 0);
          else if (!depth) { parts.push(group.slice(start, m.index).trim()); start = m.index + token.length; }
        }
        parts.push(group.slice(start).trim());
      }
      return parts.filter(Boolean);
    }
    function nestedPowderUnresolved(ing) {
      if (!ing.inner) return [];
      const out = [];
      for (const part of rawBracketParts(ing.raw)) {
        const child = normaliseIngredient(part), row = lookup(child.name);
        let unresolved = nestedPowderUnresolved(child).length > 0;
        if (row) {
          const kind = row.kind;
          unresolved = unresolved || animalPowder(child, kind) || fatPowder(child, kind);
          if (kind === "food_powder" || powderRouted(child, kind))
            unresolved = unresolved || !powderCompositionStated(child);
        }
        if (unresolved) out.push(part + " (inside " + ing.raw + ")");
      }
      return [...new Set(out)];
    }
    // salted grain guard (per-form-2a; mirrors classify.grain_added_salt): the 23 Batch-4 terms with salt added in the item's own name or bracket
    const GRAIN_SALT_WORDS = new Set(["salt", "salted"]);
    const grainAddedSalt = (ing, kind) => (kind === "whole_food" || kind === "flour") && addedIn(ing, GRAIN_SALT_WORDS) && (() => { const row = lookup(ing.name); return !!row && SCOPED_TERMS.toasted.has(row.term); })();
    const nutAddedSaltOrSugar = (ing) => addedIn(ing, NUT_ADDED);
    const NUT_OBSERVED_ORDER = ["salt", "salted", "sugar", "sugared", "sweetened", "candied", "caramelised", "caramelized", "honey", "glazed", "jaggery", "syrup", "brine", "brined"];
    const nutAddedObserved = (ing) => Array.from(new Set(NUT_OBSERVED_ORDER.filter((w) => addedIn(ing, new Set([w]))).concat((ing.inner || "").split(/\s*(?:,|;|&|\band\b)\s*/).map((p) => p.trim()).filter((p) => p && isRecognised(p) && lookup(p).kind === "culinary").map((p) => p.toLowerCase()))));
    const nutGroup3Driver = (ing) => {
      const obs = nutAddedObserved(ing);
      return !obs.length || obs.every((w) => ["salt", "salted", "sugar", "sugared"].includes(w))
        ? "nut or seed with added salt or sugar (FAO Table 1 Group 3: 'salted or sugared nuts and seeds')"
        : "nut or seed with added " + obs.join(", ") + " (FAO Table 1 Group 3 definition: 'Products made by adding salt, oil, sugar or other group 2 ingredients to group 1 foods'; class-instance of that rule, no FAO example names this form)";
    };
    const legumeAddedSaltSugarOrBrine = (ing) => addedIn(ing, LEGUME_ADDED) || (ing.inner || "").split(/\s*(?:,|;|&|\band\b)\s*/).some((p) => p.trim() && isRecognised(p.trim()) && lookup(p.trim()).kind === "culinary");
    function hitsFor(ing) {
      if (isAdditiveAbsenceClaim(ing.raw)) return [];
      if (ing.ins.some((u) => u.class_conflict)) return [{strength:"unlisted", marker_class:"unlisted_additive", detail:"declared class and local code mapping differ; entry unresolved", source:"label wording versus existing project mapping; no source resolves this mismatch"}];
      let hits = [];
      const noteOnly = colourNoteOnly(ing), sweetFoods = sweetenerFoodsOnly(ing);
      for (const { re, row } of markers) {
        if (noteOnly) break;
        if (sweetFoods && row.term === "sweetener") continue;      // the bracket names foods, so the class word is not counted      // the name has no marker and the bracket is only a function note: its words decide nothing
        if (re.test(ing.text)) hits.push({ strength: row.strength, marker_class: row.marker_class, detail: `"${row.term}" (${row.marker_class})`, source: row.source });
      }
      if (!noteOnly) for (const { re, row } of claimMarkers) {
        if (re.test(ing.text) && !hits.some((h) => h.detail === `"${row.term}" (${row.marker_class})`)) hits.push({ strength: "weak", marker_class: "claim_wording", detail: `"${row.term}" named only in claim wording ("source of" / "rich in" / "high in")`, source: "claim wording alone neither shows an added isolated ingredient nor shows it absent; abstains" });
      }
      if ((ing.name === "starch" || ing.name === "tapioca starch") && ing.inner && /modif|pregelatini[sz]ed|acid[- ]?treated|oxidi[sz]ed|cross[- ]?linked|bleached|hydroxypropyl|acetylated|phosphated|thermally|enzymatically/.test(ing.inner.toLowerCase())
          && !hits.some((h) => h.detail === '"modified starch" (derived_substance)')) {
        const mrow = T.markers.find((r) => r.term === "modified starch");
        if (mrow) hits.push({ strength: mrow.strength, marker_class: mrow.marker_class, detail: `"modified starch" (${mrow.marker_class})`, source: mrow.source });
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
    function namedWaterUnresolved(ing, sole=false) {
      const out=[], row=lookup(ing.name), raw=ing.raw.toLowerCase().replace(/^[ ,;:.]+|[ ,;:.]+$/g, "");
      if (row && row.kind === "named_water" && !(sole && ["carbonated water", "plain carbonated water"].includes(raw))) out.push(ing.raw);
      for (const part of rawBracketParts(ing.raw)) out.push(...namedWaterUnresolved(normaliseIngredient(part)));
      return out;
    }
    function plainJuiceStated(ing) {
      const row = lookup(ing.name);
      if (!row || row.kind !== "fruit_juice") return false;
      const term = row.term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      const quality = "(?:fresh|pasteuri[sz]ed)", pct = "100(?:\\.0+)?\\s*%";
      return new RegExp("^(?:" + pct + "\\s+" + quality + "|" + quality + "\\s+" + pct + ")\\s+" + term + "$").test(ing.raw.toLowerCase().replace(/^[ ,;:.]+|[ ,;:.]+$/g, ""));
    }
    function nestedJuiceUnresolved(ing) {
      const out = [];
      for (const part of rawBracketParts(ing.raw)) {
        const child = normaliseIngredient(part), row = lookup(child.name);
        if (row && row.kind === "fruit_juice") out.push(part + " (inside " + ing.raw + ")");
        out.push(...nestedJuiceUnresolved(child));
      }
      return out;
    }
    function classifyIngredients(ings, declarations) {
      const strong = [], weak = [];
      for (const ing of ings) for (const h of hitsFor(ing)) (h.strength === "strong" ? strong : weak).push({ ingredient: ing.raw, detail: h.detail, source: h.source, section: ing.section ?? null });
      for (const decl of declarations || []) {
        for (const clause of splitItemsText(decl.replace(/^contains?\s*:?[ ]*/i, ""))) {
          const ing = normaliseIngredient(clause);
          if (ing.ins.some((u) => u.class_conflict)) {
            weak.push({ingredient:clause, detail:"declared class and local code mapping differ; entry unresolved", source:"label wording versus existing project mapping; no source resolves this mismatch", section:null}); continue;
          }
          for (const h of hitsFor(ing)) {
            if (h.strength !== "strong") weak.push({ingredient:clause, detail:h.detail, source:h.source, section:null});
            else if (h.marker_class === "ins") weak.push({ingredient:clause, detail:"code stated outside ingredient list; verify declaration before using its mapped marker", source:h.source, section:null});
          }
          for (const { re, row } of markers)
            if (row.strength === "strong" && row.marker_class === "cosmetic_additive" && re.test(ing.text))
              strong.push({ingredient:decl,detail:`declared in "Contains" statement: "${row.term}"`,source:row.source,section:null});
        }
      }
      if (strong.length) return { group: 4, drivers: strong, reason: null };
      // A colour note on a named food leaves open whether a colour is added: without an independent marker (above) the result stays uncertain.
      const colourNotes = ings.filter(colourNoteOnly).map((i) => i.raw);
      if (colourNotes.length) return { group: null, drivers: weak, reason: `a colour note on a named ingredient (${colourNotes.join("; ")}) leaves open whether a colour is added, and no other marker decides the group${otherOpenItems(ings, new Set([...colourNotes, ...weak.map((d) => d.ingredient)]))}` };
      const sweetFoodEntries = ings.filter(sweetenerFoodsOnly).map((i) => i.raw);
      if (sweetFoodEntries.length) return { group: null, drivers: weak, reason: `a sweetener entry whose bracket names only foods (${sweetFoodEntries.join("; ")}) leaves open whether a sweetener additive is added, and no other marker decides the group${otherOpenItems(ings, new Set([...sweetFoodEntries, ...weak.map((d) => d.ingredient)]))}` };
      if (weak.length) {
        const names = [...new Set(weak.map((d) => `${d.ingredient} -> ${d.detail}`))].sort().join("; ");
        return { group: null, drivers: weak, reason: `only weak or unlisted markers present (${names}); not enough to call a group${otherOpenItems(ings, new Set(weak.map((d) => d.ingredient)))}` };
      }
      const unrecognised = ings.filter((i) => !isRecognised(i.name)).map((i) => i.raw);
      if (unrecognised.length) return { group: null, drivers: [], reason: "ingredients not in the local vocabulary, so processing level cannot be judged: " + unrecognised.join(", ") + otherOpenItems(ings, new Set(unrecognised)) };
      const bracketUnknown = ings.filter((i) => ((GUARDED_KINDS.includes(lookup(i.name).kind) || lookup(i.name).kind === "flour" || lookup(i.name).kind === "whole_food") && bracketResidual(i).length) || (lookup(i.name).kind === "culinary" && (fatBracketResidual(i).length || plainCulinaryResidual(i).length))).map((i) => [i.raw, lookup(i.name).kind === "culinary" ? (fatBracketResidual(i).length ? fatBracketResidual(i) : plainCulinaryResidual(i)) : bracketResidual(i), lookup(i.name).kind]);
      const wfCondition = ings.map((i) => [i.raw, wholeFoodObserved(i, lookup(i.name).kind)]).filter(([, o]) => o.length);
      const wfNested = ings.map((i) => [i.raw, wholeFoodNested(i, lookup(i.name).kind)]).filter(([, r]) => r.length);
      const kinds = ings.map((i) => (powderRouted(i, lookup(i.name).kind) ? "food_powder" : lookup(i.name).kind));
      const unplacedNames = ings.filter((i, n) => kinds[n] === "unplaced").map((i) => i.raw).concat(ings.flatMap(nestedUnplaced));
      if (unplacedNames.length) return { group: null, drivers: [], reason: "recognised by name only, and no source read places " + unplacedNames.join("; ") + ", so the processing level cannot be judged (recognition is vocabulary, not classification)" + otherOpenItems(ings, new Set(unplacedNames)) };
      const juices = ings.filter((i,n) => kinds[n] === "fruit_juice").map(i => i.raw), nestedJuices = ings.flatMap(nestedJuiceUnresolved);
      if (juices.length || nestedJuices.length) {
        if (ings.length === 1 && !nestedJuices.length && plainJuiceStated(ings[0])) return {group:1,drivers:[{ingredient:ings[0].raw,detail:"single explicitly 100% fresh or pasteurized fruit juice; FAO Table 1 Group 1 conditioned juice example",source:lookup(ings[0].name).source,section:ings[0].section ?? null}],reason:null};
        return {group:null,drivers:[],reason:"a named fruit juice (" + juices.concat(nestedJuices).join("; ") + "): FAO Group 1 covers fresh or pasteurized juice with no added sugar, sweeteners or flavours; the item's processing and composition are not established by this list, so no group is asserted"};
      }
      const waters = ings.flatMap(i => namedWaterUnresolved(i, ings.length === 1));
      if (waters.length) return {group:null,drivers:[],reason:"a named water's plain form or standalone scope is not established: " + waters.join("; ") + "; the source names plain or carbonated water as a dietary item, not treated forms or mixtures, so no group is asserted"};
      if (ings.length === 1 && kinds[0] === "named_water") return {group:1,drivers:[{ingredient:ings[0].raw,detail:"single plain carbonated water; exact-named Group 1 dietary-water example (Khandpur et al. 2021 Table 3)",source:lookup(ings[0].name).source,section:ings[0].section ?? null}],reason:null};
      const substantive = ings.map((i, n) => [i, kinds[n]]).filter(([, k]) => k !== "neutral" && k !== "culture");
      const kinds0 = ings.map((i) => lookup(i.name).kind);
      const cv = cannedFishVerdict(ings);
      if (cv) {
        if (cv[0] === 3) { const c0 = ings.find((i) => isCannedFishRow(lookup(i.name))); return { group: 3, drivers: [{ ingredient: c0.raw, detail: cv[1], source: lookup(c0.name).source, section: c0.section ?? null }], reason: null }; }
        return { group: null, drivers: [], reason: "a canned fish is named: " + cv[1] + ", so no group is asserted" };
      }
      const tv = tomatoConcVerdict(ings);
      if (tv) {
        if (tv[0] === 3) { const t0 = ings.find((i) => isTomatoConcRow(lookup(i.name))); return { group: 3, drivers: [{ ingredient: t0.raw, detail: tv[1], source: lookup(t0.name).source, section: t0.section ?? null }], reason: null }; }
        return { group: null, drivers: [], reason: "a tomato concentrate is named: " + tv[1] + ", so no group is asserted" };
      }
      const animalPowders = ings.filter((i, n) => animalPowder(i, kinds0[n])).map((i) => i.raw);
      const animalDry = ings.filter((i, n) => animalDried(i, kinds0[n])).map((i) => i.raw);
      const animalDryUnscoped = ings.filter((i, n) => animalDriedUnscoped(i, kinds0[n])).map((i) => i.raw);
      const nutSalted = animalDry.concat(ings.filter((i, n) => (kinds[n] === "nut_seed" && nutAddedSaltOrSugar(i)) || (GUARDED_KINDS.includes(kinds[n]) && legumeAddedSaltSugarOrBrine(i)) || grainAddedSalt(i, kinds[n])).map((i) => i.raw));
      const plainCul = new Map(ings.filter((i) => plainCulinaryResidual(i).length).map((i) => [i.raw, lookup(i.name).term]));
      if (bracketUnknown.length) return { group: null, drivers: [], reason: (bracketUnknown.some(([raw]) => plainCul.has(raw))
          ? (() => { const ts = new Set(bracketUnknown.filter(([raw]) => plainCul.has(raw)).map(([raw]) => plainCul.get(raw)));
              return ts.size === 1 && bracketUnknown.every(([raw]) => plainCul.has(raw)) ? "a bracket on " + [...ts][0] : "a bracket on a food item"; })()
          : (bracketUnknown.some(([, , k]) => k === "culinary")
          ? (bracketUnknown.every(([, , k]) => k === "culinary") ? "a bracket on a processed culinary ingredient" : "a bracket on a food item")
          : (bracketUnknown.every(([, , k]) => k !== "nut_seed") ? "a bracket on a legume, vegetable, fruit or flour item" : (bracketUnknown.every(([, , k]) => k === "nut_seed") ? "a bracket on a nut or seed item" : "a bracket on a food item"))))
        + (bracketUnknown.some(([raw]) => plainCul.has(raw)) ? " adds content beyond the plain food the source names (" : (bracketUnknown.some(([, , k]) => k === "culinary") ? " names content that is unrecognised or is a different food, not a culinary ingredient (" : " names content the vocabulary does not recognise (")) + bracketUnknown.map(([raw, r]) => raw + ": " + r.join(", ")).join("; ")
        + (bracketUnknown.some(([raw]) => plainCul.has(raw)) ? (() => { const ts = new Set(bracketUnknown.filter(([raw]) => plainCul.has(raw)).map(([raw]) => plainCul.get(raw)));
            return ts.size === 1 ? "), so the item is not established as plain " + [...ts][0] + " and no group is asserted" : "), so the items are not established as the plain foods the sources name and no group is asserted"; })()
          : (bracketUnknown.some(([, , k]) => k === "culinary") ? "), so what the item contains is not established and no group is asserted while part of the item is unassessed" : "), so neither Group 1 nor Group 3 is established while part of the item is unassessed")) };
      if (animalPowders.length) return { group: null, drivers: [], reason: "a powder of an animal food is named (" + animalPowders.join("; ") + "): no source read names powdered meat, poultry, fish or seafood, so its form and composition are not established and no group is asserted, whatever percentage the item states" };
      if (animalDryUnscoped.length) return { group: null, drivers: [], reason: "a dried form of an animal food is named (" + animalDryUnscoped.join("; ") + "): the FAO Group 3 example names dried meats and fish only, so whether a dried form of this food is processed that way is not established, and drying alone does not make it Group 1" };
      const fatPowders = ings.filter((i, n) => fatPowder(i, kinds[n])).map((i) => i.raw);
      if (fatPowders.length) return { group: null, drivers: [], reason: "a powder of an oil or fat is named (" + fatPowders.join("; ") + "): a powder is named but its composition is not established, so no group is asserted unless the item's own name states 100%" };
      if (wfNested.length) return { group: null, drivers: [], reason: "a bracket names a different food inside the item (" + wfNested.map(([raw, r]) => raw + ": " + r.join(", ")).join("; ") + "): no rule or source available here establishes that it is the same food or how the two combine, so what the item is made of is not established and neither Group 1 nor Group 3 is asserted" };
      if (wfCondition.length) return { group: null, drivers: [], reason: "an item whose own text names an added or preserving condition (" + wfCondition.map(([raw, o]) => raw + ": " + o.join(", ")).join("; ") + "): the general Group 3 definition covers group 1 foods with salt, oil, sugar or other group 2 ingredients added, but this food's form and composition are not established by the label evidence and the rules available, so neither Group 1 nor Group 3 is asserted" };
      const nestedPowders = ings.flatMap(nestedPowderUnresolved);
      if (nestedPowders.length) return { group: null, drivers: [], reason: "a nested powder's form or composition is not established (" + nestedPowders.join("; ") + "), so it cannot inherit the outer food's plain placement and no group is asserted" };
      const cheeseNames = ings.filter((i, n) => kinds[n] === "whole_food" && isCheeseRow(lookup(i.name))).map((i) => i.raw);
      if (cheeseNames.length) {
        if (ings.length === 1 && !ings[0].inner && !addedIn(ings[0], CHEESE_ABSTAIN))
          return { group: 3, drivers: [{ ingredient: ings[0].raw, detail: "cheese (Brazil Dietary Guidelines Group 3: 'cheeses'; FAO Table 1 Group 3: 'simple cheeses to which salt is added'); a sole plain cheese item", source: lookup(ings[0].name).source, section: ings[0].section ?? null }], reason: null };
        return { group: null, drivers: [], reason: "a cheese is named (" + cheeseNames.join("; ") + ") inside a longer list, with a bracket, or with a stated form (powder, processed, smoked, spread, sauce, flavoured, grated, sliced): no source read here places that form or combination, so no group is asserted" };
      }
      const yoghurtNames = ings.filter((i, n) => kinds[n] === "whole_food" && isYoghurtRow(lookup(i.name))).map((i) => i.raw);
      if (yoghurtNames.length) {
        if (ings.length === 1 && !ings[0].inner && !addedIn(ings[0], YOGHURT_ABSTAIN))
          return { group: 1, drivers: [{ ingredient: ings[0].raw, detail: "plain yoghurt (FAO Table 1 Group 1: 'fresh or pasteurized plain yoghurt'); a sole plain item, identity FSSAI Chapter 2.1 and USDA FDC SR Legacy", source: lookup(ings[0].name).source, section: ings[0].section ?? null }], reason: null };
        return { group: null, drivers: [], reason: "yoghurt is named (" + yoghurtNames.join("; ") + ") inside a longer list, with a bracket, or with a stated form (sweetened, flavoured, fruit, frozen, drinking, powder): the FAO clause names only plain yoghurt, so no group is asserted" };
      }
      const smokedFishNames = ings.filter((i, n) => kinds[n] === "whole_food" && isSmokedFishRow(lookup(i.name))).map((i) => i.raw);
      if (smokedFishNames.length) {
        if (ings.length === 1 && !ings[0].inner && !addedIn(ings[0], SMOKED_FISH_ABSTAIN))
          return { group: 3, drivers: [{ ingredient: ings[0].raw, detail: "smoked fish (FAO Table 1 Group 3 prose: 'processed animal foods such as ham, bacon, pastrami, and smoked fish'); a sole plain item, identity USDA FDC SR Legacy", source: lookup(ings[0].name).source, section: ings[0].section ?? null }], reason: null };
        return { group: null, drivers: [], reason: "a smoked fish is named (" + smokedFishNames.join("; ") + ") inside a longer list, with a bracket, or with a stated form (canned, salted, pate, spread, powder, flavoured): no source read here places that form or combination, so no group is asserted" };
      }
      const curedNames = ings.filter((i, n) => kinds[n] === "whole_food" && isCuredMeatRow(lookup(i.name))).map((i) => i.raw);
      if (curedNames.length) {
        if (ings.length === 1 && !ings[0].inner && !addedIn(ings[0], CURED_ABSTAIN))
          return { group: 3, drivers: [{ ingredient: ings[0].raw, detail: "cured meat (FAO Table 1 Group 3 prose: 'processed animal foods such as ham, bacon, pastrami'); a sole plain item, identity USDA FDC SR Legacy", source: lookup(ings[0].name).source, section: ings[0].section ?? null }], reason: null };
        return { group: null, drivers: [], reason: "a cured meat is named (" + curedNames.join("; ") + ") inside a longer list, with a bracket, or with a stated form or other-species word: no source read here places that form or combination, so no group is asserted" };
      }
      const legumePreserved = ings.filter((i, n) => GUARDED_KINDS.includes(kinds[n]) && legumePreservedForm(i) && !legumeAddedSaltSugarOrBrine(i)).map((i) => i.raw);
      if (legumePreserved.length) {
        const preservedNut = ings.map((i, n) => [i, kinds[n]]).filter(([i, k]) => GUARDED_KINDS.includes(k) && legumePreservedForm(i) && !legumeAddedSaltSugarOrBrine(i)).map(([, k]) => k === "nut_seed");
        if (!preservedNut.some(Boolean)) return { group: null, drivers: [], reason: "a canned, bottled or preserved legume, vegetable or fruit (" + legumePreserved.join("; ") + "): FAO Group 3 names vegetables and legumes preserved in brine and fruit in syrup, but the item does not say that salt, sugar, syrup or brine is added, so neither Group 1 nor Group 3 is established" };
        return { group: null, drivers: [], reason: "a canned, bottled or preserved " + (preservedNut.every(Boolean) ? "nut or seed" : "food") + " (" + legumePreserved.join("; ") + "): the FAO Group 3 definition covers group 1 foods with salt, oil, sugar or other group 2 ingredients added, using preservation methods such as canning and bottling, but the item does not say that any such substance is added, so added substances are not established and neither Group 1 nor Group 3 is established" };
      }
      if (ings.length === 1 && (kinds[0] === "nut_seed" || BRINE_KINDS.includes(kinds[0])))
        return nutSalted.length
          ? { group: 3, drivers: [{ ingredient: ings[0].raw, detail: kinds[0] === "nut_seed" ? nutGroup3Driver(ings[0]) : kinds[0] === "fruit" ? "fruit with added sugar, syrup or salt (FAO Group 3: 'whole fruit preserved in syrup'; definition: adding salt or sugar to group 1 foods)" : kinds[0] + " with added salt, sugar or brine (FAO Group 3: 'canned or bottled vegetables or legumes (pulses) preserved in brine'; definition: adding salt or sugar to group 1 foods)", source: lookup(ings[0].name).source, section: ings[0].section ?? null }], reason: null }
          : { group: 1, drivers: [{ ingredient: ings[0].raw, detail: "single recognised unprocessed food", source: lookup(ings[0].name).source, section: ings[0].section ?? null }], reason: null };
      if (ings.length === 1 && animalDry.length)
        return { group: 3, drivers: [{ ingredient: ings[0].raw, detail: "dried meat, poultry, fish or seafood (FAO Table 1 Group 3 example: 'salted, dried, cured, or smoked meats and fish'); class-instance of that example", source: lookup(ings[0].name).source, section: ings[0].section ?? null }], reason: null };
      if (ings.length === 1 && (kinds[0] === "whole_food" || kinds[0] === "flour") && nutSalted.length)
        return { group: 3, drivers: [{ ingredient: ings[0].raw, detail: "grain or grain flour with added salt (FAO: group 1 foods with salt added are classed in NOVA group 3 as processed foods; inference: no clause names a salted grain)", source: lookup(ings[0].name).source, section: ings[0].section ?? null }], reason: null };
      if (ings.length === 1 && (kinds[0] === "whole_food" || kinds[0] === "flour"))
        return { group: 1, drivers: [{ ingredient: ings[0].raw, detail: milkPowderNamed(ings[0]) ? "powdered milk (FAO Table 1 Group 1: 'fresh, powdered or pasteurized milk')" : "single recognised unprocessed food", source: lookup(ings[0].name).source, section: ings[0].section ?? null }], reason: null };
      if (ings.length === 1 && kinds[0] === "food_powder" && powderCompositionStated(ings[0]))
        return { group: 1, drivers: [{ ingredient: ings[0].raw, detail: "single recognised powder of one food whose own text states whole-food composition ('100%' or 'whole'); nothing else listed", source: lookup(ings[0].name).source, section: ings[0].section ?? null }], reason: null };
      if (ings.length === 1 && kinds[0] === "culinary")
        return { group: 2, drivers: [{ ingredient: ings[0].raw, detail: "single processed culinary ingredient", source: lookup(ings[0].name).source, section: ings[0].section ?? null }], reason: null };
      const rows = ings.map((i) => lookup(i.name));
      if (rows.some((r) => r.kind === "culture") && rows.some((r) => MILK_TERMS.includes(r.term)) && rows.every((r) => r.kind === "culture" || MILK_TERMS.includes(r.term)))
        // Narrow rule (research/04): the WHOLE list is recognised and is only milk plus starter culture(s). Not keyed off product words.
        return { group: 1, drivers: ings.map((i) => ({ ingredient: i.raw, detail: "milk fermented with a starter culture, nothing else listed (NUPENS-USP: plain yoghurt with no added sugar or artificial sweeteners; fermentation of milk to make yoghurt)", source: "NUPENS-USP classification page (research/04)", section: i.section ?? null })), reason: null };
      const powders = ings.filter((i, n) => kinds[n] === "food_powder").map((i) => i.raw);
      if (powders.length) return { group: null, drivers: [], reason: "a powder of a food (" + powders.join("; ") + ") is named without its composition: the label does not say whether it is that food alone or carries carriers or anti-caking agents, so the level cannot be judged" + otherOpenItems(ings, new Set(powders)) };
      if (kinds.includes("flour")) return { group: null, drivers: [], reason: "flour-based list: bakery-fresh versus industrial formulation cannot be told from the ingredient list" };
      const hasFood = substantive.some(([, k]) => k === "whole_food" || k === "nut_seed" || k === "legume" || k === "vegetable" || k === "fruit");
      const hasCulinary = substantive.some(([, k]) => k === "culinary") || nutSalted.length > 0;
      if (hasFood && hasCulinary)
        return { group: 3, drivers: substantive.map(([i, k]) => ({ ingredient: i.raw, detail: "recognised " + (k === "nut_seed" || BRINE_KINDS.includes(k) ? "whole food" : k.replace(/_/g, " ")), source: lookup(i.name).source, section: i.section ?? null })), reason: null };
      return { group: null, drivers: [], reason: "recognised ingredients, but the combination does not match a group 1, 2 or 3 pattern" };
    }

    /* ---------- pipeline ---------- */
    const NOT_ENOUGH = "Not enough information";
    const GROUP_NAMES = { 1: "unprocessed or minimally processed foods", 2: "processed culinary ingredients", 3: "processed foods", 4: "ultra-processed foods" };
    const MIN_CHARS = 20, MIN_ALPHA_RATIO = 0.5;

    function abstain(reason, text, extra) {
      return Object.assign({ answered: false, group: null, reason, ingredients: [], drivers: [], ins: [], warnings: [], sections: [], unassessed: [], unplaced: [], ignored: [], declared: [], heading: { kind: "none", text: "" }, completeness: { status: "uncertain", heading: "none", reasons: ["no ingredient list was read"], list_share: 0.0, words: { region: 0, in_list: 0, declared: 0, excluded: 0, not_read: 0, unaccounted: 0 }, assessed: { items: 0, not_assessed: 0 } }, text }, extra || {}, { headline: `${NOT_ENOUGH}: ${reason}` });
    }
    const recognisableIng = (ing) => isRecognised(ing.name) || ing.ins.length > 0 || hitsFor(ing).length > 0;
    // words and phrases of the vocabulary tables, for telling a cut-off fragment from an unknown whole word (mirrors pipeline._looks_cut_off)
    const vocabWords = new Set(), vocabPhrases = new Set();
    for (const [tbl, cols] of [[T.lexicon, ["term"]], [T.synonyms, ["from", "to"]], [T.markers, ["term"]], [T.descriptors, ["word"]]])
      for (const r of tbl) for (const c of cols) { const t = String(r[c] || "").toLowerCase(), ws = t.match(/[a-z]+/g) || []; ws.forEach((w) => vocabWords.add(w)); vocabPhrases.add(ws.join(" ")); }
    const vocabList = [...vocabWords], phraseList = [...vocabPhrases];
    function looksCutOff(ing) {
      const toks = ing.name.toLowerCase().match(/[a-z]+/g) || [];
      if (!toks.length) return false;
      const last = toks[toks.length - 1];
      if (last.length >= 3 && !vocabWords.has(last) && vocabList.some((w) => w.startsWith(last))) return true;
      for (let k = 0; k < toks.length; k++)      // drop leading descriptor words one at a time: "pasteurized toned" -> "toned" is the start of "toned milk"
        if ((k === 0 || allDescriptorWords.has(toks[k - 1])) && phraseList.some((p) => p.startsWith(toks.slice(k).join(" ") + " "))) return true;
      return false;
    }
    // mirrors pipeline._split_amp_pair: an '&'- or 'and'-joined pair inside a bracket splits only when each side is recognised WITH its shared modifier; the shared percentage is a note, not copied onto the items
    function splitAmpPair(raw) {
      const [parts, connectors] = splitTopLevelAndEx(raw);
      if (parts.length !== 2 || connectors.length !== 1) return [[raw], []];
      const conn = connectors[0];
      const connLower = conn.toLowerCase();
      if (connLower !== "&" && connLower !== "and") return [[raw], []];
      if (sharedCodeList(parts)) return [[raw], []];
      const left = parts[0]; let right = parts[1], pct = null;
      const m = /^(.*?)\s*\(\s*(\d+(?:\.\d+)?\s*%)\s*\)$/s.exec(right);
      if (m) { right = m[1].trim(); pct = m[2].replace(/\s+/g, ""); }
      if (!left || !right || /[(\[{)\]}]/.test(left + right)) return [[raw], []];
      const toks = left.split(/\s+/).filter(Boolean);
      let mod = "";
      for (let k = 1; k < toks.length; k++) {
        if (recognisableIng(normaliseIngredient(toks.slice(k).join(" ")))) { mod = toks.slice(0, k).join(" "); break; }
      }
      const rightFull = mod && !right.toLowerCase().startsWith(mod.toLowerCase() + " ") ? `${mod} ${right}` : right;
      if (!(recognisableIng(normaliseIngredient(left)) && recognisableIng(normaliseIngredient(rightFull)))) return [[raw], []];
      if (namesTwoOils([left, rightFull])) return [[raw], []];
      const notes = [];
      if (mod) notes.push(`"${mod}" was read as shared by both sides of "${left} ${conn} ${right}"`);
      if (pct) notes.push(`The ${pct} after "${left} ${conn} ${right}" applies to the pair, not to each item separately`);
      return [[left, rightFull], notes];
    }
    function expand(items, depth, heads, notes) {   // items: [raw, section label] pairs
      const out = [];
      for (const [raw, section] of items) {
        const ing = normaliseIngredient(raw);
        ing.section = section;
        ing.ins.forEach((u) => { u.section = section; });
        let split = depth < 3 && !isAdditiveAbsenceClaim(raw) ? splitCompound(raw) : null;
        if (split && split[1].length === 1 && isColourNote(normaliseIngredient(split[1][0]).text)) split = null;   // "Annatto (colour)": a function note on a named food
        if (split && !recognisableIng(normaliseIngredient(split[0]))) {
          if (heads) heads.push(split[0]);       // the group name itself is not classified: keep it visible
          const subs = [];
          for (const sub of split[1]) { const [pieces, pairNotes] = splitAmpPair(sub); subs.push(...pieces); if (notes) for (const n of pairNotes) if (!notes.includes(n)) notes.push(n); }
          out.push(...expand(subs.map((sub) => [sub, section]), depth + 1, heads, notes));
        }
        else out.push(ing);
      }
      return out;
    }
    const splitItemsText = (t) => splitTopLevel(collapse(t)).items;
    const markerTerms = (text) => new Set(markers.filter(({ re }) => re.test(text)).map(({ row }) => row.term));
    const ingredientMarkerTerms = (ing) => {
      if (colourNoteOnly(ing)) return new Set();
      const terms = markerTerms(ing.text);
      if (sweetenerFoodsOnly(ing)) terms.delete("sweetener");
      return terms;
    };
    const subset = (a, b) => [...a].every((x) => b.has(x));
    // "emulsifier [472e] and flour treatment agent [1101(ii)]" -> two items, only when EVERY side is recognisable
    const CODE_ONLY = /^\s*(?:(?:ins|e)\s*[-:.]?\s*)?\d{3,4}[a-z]?(?:\([ivxl]+\))*(?:\s*(?:,|;|and|&|\/)\s*(?:(?:ins|e)\s*[-:.]?\s*)?\d{3,4}[a-z]?(?:\([ivxl]+\))*)*\s*$/i;
    function sharedCodeList(parts) {     // "emulsifiers and stabilizers [INS 460(i), INS 471]": one code list for both classes; not split
      const last = parts[parts.length - 1].trimEnd();
      if (parts.length < 2 || !last || !")]}".includes(last[last.length - 1]) || parts.slice(0, -1).some((p) => /[(\[{]/.test(p))) return false;
      if (parts.slice(0, -1).some((p) => /flavou?r/i.test(p))) return false;       // flavourings have no INS numbers (CXG 36 introduction)
      let depth = 0;
      for (let i = last.length - 1; i >= 0; i--) {
        if (")]}".includes(last[i])) depth++;
        if ("([{".includes(last[i])) depth--;
        if (depth === 0) return CODE_ONLY.test(last.slice(i + 1, -1));
      }
      return false;
    }
    function endsInCodeBracket(part) {   // "dough conditioner (223)": a bracket holding only additive codes marks an additive item
      const s = part.trimEnd();
      if (!s || !")]}".includes(s[s.length - 1])) return false;
      let depth = 0;
      for (let i = s.length - 1; i >= 0; i--) {
        if (")]}".includes(s[i])) depth++;
        if ("([{".includes(s[i])) depth--;
        if (depth === 0) return i > 0 && CODE_ONLY.test(s.slice(i + 1, -1));
      }
      return false;
    }
    function splitPairsEx(raw) {
      const [parts, connectors] = splitTopLevelAndEx(raw);
      if (parts.length > 1 && !sharedCodeList(parts) && parts.every((p) => recognisableIng(normaliseIngredient(p)) || endsInCodeBracket(p)))
        return namesTwoOils(parts) ? [[raw], 0] : [parts, connectors.reduce((n, c) => n + countWords(c), 0)];     // culinary-guard-1: 'Corn and Canola Oil' names two oils, kept whole
      return [[raw], 0];
    }
    function namesTwoOils(parts) {
      if (parts.length !== 2) return false;
      const first = normaliseIngredient(parts[0]), second = normaliseIngredient(parts[1]);
      if (!isFatRow(lookup(second.name)) || !lookup(first.name) || lookup(first.name).kind === "culinary") return false;
      return ["oil", "fat"].some((w) => isFatRow(lookup(first.name + " " + w)));
    }
    const splitPairs = (raw) => splitPairsEx(raw)[0];
    const unclosedOpeners = (text) => {
      const stack = [];
      for (let i = 0; i < text.length; i++) { if (OPEN.includes(text[i])) stack.push(i); else if (CLOSE.includes(text[i]) && stack.length) stack.pop(); }
      return stack.map((i) => text.slice(Math.max(0, i - 15), i + 45).replace(/\s+/g, " ").trim());
    };
    // additive/flavour clauses of the "Contains ..." lines, marked as in or missing from the list; allergens are dropped
    function declaredAdditives(declarations, ings) {
      const listTerms = new Set(); const listCodes = new Set();
      for (const i of ings) { ingredientMarkerTerms(i).forEach((t) => listTerms.add(t)); i.ins.forEach((u) => listCodes.add(u.code)); }
      const out = [];
      for (const decl of declarations) {
        const body = decl.replace(/^contains\s*:?\s*/i, "");
        for (const part of splitItemsText(body)) for (const clause of splitTopLevelAnd(part)) {
          const ing = normaliseIngredient(clause);
          const terms = markerTerms(ing.text), codes = new Set(ing.ins.map((u) => u.code));
          if (!terms.size && !codes.size) continue;
          const entry = { text: stripChars(clause, " ."), in_list: subset(terms, listTerms) && subset(codes, listCodes) };
          if (!out.some((e) => e.text === entry.text && e.in_list === entry.in_list)) out.push(entry);
        }
      }
      return out;
    }
    const shortText = (t, limit = 100) => (t.length <= limit ? t : t.slice(0, limit - 3) + "...");
    const startsWithDeniedLabel = (seg) => { const m = LABEL.exec(seg); return !!m && DENY.test(m[1].trim()); };
    // unread text after a full stop that could be the rest of the list (mirrors pipeline._looks_like_more_ingredients)
    function looksLikeMoreIngredients(seg) {
      if (/^\s*[*\u2020#]/.test(seg) || startsWithDeniedLabel(seg)) return false;
      if (/\bcultures?\b/i.test(seg)) return true;  // unread ingredient-like token, never a role/placement mapping
      const parts = splitTopLevel(collapse(seg)).items;
      return parts.length >= 2 || parts.some((part) => recognisableIng(normaliseIngredient(part)));
    }
    const NUTRITION = ["kcal", "energy", "carbohydrate", "per 100", "serving size", "cholesterol", "nutrition", "rda", "calories", "total fat", "trans fat"];
    const MARKETING = ["buy", "offer", "free", "mrp", "enjoy", "tasty", "crunchy", "delicious", "limited", "new!", "gift", "price", "taste", "extra"];
    const RETAKE = 'retake the photo with the ingredient panel (and its "Ingredients" heading) in frame';
    // no heading: the most plausible ingredient block, never a nutrition table, marketing copy or allergen statement (see pipeline._infer_block)
    function outsideBrackets(s) {      // the item without its bracketed contents: a long sub-list is not a long item
      let prev = null;
      while (prev !== s) { prev = s; s = s.replace(/[(\[{][^(\[{)\]}]*[)\]}]/g, ""); }
      return s;
    }
    function inferBlock(text) {
      let best = null, bestScore = 0;
      for (const block of text.replace(/\r\n/g, "\n").split(/\n\s*\n/)) {
        const flat = block.replace(/\s+/g, " ").trim(), low = flat.toLowerCase();
        if (!flat || /^(?:(?:may\s+)?contains?\b|allerg)/.test(low)) continue;
        if (NUTRITION.filter((k) => low.includes(k)).length >= 2 || MARKETING.filter((k) => low.includes(k)).length >= 2) continue;
        const parts = splitItemsText(flat);
        if (parts.length < 4 || parts.reduce((n, x) => n + outsideBrackets(x).split(/\s+/).filter(Boolean).length, 0) / parts.length > 6) continue;
        const ings = parts.map(normaliseIngredient);
        const recognised = ings.filter(recognisableIng).length;
        const marked = ings.filter((i) => i.ins.length > 0 || hitsFor(i).length > 0).length;
        const score = recognised + 2 * marked;
        if (recognised / parts.length >= 0.4 && score >= 3 && score > bestScore) { best = flat; bestScore = score; }
      }
      return best;
    }
    const NO_TEXT = "No text to analyse", NO_INGREDIENTS = "No ingredients found in this text";
    // source "ocr" (default, photo path): short/noisy text is blamed on OCR and the heading is required.
    // source "text" (typed or pasted): no length gate, a heading-less text is the list, messages are about the text.
    const SUSPECT_PCT = /\(\s*\d+(?:\.\d+)?\s*%\s*\)\s+(?!and\b|or\b|with\b|of\b|in\b|&|\(|\[|\{)[A-Za-z]/i;
    function roleNotes(ings) {      // a role phrase read as its class word is a PROVISIONAL mapping: keep that visible
      const out = [];
      for (const i of ings) {
        const low = i.raw.toLowerCase();
        for (const r of T.synonyms) {
          if (r.source.startsWith("PROVISIONAL role phrase") && new RegExp("(?<![a-z])" + r.from.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "(?![a-z])").test(low)) {
            out.push(`"${shortText(i.raw)}": "${r.from}" is read as the ${r.to.split(" & ")[0]} class by a provisional mapping (no source names the phrase)`);
            break;
          }
        }
      }
      return out;
    }
    function isImplausible(ings) {   // few recognised items and no additive code or marker at all (photo path)
      if (!ings.length) return false;
      if (ings.some((i) => i.ins.length > 0 || hitsFor(i).length > 0)) return false;
      return ings.filter(recognisableIng).length / ings.length < 1 / 3;
    }
    // REVIEW HINTS ONLY (see pipeline._possible_misreads): a code is never replaced and no alternative is used in classification.
    function possibleMisreads(ings) {
      const out = [], seen = new Set();
      for (const ing of ings) {
        if (!ing.ins.length) continue;
        const head = (ing.raw.split(/[\[({]/, 1)[0].replace(/^[ ,;:*-]+|[ ,;:*-]+$/g, "")) || ing.raw;
        const codes = new Set(ing.ins.map((u) => u.code));
        for (const u of ing.ins) {
          const key = ing.raw + "|" + u.code; if (seen.has(key)) continue;
          const tied = Object.keys(insRef).find((c) => insRef[c].name.length >= 5 && ing.name.includes(insRef[c].name.toLowerCase()) && !codes.has(c));
          if (tied) {
            seen.add(key);
            const url = /https?:\/\/\S+/.exec(insRef[tied].source || "");
            out.push(`Read as INS ${u.code}. The label text says ${head}, and the source page for ${insRef[tied].name.toLowerCase()} gives INS ${tied}${url ? " (" + url[0] + ")" : ""}. Possible misread, check the pack.`);
            continue;
          }
        }
      }
      return out;
    }
    const PROVENANCE = /^made\s+(?:from|with|using)\s+(.+)$/i;
    function stripProvenance(parsed) {     // see pipeline._strip_provenance
      let words = 0;
      for (const sec of parsed.sections) {
        while (sec.items.length > 1) {
          const m = PROVENANCE.exec(sec.items[sec.items.length - 1]);
          const row = m ? lookup(normaliseIngredient(m[1]).name) : null;
          if (!row || !MILK_TERMS.includes(row.term)) break;
          words += countWords(sec.items.pop());
        }
      }
      parsed.items = parsed.sections.flatMap((sec) => sec.items);
      return words;
    }
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
        if (chars.length < MIN_CHARS) return abstain("OCR produced little text; retake the photo closer and in focus", text);
        if (alphaShare() < MIN_ALPHA_RATIO) return abstain("extracted text looks like noise, not a readable label; retake a clearer photo", text);
        parsed = parseIngredientList(text);
        if (!parsed.found) {
          const block = inferBlock(text);
          parsed = block ? parseIngredientList(block, { assumeList: true }) : null;
          if (!parsed || !parsed.found) return abstain(`no ingredient list found in the text; ${RETAKE}`, text);
          parsed.headingKind = "inferred";
        }
      }
      const provenanceWords = stripProvenance(parsed);
      let joiners = 0;
      const sections = parsed.sections.map((sec) => ({ label: sec.label, items: sec.items.flatMap((raw) => {
        const [parts, j] = splitPairsEx(raw);
        joiners += j;          // only the joiner words; any other word a split dropped stays "unaccounted"
        return parts;
      }) }));
      const items = sections.flatMap((sec) => sec.items);
      const heads = [];
      const ampNotes = [];
      const ings = expand(sections.flatMap((sec) => sec.items.map((raw) => [raw, sec.label])), 0, heads, ampNotes);
      const declared = declaredAdditives(parsed.declarations, ings);
      const unassessed = [...new Set([
        ...ings.filter((i) => !recognisableIng(i)).map((i) => i.raw),
        ...heads.map((h) => `${h} (group name; its contents were assessed separately)`)])];
      const unplaced = [...new Set(ings.filter((i) => { const l = lookup(i.name); return l && l.kind === "unplaced"; }).map((i) => i.raw).concat(ings.flatMap(nestedUnplaced),ings.filter(i => lookup(i.name)?.kind === "fruit_juice" && !(ings.length === 1 && plainJuiceStated(i))).map(i => i.raw),ings.flatMap(nestedJuiceUnresolved),ings.flatMap(i => namedWaterUnresolved(i, ings.length === 1))))];
      const declarationEvidence = parsed.declarations.flatMap((d) => splitItemsText(d.replace(/^contains?\s*:?[ ]*/i, "")).map(normaliseIngredient)).filter((i) => i.ins.length || hitsFor(i).length);
      const sectionWarnings = suspectSectionItems(items).map((it) => `"${it}" contains a colon, so a section label may not have been split from the ingredient before it`).concat(ampNotes);
      sectionWarnings.push(...parsed.composition.map((seg) => `Milk composition declaration (not an added ingredient): "${seg}". No vitamin, added-solid or milk-fat ingredient was inferred.`));
      const unreadLike = parsed.ignored.filter(looksLikeMoreIngredients);
      sectionWarnings.push(...unreadLike.map((seg) => `Text after a full stop was not read as ingredients but looks like more of the list: "${shortText(seg)}"`));
      sectionWarnings.push(...ings.filter(colourNoteOnly).map((i) => `"${i.raw}": a colour note on a named ingredient is not counted as an added colour`));
      sectionWarnings.push(...ings.filter(sweetenerFoodsOnly).map((i) => `"${i.raw}": the bracket names foods, so the word "sweeteners" is not counted as an added sweetener class`));
      sectionWarnings.push(...ings.filter((i) => isAdditiveAbsenceClaim(i.raw)).map((i) => `"${i.raw}": additive-absence wording is not treated as a positive ingredient or code declaration; the entry stays unresolved`));
      sectionWarnings.push(...ings.concat(declarationEvidence).filter((i) => i.ins.some((u) => u.class_conflict)).map((i) => `"${i.raw}": declared class and local code mapping differ; codes remain visible, but marker evidence from this entry is not used`));
      sectionWarnings.push(...roleNotes(ings));
      const pctSuspects = items.filter((it) => SUSPECT_PCT.test(it));
      sectionWarnings.push(...pctSuspects.map((it) => `"${shortText(it)}" has text after a percentage; a comma may be missing between two ingredients`));
      const boundarySuspects = suspectAdjacentClassItems(items);
      sectionWarnings.push(...boundarySuspects.map(it => `"${shortText(it)}": an additive-class bracket follows a closed food bracket without a separator; the ingredient boundary may be missing. The original item is kept unchanged.`));
      const implausible = source === "ocr" && isImplausible(ings);
      if (implausible) sectionWarnings.push("Few of the items were recognised, so this text may not be the ingredient list");
      sectionWarnings.push(...possibleMisreads(ings));
      if (parsed.unbalanced) sectionWarnings.push(...items.flatMap((it) => unclosedOpeners(it)).map((snip) => `A bracket near "${snip}" was never closed, so the text after it was kept together as one item instead of being split (where it should close cannot be known)`));
      const common = { ingredients: items, ins: ings.flatMap((i) => i.ins).concat(declarationEvidence.flatMap((i) => i.ins.map((u) => ({...u,declaration_only:true})))), warnings: [...sectionWarnings], unassessed, unplaced, ignored: [...parsed.ignored], declared, heading: { kind: parsed.headingKind, text: parsed.headingText }, sections: sections.map((sec) => [sec.label, sec.items]) };
      let truncation = null, vocabLast = false;      // vocabLast: the last item is not in the vocabulary but does not look cut off (a vocabulary gap, not a truncation)
      if (parsed.unbalanced) truncation = "ingredient list looks truncated (unclosed bracket)";
      else if (!parsed.terminated && !recognisableIng(ings[ings.length - 1])) {
        if (looksCutOff(ings[ings.length - 1])) truncation = `ingredient list looks truncated (ends mid-word: "${items[items.length - 1]}")`;
        else vocabLast = true;
      }
      // unlabelled text after a full stop that looks like more of the list: like truncation, only a strong-marker Group 4 stands
      const unread = unreadLike.length ? `text after a full stop looks like more ingredients and was not read: "${shortText(unreadLike[0])}"` : null;
      let headingRisk = null;
      if (source === "ocr" && parsed.headingKind === "fuzzy")
        headingRisk = `the "Ingredients" heading was read as "${parsed.headingText}" (the photo may be cut off at the left edge), so the start of the list may be missing; ${RETAKE}`;
      else if (source === "ocr" && parsed.headingKind === "inferred")
        headingRisk = `no "Ingredients" heading was found, so the text block used may not be the ingredient list; ${RETAKE}`;
      const inList = sections.reduce((n, sec) => n + countWords(sec.label || "") + sec.items.reduce((m, x) => m + countWords(x), 0), 0) + joiners;
      const notRead = parsed.ignored.reduce((n, x) => n + countWords(x), 0);
      const declaredW = parsed.declarations.reduce((n, x) => n + countWords(x), 0);
      const unaccounted = Math.max(0, parsed.keptWords - inList - notRead - provenanceWords);
      const reasons = [];
      if (source === "ocr" && parsed.headingKind === "fuzzy") reasons.push(`the heading was read as "${parsed.headingText}": the photo may be cut off at the left edge`);
      if (source === "ocr" && parsed.headingKind === "inferred") reasons.push('no "Ingredients" heading was found: the most list-like text block was used');
      if (parsed.unbalanced) reasons.push("brackets are not balanced: text may be cut off or misread");
      if (truncation) reasons.push("the list looks truncated");
      else if (vocabLast) reasons.push("the last item is not in the local vocabulary");
      if (unreadLike.length) reasons.push("text after a full stop looks like more ingredients and was not read");
      if (unaccounted) reasons.push(`${unaccounted} word(s) after the heading were neither read as ingredients nor set aside`);
      if (suspectSectionItems(items).length) reasons.push("a section label may not have been split from an ingredient");
      if (pctSuspects.length) reasons.push("an item has text after a percentage: a comma may be missing between two ingredients");
      if (boundarySuspects.length) reasons.push("an additive-class bracket follows a closed food bracket without a separator: ingredient-item boundaries are uncertain, even though the words are accounted for");
      if (implausible) reasons.push("few of the items were recognised: this text may not be an ingredient list");
      const denom = inList + notRead + unaccounted;
      common.completeness = {
        status: reasons.length ? "uncertain" : "complete", heading: parsed.headingKind, reasons,
        list_share: denom ? Math.round(inList / denom * 1000) / 1000 : 0.0,
        words: { region: parsed.regionWords, in_list: inList, declared: declaredW, excluded: Math.max(0, parsed.tailWords - declaredW) + provenanceWords, not_read: notRead, unaccounted },
        assessed: { items: ings.length, not_assessed: ings.filter((i) => { const l = lookup(i.name); return !recognisableIng(i) || i.ins.some((u) => u.class_conflict) || (l && l.kind === "unplaced") || nestedUnplaced(i).length > 0 || (l && l.kind === "fruit_juice" && !(ings.length === 1 && plainJuiceStated(i))) || nestedJuiceUnresolved(i).length > 0 || namedWaterUnresolved(i, ings.length === 1).length > 0; }).length } };
      if (parsed.composition.length) {
        const compositionWords = parsed.composition.reduce((n, x) => n + countWords(x), 0);
        common.completeness.words.composition = compositionWords; common.completeness.words.excluded -= compositionWords;
        sectionWarnings.push("Existing milk mappings may be PROVISIONAL: NOVA names milk, not each species or standardised class. The composition note supplies no new placement evidence; see full source evidence.");
        common.warnings = [...sectionWarnings];
      }
      const lost = unaccounted ? `${unaccounted} word(s) after the heading were neither read nor set aside, so text may have been lost` : null;
      const blocking = truncation || unread || headingRisk || lost;
      const r = classifyIngredients(ings, parsed.declarations);
      // Option A (user decision): a strong-marker Group 4 call stands on a possibly incomplete list, with a warning.
      if (blocking && r.group !== 4) return abstain(blocking, text, Object.assign({ drivers: r.drivers }, common));
      if (r.group === null) return abstain(r.reason || "classification uncertain", text, Object.assign({ drivers: r.drivers }, common));
      const warnings = [...sectionWarnings];
      if (headingRisk) warnings.push(headingRisk[0].toUpperCase() + headingRisk.slice(1).split("; retake")[0] + ". Group 4 stands because the markers found are already enough.");
      if (truncation) warnings.push("List may be incomplete (" + stripChars(truncation.replace(/^ingredient list looks truncated /, ""), "()") + "). Group 4 stands because the markers found are already enough.");
      return Object.assign({}, common, { answered: true, group: r.group, reason: null, drivers: r.drivers, warnings, text, headline: `NOVA group ${r.group}: ${GROUP_NAMES[r.group]}` });
    }
    // Presentation-only: uses the same item predicates as the existing uncertainty reason.
    // It does not choose a group, add a rule or turn recognition into placement.
    function explanationItems(a) {
      const out = [], seen = new Set();
      function add(item, reason, need) {
        const key = item + "||" + reason;
        if (!seen.has(key)) { seen.add(key); out.push({ item, reason, need }); }
      }
      (a.unplaced || []).forEach((item) => add(item, "Recognised by name, but the available evidence does not establish this form in this list.", "A source that covers this exact form or a class that genuinely includes it."));
      const secs = (a.sections || []).map(([label, items]) => ({ label, items }));
      const ings = expand(secs.flatMap((sec) => sec.items.map((raw) => [raw, sec.label])), 0, [], []);
      for (const ing of ings) {
        const row = lookup(ing.name);
        if (row && (fatPowder(ing, row.kind) || ((row.kind === "food_powder" || powderRouted(ing, row.kind)) && !(ings.length === 1 && powderCompositionStated(ing)))))
          add(ing.raw, "The powder's composition is not established for classification.", "Item-specific composition, including any carriers or anti-caking agents. Its percentage of this product does not establish what the powder contains.");
      }
      (a.unassessed || []).filter((item) => !item.includes("(group name; its contents were assessed separately)")).forEach((item) => add(item, "Not fully assessed by the available vocabulary and rules.", "Check the extracted name against the pack; if accurate, the ingredient needs a supported decision rule."));
      if (!a.answered) (a.drivers || []).forEach((d) => add(d.ingredient, "Weak or unlisted evidence, not enough on its own to decide a group.", "A supported processing rule or other decisive label evidence. This is not proof of ultra-processing."));
      return out;
    }
    return { analyseText, explanationItems, NOT_ENOUGH, GROUP_NAMES };
  }

  root.FoodScan = { createEngine };
  if (typeof module !== "undefined" && module.exports) module.exports = root.FoodScan;
})(typeof window !== "undefined" ? window : globalThis);
