// Task 18 browser acceptance gate (senior version). Real local OCR (the page's own Tesseract files); no mocked reader.
// Usage: node browser_acceptance_18_senior.js --target=URL --out=results.json --screenshots-dir=DIR --fixtures=fixtures.json --root=REPO
//        [--provenance=file.json] [--allow-unknown-build] [--skip-photo] [--browser=/path/to/chrome]
//        [--smoke-live=URL [--expected-parity=N]]       production smoke is explicit opt-in; nothing is contacted otherwise
// Exit code: 0 all checks passed and all required evidence present; 1 a check failed / required evidence missing / wrong local build; 2 partial run (--skip-photo), not an acceptance.
// Results go only to --out and --screenshots-dir (the caller chooses; tracked evidence is never overwritten by default).
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path'); const crypto = require('crypto');
const A = Object.fromEntries(process.argv.slice(2).filter(a => a.startsWith('--')).map(a => { const i = a.indexOf('='); return i < 0 ? [a.slice(2), true] : [a.slice(2, i), a.slice(i + 1)]; }));
const need = (k) => { if (!A[k]) { console.error('missing --' + k); process.exit(1); } return A[k]; };
const target = need('target'), outPath = need('out'), shotDir = need('screenshots-dir'), fixPath = need('fixtures'), ROOT = need('root');
const sha = (buf) => crypto.createHash('sha256').update(buf).digest('hex');
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const report = { gate: 'real_label_browser_acceptance', runTimestamp: new Date().toISOString(), target, browser: null, provenance: null, build: {}, labels: {}, controls: {}, viewport: {}, liveSmoke: null, limitations: [
  'Files are attached with the browser automation file-input API; the operating-system picker (and its cancel) is not exercised.',
  'Pixel checks are screenshot decodes (not blank, content present) plus DOM metrics; they do not prove visual correctness of every element.',
  'OCR runs the page\'s bundled Tesseract: output can vary between runs and browsers; photo expectations name only items that were stable and label-visible.'], checks: [], missingEvidence: [] };
function check(name, pass, detail) { report.checks.push({ name, pass: !!pass, detail: detail === undefined ? null : detail }); return !!pass; }
function missing(what) { report.missingEvidence.push(what); }

