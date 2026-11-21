// Renders a pasted list holding an unplaced item and prints the section headings and the list items under them (run by tests/test_unplaced_render.py).
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage();
  await pg.goto(process.argv[2] + '/index.html');
  await pg.fill('#label-text', 'Ingredients: Rice, salt, Vitamins and Minerals, Sprouted Ragi, Zorbium.');
  await pg.click('#analyse'); await pg.waitForTimeout(500);
  const out = await pg.evaluate(() => {
    const r = document.getElementById('result'); const secs = {};
    r.querySelectorAll('h3').forEach(h => { const ul = h.parentElement.querySelector('ul'); secs[h.textContent] = ul ? Array.from(ul.querySelectorAll('li')).map(l => l.textContent) : []; });
    return { text: r.innerText.slice(0, 600), secs, scale: (r.querySelector('[role=img]') || {}).getAttribute ? r.querySelector('[role=img]').getAttribute('aria-label') : null };
  });
  console.log(JSON.stringify(out)); await b.close();
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
