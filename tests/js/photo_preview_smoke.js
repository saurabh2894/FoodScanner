// Photo preview smoke test (run by tests/test_photo_preview.py): a selected image gets a small self-contained thumbnail that survives the file being removed from disk;
// a file that is not an image hides the preview and says so, and never leaves a broken image. Args: base URL, a directory for temp files.
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => {
  const base = process.argv[2], dir = process.argv[3];
  // 600x400 gradient PNG built in the page itself, so no image library is needed here
  const b = await chromium.launch(); const pg = await b.newPage();
  await pg.goto(base + '/index.html'); await pg.click('#tab-photo');
  const png = await pg.evaluate(() => { const c = document.createElement('canvas'); c.width = 1600; c.height = 1000; const g = c.getContext('2d'); g.fillStyle = '#ddd'; g.fillRect(0,0,1600,1000); g.fillStyle = '#000'; g.font = '60px sans-serif'; g.fillText('Ingredients: Rice, salt.', 100, 500); return c.toDataURL('image/png').split(',')[1]; });
  const good = path.join(dir, 'good.png'), bad = path.join(dir, 'bad.jpg');
  fs.writeFileSync(good, Buffer.from(png, 'base64')); fs.writeFileSync(bad, 'not an image');
  const st = () => pg.evaluate(() => { const i = document.getElementById('photo-preview'); return {hidden: i.hidden, complete: i.complete, nw: i.naturalWidth, nh: i.naturalHeight, src: (i.getAttribute('src') || '').slice(0, 11), status: document.getElementById('photo-status').textContent}; });
  const out = {};
  await pg.setInputFiles('#photo', good); await pg.waitForTimeout(1200); out.selected = await st();
  fs.unlinkSync(good); await pg.waitForTimeout(400); out.fileGone = await st();
  await pg.click('#tab-text'); await pg.click('#tab-photo'); out.tabRound = await st();
  await pg.setInputFiles('#photo', bad); await pg.waitForTimeout(1200); out.notImage = await st();
  console.log(JSON.stringify(out)); await b.close();
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