async function resultOf(pg) {
  return pg.evaluate(() => {
    const res = document.getElementById('result'), h2 = res.querySelector('h2'), headline = h2 ? h2.textContent.trim() : '';
    const m = headline.match(/NOVA\s+group\s+(\d)/i), drivers = [];
    res.querySelectorAll('h3').forEach(h3 => { if (/Driven by|Weak evidence seen/i.test(h3.textContent)) { const ul = h3.nextElementSibling; if (ul && ul.tagName === 'UL') ul.querySelectorAll('li').forEach(li => drivers.push(li.textContent.trim())); } });
    const text = res.innerText, c = text.match(/COMPLETENESS:\s*([A-Z]+)/i);
    return { headline, group: m ? +m[1] : null, abstain: /not enough information/i.test(headline) || !!res.querySelector('.panel.abstain'), drivers, text, completeness: c ? c[1].toUpperCase() : null };
  });
}
function judge(label, which, r, exp, extracted) {          // item-level checks; completeness is its own check, never folded into the group check
  const pre = label + ' ' + which + ': ';
  check(pre + 'group', exp.group === null ? (r.abstain && r.group === null) : (!r.abstain && r.group === exp.group), { expected: exp.group, observed: r.group, headline: r.headline.slice(0, 100) });
  (exp.driversInclude || []).forEach(d => check(pre + 'driver/weak-evidence item "' + d + '"', r.drivers.some(x => x.includes(d)), r.drivers.slice(0, 8)));
  (exp.resultIncludes || []).forEach(s => check(pre + 'result mentions "' + s + '"', r.text.includes(s) || r.text.toLowerCase().includes(s.toLowerCase())));
  (exp.resultExcludes || []).forEach(s => check(pre + 'result does not contain "' + s + '"', !r.text.toUpperCase().includes(s.toUpperCase())));
  (exp.extractedIncludes || []).forEach(s => check(pre + 'extracted text contains "' + s + '"', (extracted || '').includes(s)));
}
async function shot(pg, name) { const p = path.join(shotDir, name); await pg.screenshot({ path: p }); const ok = fs.existsSync(p) && fs.statSync(p).size > 1000; if (!ok) missing('screenshot ' + name); return { file: name, bytes: ok ? fs.statSync(p).size : 0, sha256: ok ? sha(fs.readFileSync(p)) : null }; }
async function pixels(pg) {                                  // decode a real screenshot of the result card: must hold content, not be blank
  const buf = await pg.locator('#result').screenshot();
  return pg.evaluate(async (b64) => { const img = new Image(); img.src = 'data:image/png;base64,' + b64; await img.decode(); const c = document.createElement('canvas'); c.width = img.width; c.height = img.height; const g = c.getContext('2d'); g.drawImage(img, 0, 0);
    const d = g.getImageData(0, 0, c.width, c.height).data; let nonBg = 0; const bg = [d[0], d[1], d[2]]; const seen = new Set();
    for (let i = 0; i < d.length; i += 4) { if (Math.abs(d[i] - bg[0]) + Math.abs(d[i + 1] - bg[1]) + Math.abs(d[i + 2] - bg[2]) > 40) nonBg++; seen.add((d[i] >> 4) * 256 + (d[i + 1] >> 4) * 16 + (d[i + 2] >> 4)); }
    return { w: img.width, h: img.height, nonBackgroundFraction: +(nonBg / (d.length / 4)).toFixed(4), distinctColours: seen.size }; }, buf.toString('base64'));
}
async function setPaste(pg, text) { await pg.click('#tab-text'); await pg.fill('#label-text', text); const v = await pg.inputValue('#label-text'); await pg.click('#analyse'); return v; }

