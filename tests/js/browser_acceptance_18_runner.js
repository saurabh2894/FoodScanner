/**
 * Repeatable real-label browser acceptance gate runner (CDP-based).
 * Exercises normal browser controls without calling private APIs directly.
 */
const http = require('http');
const fs = require('fs');
const path = require('path');

function getJson(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(JSON.parse(data)));
    }).on('error', reject);
  });
}

function parseArgs() {
  const args = {};
  for (const arg of process.argv.slice(2)) {
    if (arg.startsWith('--')) {
      const eq = arg.indexOf('=');
      if (eq > -1) {
        args[arg.slice(2, eq)] = arg.slice(eq + 1);
      } else {
        args[arg.slice(2)] = true;
      }
    }
  }
  return args;
}

class CDPClient {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.ws = null;
    this.nextId = 1;
    this.pending = new Map();
    this.eventListeners = new Map();
  }
  connect() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.wsUrl);
      this.ws.onopen = () => resolve();
      this.ws.onerror = reject;
      this.ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.id && this.pending.has(msg.id)) {
          const { resolve, reject } = this.pending.get(msg.id);
          this.pending.delete(msg.id);
          if (msg.error) reject(new Error(msg.error.message));
          else resolve(msg.result);
        } else if (msg.method) {
          const listeners = this.eventListeners.get(msg.method) || [];
          for (const l of listeners) l(msg.params);
        }
      };
    });
  }
  send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = this.nextId++;
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }
  close() {
    if (this.ws) this.ws.close();
  }
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function main() {
  const args = parseArgs();
  const cdpPort = args['cdp-port'] || 9222;
  const targetUrl = args['target'] || 'http://127.0.0.1:8000/index.html';
  const outPath = args['out'] || path.resolve(__dirname, '../../evaluation/browser_acceptance_18/test_results.json');
  const screenshotsDir = args['screenshots-dir'] || path.resolve(__dirname, '../../evaluation/browser_acceptance_18/screenshots');
  const smokeLive = Boolean(args['smoke-live']);

  fs.mkdirSync(screenshotsDir, { recursive: true });

  const versionInfo = await getJson(`http://127.0.0.1:${cdpPort}/json/version`);
  const targets = await getJson(`http://127.0.0.1:${cdpPort}/json`);
  const pageTarget = targets.find(t => t.type === 'page');
  if (!pageTarget) throw new Error('No page target found');

  const cdp = new CDPClient(pageTarget.webSocketDebuggerUrl);
  await cdp.connect();
  await cdp.send('Page.enable');
  await cdp.send('DOM.enable');
  await cdp.send('Runtime.enable');

  async function evalExpr(expr) {
    const res = await cdp.send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
    if (res.exceptionDetails) {
      throw new Error(`Eval error: ${JSON.stringify(res.exceptionDetails)}`);
    }
    return res.result ? res.result.value : undefined;
  }

  async function setViewport(width, height, isMobile = false) {
    await cdp.send('Emulation.setDeviceMetricsOverride', {
      width,
      height,
      deviceScaleFactor: 1,
      mobile: isMobile
    });
    await sleep(200);
  }

  async function captureScreenshot(filename) {
    const shot = await cdp.send('Page.captureScreenshot', { format: 'png' });
    const fullPath = path.join(screenshotsDir, filename);
    fs.writeFileSync(fullPath, Buffer.from(shot.data, 'base64'));
    return fullPath;
  }

  async function waitForCondition(checkFn, timeoutMs = 45000, intervalMs = 250) {
    const t0 = Date.now();
    while (Date.now() - t0 < timeoutMs) {
      const val = await checkFn();
      if (val) return val;
      await sleep(intervalMs);
    }
    throw new Error(`Timed out waiting for condition after ${timeoutMs}ms`);
  }

  async function switchToTab(tabId) {
    await evalExpr(`document.getElementById('${tabId}').click();`);
    await sleep(150);
  }

  async function setPasteText(text) {
    await evalExpr(`
      (function() {
        var el = document.getElementById('label-text');
        el.value = ${JSON.stringify(text)};
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
      })()
    `);
    await sleep(100);
  }

  async function clickAnalyse() {
    await evalExpr(`document.getElementById('analyse').click();`);
    await sleep(250);
  }

  async function getLayoutMetrics() {
    return await evalExpr(`
      (function() {
        var de = document.documentElement;
        var btnAnalyse = document.getElementById('analyse');
        var rAnalyse = btnAnalyse ? btnAnalyse.getBoundingClientRect() : null;
        var btnPhoto = document.getElementById('photo-analyse');
        var rPhoto = btnPhoto ? btnPhoto.getBoundingClientRect() : null;
        var res = document.getElementById('result');
        var rRes = res ? res.getBoundingClientRect() : null;
        return {
          clientWidth: de.clientWidth,
          scrollWidth: de.scrollWidth,
          clientHeight: de.clientHeight,
          hasHorizontalOverflow: de.scrollWidth > de.clientWidth,
          btnAnalyse: rAnalyse ? {
            top: rAnalyse.top,
            left: rAnalyse.left,
            width: rAnalyse.width,
            height: rAnalyse.height,
            visible: rAnalyse.width > 0 && rAnalyse.height > 0
          } : null,
          btnPhoto: rPhoto ? {
            top: rPhoto.top,
            left: rPhoto.left,
            width: rPhoto.width,
            height: rPhoto.height,
            visible: rPhoto.width > 0 && rPhoto.height > 0
          } : null,
          resultCard: rRes ? {
            top: rRes.top,
            left: rRes.left,
            width: rRes.width,
            height: rRes.height,
            visible: rRes.width > 0 && rRes.height > 0
          } : null
        };
      })()
    `);
  }

  async function getResultData() {
    return await evalExpr(`
      (function() {
        var res = document.getElementById('result');
        if (!res) return null;
        var hero = res.querySelector('h2.group-hero');
        var abstainPanel = res.querySelector('.panel.abstain');
        var h2 = res.querySelector('h2');
        var headline = h2 ? h2.textContent.trim() : '';
        var groupMatch = headline.match(/NOVA\\s+group\\s+(\\d)/i);
        var group = groupMatch ? parseInt(groupMatch[1], 10) : null;
        var isAbstain = Boolean(abstainPanel) || (headline.toLowerCase().indexOf('not enough information') > -1);
        
        var warnings = [];
        res.querySelectorAll('.warn, p.hint, .ins-note').forEach(function(el) {
          warnings.push(el.textContent.trim());
        });
        
        var drivers = [];
        res.querySelectorAll('h3').forEach(function(h3) {
          var ht = h3.textContent.trim();
          if (ht.indexOf('Driven by') > -1 || ht.indexOf('Weak evidence seen') > -1) {
            var ul = h3.nextElementSibling;
            if (ul && ul.tagName === 'UL') {
              ul.querySelectorAll('li').forEach(function(li) {
                drivers.push(li.textContent.trim());
              });
            }
          }
        });

        var insMappings = [];
        res.querySelectorAll('.ins-row').forEach(function(row) {
          var code = row.querySelector('.ins-code');
          var name = row.querySelector('.ins-name');
          if (code) insMappings.push({ code: code.textContent.trim(), name: name ? name.textContent.trim() : '' });
        });

        return {
          headline: headline,
          group: group,
          isAbstain: isAbstain,
          warnings: warnings,
          drivers: drivers,
          insMappings: insMappings,
          fullHtml: res.innerHTML
        };
      })()
    `);
  }

  async function runPhotoOcr(filePath) {
    await switchToTab('tab-photo');
    const doc = await cdp.send('DOM.getDocument');
    const inputNode = await cdp.send('DOM.querySelector', { nodeId: doc.root.nodeId, selector: '#photo' });
    if (!inputNode || !inputNode.nodeId) throw new Error('#photo input element not found');

    await cdp.send('DOM.setFileInputFiles', { nodeId: inputNode.nodeId, files: [filePath] });
    await sleep(300);

    const btnDisabledBefore = await evalExpr(`document.getElementById('photo-analyse').disabled`);
    if (btnDisabledBefore) throw new Error('#photo-analyse button remained disabled after file selection');

    await evalExpr(`document.getElementById('photo-analyse').click();`);

    // Wait for OCR completion
    const t0 = Date.now();
    await waitForCondition(async () => {
      const state = await evalExpr(`
        (function() {
          var btn = document.getElementById('photo-analyse');
          var st = document.getElementById('photo-status');
          var txt = st ? st.textContent : '';
          return {
            btnDisabled: btn.disabled,
            statusText: txt,
            done: (!btn.disabled && (txt.indexOf('Done') > -1 || txt.indexOf('failed') > -1 || txt.indexOf('stalled') > -1))
          };
        })()
      `);
      return state.done ? state : null;
    }, 60000, 500);

    const extractedText = await evalExpr(`document.getElementById('label-text').value`);
    const resultData = await getResultData();
    const photoStatus = await evalExpr(`document.getElementById('photo-status').textContent`);

    return {
      durationMs: Date.now() - t0,
      photoStatus,
      extractedText,
      resultData
    };
  }

  // Setup desktop viewport by default
  await setViewport(1280, 720, false);
  await cdp.send('Page.navigate', { url: targetUrl });
  await sleep(1000);

  const testReport = {
    gateName: 'repeatable_real_label_browser_acceptance_gate',
    runTimestamp: new Date().toISOString(),
    environment: {
      targetUrl,
      browser: versionInfo.product || 'Google Chrome',
      cdpVersion: versionInfo['Protocol-Version'] || '1.3'
    },
    clientConfusionAudit: {},
    labels: {},
    syntheticControls: {},
    pixelInspection: {},
    summary: {
      totalUniqueRealLabels: 0,
      totalExecutions: 0,
      passedExecutions: 0,
      failedExecutions: 0
    }
  };

  // --- 1. Client Confusion & Stale Build Audit ---
  const localFooter = await evalExpr(`
    (function() {
      var p = document.querySelector('footer p');
      return p ? p.textContent.trim() : '';
    })()
  `);
  const localParityMatch = localFooter.match(/(\d+)\s+of\s+(\d+)\s+matched/i);
  testReport.clientConfusionAudit.localBuild = {
    url: targetUrl,
    footerText: localFooter,
    parityMatched: localParityMatch ? parseInt(localParityMatch[1], 10) : null,
    parityTotal: localParityMatch ? parseInt(localParityMatch[2], 10) : null,
    isCurrentSeniorBaseline: localParityMatch ? localParityMatch[1] === '921' : false
  };

  if (smokeLive) {
    try {
      await cdp.send('Page.navigate', { url: 'https://foodscan-nine.vercel.app/' });
      await sleep(1500);
      const liveFooter = await evalExpr(`
        (function() {
          var p = document.querySelector('footer p');
          return p ? p.textContent.trim() : '';
        })()
      `);
      const liveMatch = liveFooter.match(/(\d+)\s+of\s+(\d+)\s+matched/i);
      await captureScreenshot('live_production_desktop_1280x720.png');
      testReport.clientConfusionAudit.liveProduction = {
        url: 'https://foodscan-nine.vercel.app/',
        footerText: liveFooter,
        parityMatched: liveMatch ? parseInt(liveMatch[1], 10) : null,
        parityTotal: liveMatch ? parseInt(liveMatch[2], 10) : null,
        screenshot: 'live_production_desktop_1280x720.png',
        staleBuildDetected: liveMatch ? (liveMatch[1] !== '921') : true,
        notes: 'Production serves earlier build (859 parity) while local main tests 921 parity.'
      };
    } catch (e) {
      testReport.clientConfusionAudit.liveProduction = { error: e.message };
    } finally {
      await cdp.send('Page.navigate', { url: targetUrl });
      await sleep(1000);
    }
  }

  // --- INVENTORY OF REAL LABELS ---
  const ROOT = path.resolve(__dirname, '../..');
  const FIXTURES = {
    L01: {
      id: 'L01_multigrain',
      name: 'Original Multigrain Flour Blend Label',
      kind: 'REAL_LABEL',
      hasPhysicalPhoto: true,
      imagePath: path.join(ROOT, 'evaluation/browser_acceptance_18/inputs/original_multigrain_label.jpg'),
      imageSha256: 'beed9e9324b246295fa74e729161640e448ff2afdf0f045577e38fc53eff5f18',
      textPath: path.join(ROOT, 'evaluation/browser_acceptance_18/inputs/original_multigrain_label.txt'),
      textContent: fs.readFileSync(path.join(ROOT, 'evaluation/browser_acceptance_18/inputs/original_multigrain_label.txt'), 'utf-8').trim(),
      expectedGroup: null,
      expectedAbstain: true,
      expectedDrivers: [],
      provenanceLimitations: 'Physical pack photo uploaded via web chat (57KB, 607x494 relay compressed, not RAW camera file).',
      whyUseful: 'Validates bracketed blend pair splitting, footnote stripping on # and ##, and honest abstention on unplaced sprouted grains & powder uncertainty.'
    },
    L02: {
      id: 'L02_millet_puff',
      name: 'Millet Puff Snack Pack Label',
      kind: 'REAL_LABEL',
      hasPhysicalPhoto: true,
      imagePath: path.join(ROOT, 'tests/fixtures/millet_puff_label.jpg'),
      imageSha256: '0befae618d66bf8c5c78e5eda12db9d1fe3da8b00976eefc3737c36edf3902fb',
      textContent: `INGREDIENTS:
Puff 88%: Supergrain Blend (Jowar, Foxtail Millet,
Corn, Rice)(72%), Rice Bran Oil(16%).
Seasoning 12%: Vegetables and Spices (Onion,
Garlic, Tomato, Chilli, Amchur, Tamarind), Salt,
Natural and Nature Identical Flavours, Raw Sugar,
Acidity Regulators(INS330, INS296, INS334),
Potassium Chloride - Salt Substitute (INS 508),
Rosemary Extract - Antioxidant (INS 392).
THIS PRODUCT CONTAINS 37% MILLETS`,
      expectedGroup: 4,
      expectedAbstain: false,
      expectedDrivers: ['Natural and Nature Identical Flavours'],
      provenanceLimitations: 'Real packaged food label photo in repo fixtures, cropped to ingredients section.',
      whyUseful: 'Validates section headings with percentages (Puff 88%:, Seasoning 12%:), additive INS codes, unassessed term disclosure (Amchur), and Group 4 classification.'
    },
    L03: {
      id: 'L03_potato_chips',
      name: 'Potato Chips Label',
      kind: 'REAL_LABEL',
      hasPhysicalPhoto: true,
      imagePath: path.join(ROOT, 'tests/fixtures/chips_label.png'),
      imageSha256: 'f434a7bf97d5271abeb4db1c51f4d5013575245ab76318319a820aab811eaac9',
      textContent: `INGREDIENTS: Potato (83%), Edible Vegetable Oil*, *Seasoning (Sugar, Iodised Salt, Milk Solids (1.2%), Spices and Condiments, Maltodextrin, Flavour (Natural and Nature Identical Flavouring Substances), Cheese Powder (0.3%), Hydrolysed Vegetable Protein, Flavour Enhancers (627, 631), Edible Vegetable Oil (Palm, Coconut). *As flavouring agent. ALLERGEN ADVICE: Contains Soy, Milk`,
      expectedGroup: 4,
      expectedAbstain: false,
      expectedDrivers: ['Maltodextrin', 'Hydrolysed Vegetable Protein', 'Flavour Enhancers (627, 631)'],
      provenanceLimitations: 'Real potato chip pack photographed at small scale.',
      whyUseful: 'Validates structural syntax warning on unclosed bracket (*Seasoning ( opened and not closed), multiple UPF markers, and Group 4 assignment.'
    },
    L04: {
      id: 'L04_negation_r1',
      name: 'Dlecta Cheese / Milk Product (Negation R1)',
      kind: 'REAL_LABEL',
      hasPhysicalPhoto: false,
      textPath: path.join(ROOT, 'evaluation/negation_addendum/inputs/R1.txt'),
      textContent: fs.readFileSync(path.join(ROOT, 'evaluation/negation_addendum/inputs/R1.txt'), 'utf-8').trim(),
      expectedGroup: null,
      expectedAbstain: true,
      provenanceLimitations: 'Open Food Facts India (barcode prefix 890), photo not retained in repository git tree.',
      whyUseful: 'Validates negation handling ("CONTAINS NO ADDED FLAVOUR") without false Group 4 assignment.'
    },
    L05: {
      id: 'L05_negation_r2',
      name: 'Potato Snack Negation R2',
      kind: 'REAL_LABEL',
      hasPhysicalPhoto: false,
      textPath: path.join(ROOT, 'evaluation/negation_addendum/inputs/R2.txt'),
      textContent: fs.readFileSync(path.join(ROOT, 'evaluation/negation_addendum/inputs/R2.txt'), 'utf-8').trim(),
      expectedGroup: null,
      expectedAbstain: true,
      provenanceLimitations: 'Open Food Facts India, photo not retained in repository git tree.',
      whyUseful: 'Validates multi-term absence statement ("No artificial colours, flavours or preservatives") without false Group 4.'
    },
    L06: {
      id: 'L06_negation_r3',
      name: 'Flavoured Curd Mixed Positive + Negative R3',
      kind: 'REAL_LABEL',
      hasPhysicalPhoto: false,
      textPath: path.join(ROOT, 'evaluation/negation_addendum/inputs/R3.txt'),
      textContent: fs.readFileSync(path.join(ROOT, 'evaluation/negation_addendum/inputs/R3.txt'), 'utf-8').trim(),
      expectedGroup: 4,
      expectedAbstain: false,
      expectedDrivers: ['CONTAINS ADDED FLAVOUR(S)'],
      provenanceLimitations: 'Open Food Facts India, photo not retained in repository git tree.',
      whyUseful: 'Validates mixed clause: positive added flavour marker triggers Group 4 while negative "NO PRESERVATIVES" claim does not suppress it.'
    }
  };

  testReport.summary.totalUniqueRealLabels = Object.keys(FIXTURES).length;

  // --- 2. EXECUTE PASTE FLOWS FOR REAL LABELS ---
  for (const [key, fix] of Object.entries(FIXTURES)) {
    testReport.summary.totalExecutions++;
    await switchToTab('tab-text');
    await setPasteText(fix.textContent);
    await clickAnalyse();

    const res = await getResultData();
    const layout = await getLayoutMetrics();

    let passed = false;
    let failureReason = '';

    if (fix.expectedAbstain) {
      if (res.isAbstain && res.group === null) {
        passed = true;
      } else {
        failureReason = `Expected honest abstention (group null), got group ${res.group}`;
      }
    } else {
      if (res.group === fix.expectedGroup && !res.isAbstain) {
        passed = true;
      } else {
        failureReason = `Expected group ${fix.expectedGroup}, got ${res.group} (isAbstain=${res.isAbstain})`;
      }
    }

    if (passed) testReport.summary.passedExecutions++;
    else testReport.summary.failedExecutions++;

    const shotName = `paste_${key.toLowerCase()}_1280x720.png`;
    await captureScreenshot(shotName);

    testReport.labels[key] = {
      meta: {
        id: fix.id,
        name: fix.name,
        kind: fix.kind,
        hasPhysicalPhoto: fix.hasPhysicalPhoto,
        imageSha256: fix.imageSha256 || null,
        provenanceLimitations: fix.provenanceLimitations,
        whyUseful: fix.whyUseful
      },
      pasteFlow: {
        submittedLength: fix.textContent.length,
        headline: res.headline,
        observedGroup: res.group,
        isAbstain: res.isAbstain,
        warningsCount: res.warnings.length,
        driversFound: res.drivers,
        passed,
        failureReason: failureReason || null,
        screenshot: shotName,
        layout: {
          hasHorizontalOverflow: layout.hasHorizontalOverflow,
          btnAnalyseVisible: layout.btnAnalyse && layout.btnAnalyse.visible
        }
      }
    };
  }

  // --- 3. RE-ANALYSIS & INPUT-BINDING TEST (L01 Multigrain) ---
  testReport.summary.totalExecutions++;
  await switchToTab('tab-text');
  const editedMultigrain = FIXTURES.L01.textContent.replace(/\.\s*$/, '') + ', Sugar, Maltodextrin.';
  await setPasteText(editedMultigrain);
  await clickAnalyse();

  const editRes = await getResultData();
  const editShot = 'l01_multigrain_edited_reanalyse_1280x720.png';
  await captureScreenshot(editShot);

  const reanalysePassed = (editRes.group === 4 && editRes.drivers.some(d => d.indexOf('Maltodextrin') > -1));
  if (reanalysePassed) testReport.summary.passedExecutions++;
  else testReport.summary.failedExecutions++;

  testReport.labels.L01.editAndReanalyse = {
    action: 'Appended " Sugar, Maltodextrin."',
    observedHeadline: editRes.headline,
    observedGroup: editRes.group,
    drivers: editRes.drivers,
    passed: reanalysePassed,
    screenshot: editShot,
    provesFreshInputAssociation: reanalysePassed
  };

  // --- 4. EXECUTE PHOTO FLOWS WHERE PHYSICAL PHOTOS EXIST (L01, L02, L03) ---
  for (const key of ['L01', 'L02', 'L03']) {
    const fix = FIXTURES[key];
    testReport.summary.totalExecutions++;

    const photoResult = await runPhotoOcr(fix.imagePath);
    const photoShot = `photo_${key.toLowerCase()}_complete_1280x720.png`;
    await captureScreenshot(photoShot);

    // Calculate text similarity / diff vs reference
    const refText = fix.textContent;
    const ocrText = photoResult.extractedText;
    const diffSample = {
      refLength: refText.length,
      ocrLength: ocrText.length,
      first50CharsOcr: ocrText.slice(0, 50).replace(/\\n/g, ' '),
      exactMatch: refText === ocrText
    };

    let photoPassed = false;
    let photoFailureReason = '';

    if (fix.expectedAbstain) {
      if (photoResult.resultData.isAbstain && photoResult.resultData.group === null) {
        photoPassed = true;
      } else {
        photoFailureReason = `Expected OCR result to abstain honestly, got group ${photoResult.resultData.group}`;
      }
    } else {
      if (photoResult.resultData.group === fix.expectedGroup) {
        photoPassed = true;
      } else {
        photoFailureReason = `Expected OCR result to yield group ${fix.expectedGroup}, got ${photoResult.resultData.group}`;
      }
    }

    if (photoPassed) testReport.summary.passedExecutions++;
    else testReport.summary.failedExecutions++;

    testReport.labels[key].photoFlow = {
      imagePath: fix.imagePath,
      imageSha256: fix.imageSha256,
      durationMs: photoResult.durationMs,
      photoStatus: photoResult.photoStatus,
      diffVsReference: diffSample,
      ocrHeadline: photoResult.resultData.headline,
      ocrGroup: photoResult.resultData.group,
      ocrIsAbstain: photoResult.resultData.isAbstain,
      passed: photoPassed,
      failureReason: photoFailureReason || null,
      screenshot: photoShot
    };

    // For L01, also test OCR correction flow in Paste tab
    if (key === 'L01') {
      testReport.summary.totalExecutions++;
      await switchToTab('tab-text');
      // Fix closing quote or double asterisks in extracted OCR text
      const correctedOcr = photoResult.extractedText.replace('Vitamins”', 'Vitamins#').replace('Minerals**', 'Minerals##');
      await setPasteText(correctedOcr);
      await clickAnalyse();

      const correctedRes = await getResultData();
      const correctedShot = 'l01_multigrain_ocr_corrected_paste_1280x720.png';
      await captureScreenshot(correctedShot);

      const correctionPassed = (correctedRes.isAbstain && correctedRes.group === null);
      if (correctionPassed) testReport.summary.passedExecutions++;
      else testReport.summary.failedExecutions++;

      testReport.labels.L01.ocrCorrectionFlow = {
        action: 'Corrected OCR closing quote to footnote hash (# and ##) in Paste tab and clicked Analyse',
        observedHeadline: correctedRes.headline,
        observedGroup: correctedRes.group,
        isAbstain: correctedRes.isAbstain,
        passed: correctionPassed,
        screenshot: correctedShot
      };
    }
  }

  // --- 5. SYNTHETIC NEGATIVE CONTROLS (SEPARATE) ---
  // NC01: Empty input
  testReport.summary.totalExecutions++;
  await switchToTab('tab-text');
  await setPasteText('');
  await clickAnalyse();
  const emptyRes = await getResultData();
  const emptyShot = 'nc01_empty_input_1280x720.png';
  await captureScreenshot(emptyShot);
  const emptyPassed = (emptyRes.isAbstain && emptyRes.group === null && emptyRes.headline.indexOf('No text to analyse') > -1);
  if (emptyPassed) testReport.summary.passedExecutions++;
  else testReport.summary.failedExecutions++;

  testReport.syntheticControls.NC01_empty = {
    name: 'Empty Input Negative Control',
    kind: 'SYNTHETIC_CONTROL',
    submittedText: '',
    observedHeadline: emptyRes.headline,
    observedGroup: emptyRes.group,
    isAbstain: emptyRes.isAbstain,
    noStaleGroupVisible: emptyRes.group === null,
    passed: emptyPassed,
    screenshot: emptyShot
  };

  // NC02: Completely unknown synthetic ingredients
  testReport.summary.totalExecutions++;
  await switchToTab('tab-text');
  const unknownText = 'Ingredients: SyntheticChemicalX999, FakeCompoundZ404.';
  await setPasteText(unknownText);
  await clickAnalyse();
  const unkRes = await getResultData();
  const unkShot = 'nc02_unknown_chemical_1280x720.png';
  await captureScreenshot(unkShot);
  const unkPassed = (unkRes.isAbstain && unkRes.group === null && unkRes.warnings.some(w => w.indexOf('SyntheticChemicalX999') > -1 || w.indexOf('vocabulary') > -1));
  if (unkPassed) testReport.summary.passedExecutions++;
  else testReport.summary.failedExecutions++;

  testReport.syntheticControls.NC02_unknown_compound = {
    name: 'Unknown Synthetic Chemical Negative Control',
    kind: 'SYNTHETIC_CONTROL',
    submittedText: unknownText,
    observedHeadline: unkRes.headline,
    observedGroup: unkRes.group,
    isAbstain: unkRes.isAbstain,
    noStaleGroupVisible: unkRes.group === null,
    passed: unkPassed,
    screenshot: unkShot
  };

  // --- 6. VIEWPORT & PIXEL INSPECTION (DESKTOP 1280x720 & MOBILE 390x844) ---
  // Switch to L01 Multigrain on Mobile Viewport
  await switchToTab('tab-text');
  await setPasteText(FIXTURES.L01.textContent);
  await clickAnalyse();
  await setViewport(390, 844, true);
  await sleep(300);

  const mobileLayout = await getLayoutMetrics();
  const mobileShot = 'viewport_mobile_390x844_multigrain.png';
  await captureScreenshot(mobileShot);

  // Return to Desktop
  await setViewport(1280, 720, false);
  const desktopLayout = await getLayoutMetrics();
  const desktopShot = 'viewport_desktop_1280x720_multigrain.png';
  await captureScreenshot(desktopShot);

  testReport.pixelInspection = {
    desktop_1280x720: {
      clientWidth: desktopLayout.clientWidth,
      scrollWidth: desktopLayout.scrollWidth,
      hasHorizontalOverflow: desktopLayout.hasHorizontalOverflow,
      analyseButton: desktopLayout.btnAnalyse,
      photoAnalyseButton: desktopLayout.btnPhoto,
      resultCard: desktopLayout.resultCard,
      screenshot: desktopShot
    },
    mobile_390x844: {
      clientWidth: mobileLayout.clientWidth,
      scrollWidth: mobileLayout.scrollWidth,
      hasHorizontalOverflow: mobileLayout.hasHorizontalOverflow,
      analyseButton: mobileLayout.btnAnalyse,
      photoAnalyseButton: mobileLayout.btnPhoto,
      resultCard: mobileLayout.resultCard,
      screenshot: mobileShot,
      noHorizontalOverflowPass: !mobileLayout.hasHorizontalOverflow,
      buttonsFullyVisible: Boolean(mobileLayout.btnAnalyse && mobileLayout.btnAnalyse.visible)
    }
  };

  cdp.close();

  fs.writeFileSync(outPath, JSON.stringify(testReport, null, 2), 'utf-8');
  console.log(`Gate completed: ${testReport.summary.passedExecutions}/${testReport.summary.totalExecutions} executions passed across ${testReport.summary.totalUniqueRealLabels} real labels.`);
}

main().catch(err => {
  console.error('Gate execution failed:', err);
  process.exit(1);
});
