// Photo selection races (run by tests/test_photo_races_17.py). Args: base URL, a directory for temp files.
// Everything is deterministic: the thumbnail decode and the text reader are held on promises this script releases by hand.
//  - thumbnails: HTMLImageElement.src for blob: URLs is held while window.__holdImg is true; __imgRelease() lets the held loads start.
//  - reader: window.Tesseract is replaced by a stub whose recognize() waits on a promise released by window.__ocrRelease(i, text).
//  - which file each prepare()/makeThumb() opened is recorded by wrapping URL.createObjectURL (window.__opened = file names, in order).
// Images are generated in the page, so no private or platform-specific file is needed.
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const LIST = 'Ingredients: Wheat flour, Sugar, Acidity regulator (INS 330)';   // an additive code forces the second pass
(async () => {
  const base = process.argv[2], dir = process.argv[3];
  const b = await chromium.launch(); const out = {};
  async function fresh() {
    const pg = await b.newPage();
    await pg.addInitScript(() => {
      window.__opened = []; window.__ocr = []; window.__ocrCalls = 0; window.__holdImg = false; window.__held = [];
      const names = new Map(), cou = URL.createObjectURL.bind(URL);
      URL.createObjectURL = (f) => { const u = cou(f); names.set(u, f.name || '?'); window.__opened.push(f.name || '?'); return u; };
      const d = Object.getOwnPropertyDescriptor(HTMLImageElement.prototype, 'src');
      Object.defineProperty(HTMLImageElement.prototype, 'src', { configurable: true, get() { return d.get.call(this); },
        set(v) { if (window.__holdImg && typeof v === 'string' && v.startsWith('blob:')) window.__held.push(() => d.set.call(this, v)); else d.set.call(this, v); } });
      window.__imgRelease = () => { const h = window.__held; window.__held = []; h.forEach(f => f()); };
      window.__ocrRelease = (i, text) => window.__ocr[i].resolve({ data: { text } });
      const stub = { createWorker: async () => ({ recognize: () => new Promise((resolve) => { window.__ocr.push({ resolve }); window.__ocrCalls++; }), terminate: async () => { window.__terminated = (window.__terminated || 0) + 1; } }) };
      Object.defineProperty(window, 'Tesseract', { configurable: true, get() { return stub; }, set() {} });
    });
    await pg.goto(base + '/index.html'); await pg.click('#tab-photo');
    return pg;
  }
  async function mk(pg, name, w, h, color) {
    const png = await pg.evaluate(([w, h, color]) => { const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); g.fillStyle = color; g.fillRect(0, 0, w, h); return c.toDataURL('image/png').split(',')[1]; }, [w, h, color]);
    return { name, mimeType: 'image/png', buffer: Buffer.from(png, 'base64') };
  }
  const prev = (pg) => pg.evaluate(() => { const i = document.getElementById('photo-preview'); return { hidden: i.hidden, hasSrc: i.hasAttribute('src'), nw: i.naturalWidth, color: (() => { if (!i.hasAttribute('src') || !i.naturalWidth) return null; const c = document.createElement('canvas'); c.width = c.height = 1; const g = c.getContext('2d'); g.drawImage(i, 0, 0, 1, 1); return Array.from(g.getImageData(0, 0, 1, 1).data.slice(0, 3)); })() }; });
  const info = (pg) => pg.evaluate(() => ({ status: document.getElementById('photo-status').textContent, result: document.getElementById('result').innerText.slice(0, 120), analyse: !document.getElementById('photo-analyse').disabled, opened: window.__opened.slice(), terminated: window.__terminated || 0 }));
  const settle = (pg, ms = 500) => pg.waitForTimeout(ms);

  // T1 thumbnail of A is still decoding when B replaces it: A must not appear
  { const pg = await fresh(); const A = await mk(pg, 'A.png', 300, 200, '#ff0000'), B = await mk(pg, 'B.png', 300, 200, '#0000ff');
    await pg.evaluate(() => { window.__holdImg = true; });
    await pg.setInputFiles('#photo', A); await pg.setInputFiles('#photo', B);
    await pg.evaluate(() => { window.__holdImg = false; window.__imgRelease(); }); await settle(pg);
    out.thumb_replaced = await prev(pg); await pg.close(); }

  // T2 thumbnail of A is still decoding when the selection is cleared (empty change): A must not come back
  { const pg = await fresh(); const A = await mk(pg, 'A.png', 300, 200, '#ff0000');
    await pg.evaluate(() => { window.__holdImg = true; });
    await pg.setInputFiles('#photo', A); await pg.setInputFiles('#photo', []);
    await pg.evaluate(() => { window.__holdImg = false; window.__imgRelease(); }); await settle(pg);
    out.thumb_cleared = { ...(await prev(pg)), ...(await info(pg)), analyse: undefined, analyseEnabled: (await info(pg)).analyse }; await pg.close(); }

  // T3 same, but the clear arrives as a `cancel` event while the input is empty (a native picker cancel in browsers that clear on cancel)
  { const pg = await fresh(); const A = await mk(pg, 'A.png', 300, 200, '#ff0000');
    await pg.evaluate(() => { window.__holdImg = true; });
    await pg.setInputFiles('#photo', A);
    await pg.evaluate(() => { const i = document.getElementById('photo'); i.value = ''; i.dispatchEvent(new Event('cancel')); });
    await pg.evaluate(() => { window.__holdImg = false; window.__imgRelease(); }); await settle(pg);
    out.thumb_cancel_empty = { ...(await prev(pg)), analyseEnabled: (await info(pg)).analyse }; await pg.close(); }

  // T4 a synthetic cancel event while the selection is intact must not drop the selection or stop a reading
  { const pg = await fresh(); const A = await mk(pg, 'A.png', 300, 200, '#ff0000');
    await pg.setInputFiles('#photo', A); await settle(pg);
    await pg.click('#photo-analyse'); await settle(pg);
    await pg.evaluate(() => { document.getElementById('photo').dispatchEvent(new Event('cancel')); });
    await settle(pg, 200);
    const mid = await info(pg);
    await pg.evaluate((t) => window.__ocrRelease(0, t), LIST); await settle(pg, 300);
    await pg.evaluate((t) => window.__ocrRelease(1, t), LIST); await settle(pg, 500);
    out.synthetic_cancel = { analyseEnabledAfterCancel: mid.analyse, terminatedAfterCancel: mid.terminated, final: await info(pg), prev: await prev(pg) }; await pg.close(); }

  // T5 the first reading of A is in flight; B replaces A; the reading finishes. The second pass must not open B, and A's result must not be shown for B
  { const pg = await fresh(); const A = await mk(pg, 'A.png', 300, 200, '#ff0000'), B = await mk(pg, 'B.png', 300, 200, '#0000ff');
    await pg.setInputFiles('#photo', A); await settle(pg);
    await pg.click('#photo-analyse'); await settle(pg);
    await pg.setInputFiles('#photo', B); await settle(pg);
    const before = await info(pg);
    await pg.evaluate((t) => window.__ocrRelease(0, t), LIST); await settle(pg, 800);
    const calls = await pg.evaluate(() => window.__ocrCalls);
    if (calls > 1) { await pg.evaluate((t) => window.__ocrRelease(1, t), LIST); await settle(pg, 500); }
    out.replace_during_first_read = { beforeRelease: before, ocrCalls: calls, final: await info(pg), analyseEnabled: (await info(pg)).analyse }; await pg.close(); }

  // T6 the second pass of A is in flight; B replaces A; it finishes: A's result must not be shown for B
  { const pg = await fresh(); const A = await mk(pg, 'A.png', 300, 200, '#ff0000'), B = await mk(pg, 'B.png', 300, 200, '#0000ff');
    await pg.setInputFiles('#photo', A); await settle(pg);
    await pg.click('#photo-analyse'); await settle(pg);
    await pg.evaluate((t) => window.__ocrRelease(0, t), LIST); await settle(pg, 800);
    await pg.setInputFiles('#photo', B); await settle(pg);
    await pg.evaluate((t) => window.__ocrRelease(1, t), LIST); await settle(pg, 800);
    out.replace_during_second_read = { final: await info(pg), prev: await prev(pg) }; await pg.close(); }

  // T7 cleared during the first reading
  { const pg = await fresh(); const A = await mk(pg, 'A.png', 300, 200, '#ff0000');
    await pg.setInputFiles('#photo', A); await settle(pg);
    await pg.click('#photo-analyse'); await settle(pg);
    await pg.setInputFiles('#photo', []); await settle(pg);
    await pg.evaluate((t) => window.__ocrRelease(0, t), LIST); await settle(pg, 800);
    const calls = await pg.evaluate(() => window.__ocrCalls);
    out.clear_during_first_read = { ocrCalls: calls, final: await info(pg) }; await pg.close(); }

  // T8 a finished result of A, then B is chosen: A's result must not stay next to B's photo
  { const pg = await fresh(); const A = await mk(pg, 'A.png', 300, 200, '#ff0000'), B = await mk(pg, 'B.png', 300, 200, '#0000ff');
    await pg.setInputFiles('#photo', A); await settle(pg);
    await pg.click('#photo-analyse'); await settle(pg);
    await pg.evaluate((t) => window.__ocrRelease(0, t), LIST); await settle(pg, 600);
    await pg.evaluate((t) => window.__ocrRelease(1, t), LIST); await settle(pg, 800);
    const done = await info(pg);
    await pg.setInputFiles('#photo', B); await settle(pg);
    out.result_after_replace = { done, afterReplace: await info(pg) }; await pg.close(); }

  console.log(JSON.stringify(out)); await b.close();
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