(async () => {
  fs.mkdirSync(shotDir, { recursive: true }); fs.mkdirSync(path.dirname(outPath), { recursive: true });
  const fx = JSON.parse(fs.readFileSync(fixPath, 'utf8')).labels;
  // provenance of the build under test (computed by the Python caller from the sources; this runner only records and enforces it)
  let prov = null; if (A.provenance) { try { prov = JSON.parse(fs.readFileSync(A.provenance, 'utf8')); } catch (e) { missing('provenance file unreadable: ' + e.message); } }
  report.provenance = prov;
  const buildStatus = prov ? prov.status : 'unknown';
  report.build.status = buildStatus;
  check('local build identity: dist is an exact rebuild of the current sources', buildStatus === 'exact_rebuild_match' || (buildStatus === 'unknown' && !!A['allow-unknown-build']), { status: buildStatus, note: buildStatus === 'unknown' ? 'identity could not be established; pass --allow-unknown-build only for a build you cannot verify' : undefined });

  const b = await chromium.launch(A.browser ? { executablePath: A.browser } : {}); report.browser = b.version();
  const pg = await b.newPage({ viewport: { width: 1280, height: 720 } });
  const errs = []; pg.on('pageerror', e => errs.push(String(e.message).slice(0, 200)));
  await pg.goto(target); await sleep(500);
  const footer = await pg.evaluate(() => { const p = document.querySelector('footer p'); return p ? p.textContent.trim() : ''; });
  const fm = footer.match(/(\d+)\s+of\s+(\d+)\s+matched/i);
  report.build.footerStamp = { text: footer, matched: fm ? +fm[1] : null, total: fm ? +fm[2] : null, note: 'a static string written at build time: a stamp, not proof of which commit built the page' };
  if (prov && prov.expectedParityTotal != null) check('footer stamp equals the parity total of the current sources (stamp consistency only)', report.build.footerStamp.total === prov.expectedParityTotal && report.build.footerStamp.matched === prov.expectedParityTotal, { observed: report.build.footerStamp, expected: prov.expectedParityTotal });

  // ---- paste flows (deterministic) ----
  const texts = {};
  for (const f of fx) {
    const p = path.join(ROOT, f.textPath);
    if (!fs.existsSync(p)) { missing('fixture text ' + f.textPath); check(f.key + ': fixture text present', false, f.textPath); continue; }
    texts[f.key] = fs.readFileSync(p, 'utf8').trim();
    const submitted = await setPaste(pg, texts[f.key]);
    check(f.key + ' paste: the textarea held exactly the fixture text that was analysed', submitted === texts[f.key]);
    const r = await resultOf(pg); judge(f.key, 'paste', r, f.paste);
    check(f.key + ' paste: completeness (separate from group)', r.completeness === f.paste.completeness, { expected: f.paste.completeness, observed: r.completeness });
    const px = await pixels(pg); check(f.key + ' paste: result card screenshot has content', px.nonBackgroundFraction > 0.01 && px.distinctColours > 3, px);
    report.labels[f.key] = { name: f.name, kind: f.kind, provenance: f.provenance, why: f.why, hasPhysicalPhoto: !!f.imagePath, imageSha256: f.imageSha256 || null, paste: { headline: r.headline, group: r.group, completeness: r.completeness, drivers: r.drivers, pixels: px, screenshot: await shot(pg, 'paste_' + f.key.toLowerCase() + '.png') } };
  }

  // ---- re-analysis binds to fresh input (synthetic edit of the L01 reference text; a mutation CONTROL, not a real-label result) ----
  if (texts.L01) {
    const before = await (async () => { await setPaste(pg, texts.L01); return resultOf(pg); })();
    const edited = texts.L01.replace(/\.\s*$/, '') + ', Sugar, Maltodextrin.';
    const sub = await setPaste(pg, edited); const after = await resultOf(pg);
    check('CONTROL edit-and-reanalyse: submitted text is exactly the edited text and differs from the original', sub === edited && edited !== texts.L01);
    check('CONTROL edit-and-reanalyse: the result changed with the input (group and driver)', after.group === 4 && after.drivers.some(d => d.includes('Maltodextrin')) && before.group === null, { before: before.group, after: after.group });
    report.controls.synthetic_edit_reanalyse = { kind: 'SYNTHETIC_MUTATION_CONTROL', action: 'appended ", Sugar, Maltodextrin." to the L01 reference text', beforeGroup: before.group, afterGroup: after.group, afterDrivers: after.drivers, screenshot: await shot(pg, 'control_edit_reanalyse.png') };
  }
  // ---- negative controls (synthetic) ----
  { await setPaste(pg, ''); const r = await resultOf(pg); check('CONTROL empty input: abstains with "No text to analyse" and no stale group', r.abstain && r.group === null && /No text to analyse/i.test(r.headline), r.headline); report.controls.empty = { kind: 'SYNTHETIC_CONTROL', headline: r.headline }; }
  { await setPaste(pg, 'Ingredients: SyntheticChemicalX999, FakeCompoundZ404.'); const r = await resultOf(pg); check('CONTROL unknown compounds: abstain and name them', r.abstain && r.group === null && r.text.includes('SyntheticChemicalX999') && r.text.includes('FakeCompoundZ404'), r.headline.slice(0, 120)); report.controls.unknown = { kind: 'SYNTHETIC_CONTROL', headline: r.headline.slice(0, 160) }; }

  // ---- photo flows: real local OCR ----
  const photoKeys = fx.filter(f => f.imagePath).map(f => f.key);
  if (A['skip-photo']) { report.partial = 'photo flows skipped (--skip-photo): not an acceptance run'; }
  else for (const f of fx.filter(x => x.imagePath)) {
    const ip = path.join(ROOT, f.imagePath);
    if (!fs.existsSync(ip)) { missing('fixture image ' + f.imagePath); check(f.key + ': fixture image present', false, f.imagePath); continue; }
    const bytes = fs.readFileSync(ip); check(f.key + ': fixture image is the recorded file (sha256)', sha(bytes) === f.imageSha256, { observed: sha(bytes), expected: f.imageSha256 });
    await pg.reload(); await pg.click('#tab-photo'); await pg.setInputFiles('#photo', ip);
    const t0 = Date.now(); await pg.click('#photo-analyse');
    let timedOut = false; try { await pg.waitForFunction(() => /Done|failed|stalled/.test(document.getElementById('photo-status').textContent), null, { timeout: 120000 }); } catch (e) { timedOut = true; }
    const dur = Date.now() - t0, status = await pg.textContent('#photo-status'), extracted = await pg.inputValue('#label-text'), r = await resultOf(pg);
    check(f.key + ' photo: reading finished with "Done" (not failed/stalled/timeout)', !timedOut && /^Done/.test(status), status.slice(0, 120));
    check(f.key + ' photo: extracted text is non-empty (>= 20 words)', extracted.trim().split(/\s+/).filter(Boolean).length >= 20, { words: extracted.trim().split(/\s+/).filter(Boolean).length });
    judge(f.key, 'photo', r, f.photo, extracted);
    const refWords = new Set(texts[f.key].toLowerCase().match(/[a-z]{4,}/g) || []), ocrWords = new Set(extracted.toLowerCase().match(/[a-z]{4,}/g) || []);
    let hit = 0; refWords.forEach(w => { if (ocrWords.has(w)) hit++; });
    const px = await pixels(pg); check(f.key + ' photo: result card screenshot has content', px.nonBackgroundFraction > 0.01 && px.distinctColours > 3, px);
    report.labels[f.key].photo = { durationMs: dur, status, extractedWords: extracted.trim().split(/\s+/).filter(Boolean).length, referenceWordRecall: +(hit / Math.max(1, refWords.size)).toFixed(3), headline: r.headline, group: r.group, completeness: r.completeness, completenessNote: 'recorded, not part of the group check', drivers: r.drivers, extractedTextFirst400: extracted.slice(0, 400), screenshot: await shot(pg, 'photo_' + f.key.toLowerCase() + '.png') };

    if (f.key === 'L01') {      // real OCR correction: only when the real OCR output actually contains the artefacts, and only against the owner's reference text
      const fixes = [['Vitamins”', 'Vitamins#'], ['Minerals**', 'Minerals##']].filter(([from]) => extracted.includes(from));
      if (!fixes.length) { report.labels.L01.ocrCorrection = { status: 'skipped', reason: 'the real OCR output of this run contained neither "Vitamins”" nor "Minerals**", so there was nothing to correct; no correction is claimed' }; }
      else {
        let corrected = extracted; fixes.forEach(([from, to]) => { corrected = corrected.split(from).join(to); });
        const beforeR = r; const sub = await setPaste(pg, corrected); const afterR = await resultOf(pg);
        check('L01 OCR correction: corrected text differs from the OCR text and is exactly what was submitted', corrected !== extracted && sub === corrected);
        check('L01 OCR correction: result reflects the correction (footnote items now read Vitamins#/Minerals##, still honest abstention)', afterR.abstain && afterR.group === null && afterR.text !== beforeR.text && fixes.every(([, to]) => afterR.text.includes(to)), { changed: afterR.text !== beforeR.text });
        report.labels.L01.ocrCorrection = { status: 'run', replacements: fixes.map(([a, b2]) => a + ' -> ' + b2), basis: 'the owner\'s reference transcription reads "Vitamins# and Minerals##"', beforeGroup: beforeR.group, afterGroup: afterR.group, screenshot: await shot(pg, 'l01_ocr_corrected_paste.png') };
      }
    }
  }
  report.inventory = { realLabels: fx.length, withPhysicalPhoto: photoKeys.length, pasteOnly: fx.length - photoKeys.length, photoKeys };

  // ---- viewports ----
  if (texts.L01) {
    await pg.goto(target); await setPaste(pg, texts.L01);
    for (const [name, w, h, mobile] of [['mobile_390x844', 390, 844, true], ['desktop_1280x720', 1280, 720, false]]) {
      const ctx = await b.newContext({ viewport: { width: w, height: h }, isMobile: mobile, hasTouch: mobile }); const p2 = await ctx.newPage(); await p2.goto(target); await setPaste(p2, texts.L01);
      const m = await p2.evaluate(() => { const de = document.documentElement, vis = id => { const e = document.getElementById(id); if (!e) return null; const r = e.getBoundingClientRect(); return { width: Math.round(r.width), height: Math.round(r.height), visible: r.width > 0 && r.height > 0 && r.left >= 0 && r.right <= de.clientWidth + 1 }; }; return { clientWidth: de.clientWidth, scrollWidth: de.scrollWidth, overflow: de.scrollWidth > de.clientWidth, analyse: vis('analyse'), result: vis('result') }; });
      check('viewport ' + name + ': no horizontal overflow and Analyse button inside the viewport', !m.overflow && m.analyse && m.analyse.visible, m);
      const px = await pixels(p2); check('viewport ' + name + ': result card screenshot has content', px.nonBackgroundFraction > 0.01, px);
      report.viewport[name] = { ...m, pixels: px, screenshot: await (async () => { const f2 = path.join(shotDir, 'viewport_' + name + '.png'); await p2.screenshot({ path: f2 }); return { file: path.basename(f2), sha256: sha(fs.readFileSync(f2)) }; })() };
      await ctx.close();
    }
  }
  check('no uncaught page errors', errs.length === 0, errs);
  await pg.close();

  // ---- production smoke: explicit opt-in only; compares what is observed with what the caller says is expected; never a commit proof ----
  if (A['smoke-live']) {
    const url = A['smoke-live'] === true ? null : A['smoke-live'];
    if (!url) { report.liveSmoke = { status: 'not_run', reason: '--smoke-live needs a URL' }; missing('live smoke URL'); }
    else {
      const p3 = await b.newPage(); try { await p3.goto(url, { timeout: 30000 }); const t = await p3.evaluate(() => { const p = document.querySelector('footer p'); return p ? p.textContent.trim() : ''; }); const m = t.match(/(\d+)\s+of\s+(\d+)\s+matched/i);
        const obs = m ? { matched: +m[1], total: +m[2] } : null; const exp = A['expected-parity'] ? +A['expected-parity'] : null;
        report.liveSmoke = { url, observedStamp: obs, expectedParity: exp, status: !obs ? 'unreadable_stamp' : exp === null ? 'observed_only' : (obs.total === exp && obs.matched === exp ? 'stamp_matches_expected' : 'stamp_differs_from_expected'), note: 'the footer stamp is not commit identity; a match is consistent with, not proof of, the expected build' };
        if (exp !== null) check('live smoke: observed footer stamp equals the expected stamp you supplied', report.liveSmoke.status === 'stamp_matches_expected', report.liveSmoke);
      } catch (e) { report.liveSmoke = { url, status: 'unreachable', error: String(e.message).slice(0, 160) }; check('live smoke: site reachable', false, report.liveSmoke); }
      await p3.close();
    }
  }
  await b.close();

  const failed = report.checks.filter(c => !c.pass);
  report.summary = { checks: report.checks.length, passed: report.checks.length - failed.length, failed: failed.length, failedNames: failed.map(c => c.name), missingEvidence: report.missingEvidence, partial: report.partial || null, buildStatus };
  fs.writeFileSync(outPath, JSON.stringify(report, null, 2));
  console.log(`checks ${report.summary.passed}/${report.summary.checks} passed; missing evidence: ${report.missingEvidence.length}; build: ${buildStatus}${report.partial ? '; PARTIAL' : ''}`);
  failed.forEach(c => console.log('FAIL ' + c.name));
  process.exit(failed.length || report.missingEvidence.length ? 1 : report.partial ? 2 : 0);
})().catch(e => { console.error('gate crashed:', e.message); process.exit(1); });
