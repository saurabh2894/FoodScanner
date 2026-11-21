const http = require('http');
const fs = require('fs');

function getJson(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(JSON.parse(data)));
    }).on('error', reject);
  });
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

async function main() {
  const cdpPort = process.argv[2];
  const origJpg = process.argv[3];
  const validPng = process.argv[4];
  const invalidFile = process.argv[5];
  const screenshotDir = process.argv[6];

  const tabs = await getJson(`http://127.0.0.1:${cdpPort}/json`);
  const pageTab = tabs.find(t => t.type === 'page');
  const client = new CDPClient(pageTab.webSocketDebuggerUrl);
  await client.connect();

  await client.send('Page.enable');
  await client.send('DOM.enable');
  await client.send('Runtime.enable');

  async function evalState() {
    const r = await client.send('Runtime.evaluate', {
      expression: `({
        status: document.getElementById('photo-status').textContent,
        previewHidden: document.getElementById('photo-preview').hidden,
        previewSrc: (document.getElementById('photo-preview').getAttribute('src') || '').slice(0, 40),
        previewComplete: document.getElementById('photo-preview').complete,
        naturalWidth: document.getElementById('photo-preview').naturalWidth,
        naturalHeight: document.getElementById('photo-preview').naturalHeight,
        btnDisabled: document.getElementById('photo-analyse').disabled,
        clientWidth: document.documentElement.clientWidth,
        scrollWidth: document.documentElement.scrollWidth,
        hasResultCard: document.getElementById('result').children.length > 0
      })`,
      returnByValue: true
    });
    return r.result.value;
  }

  async function takeScreenshot(name) {
    const ss = await client.send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(`${screenshotDir}/${name}.png`, Buffer.from(ss.data, 'base64'));
  }

  // Navigate to photo tab
  await client.send('Runtime.evaluate', { expression: `document.getElementById('tab-photo').click()` });
  const doc = await client.send('DOM.getDocument');
  const photoNode = await client.send('DOM.querySelector', { nodeId: doc.root.nodeId, selector: '#photo' });

  const results = {};

  // 1. Original JPEG Desktop (1280x720)
  await client.send('DOM.setFileInputFiles', { files: [origJpg], nodeId: photoNode.nodeId });
  await new Promise(r => setTimeout(r, 1500));
  results.original_jpeg_desktop = await evalState();
  await takeScreenshot('after_fix_desktop_orig_1280x720');

  // 2. Original JPEG Mobile (390x844)
  await client.send('Emulation.setDeviceMetricsOverride', {
    width: 390,
    height: 844,
    deviceScaleFactor: 2,
    mobile: true
  });
  await new Promise(r => setTimeout(r, 500));
  results.original_jpeg_mobile = await evalState();
  await takeScreenshot('after_fix_mobile_orig_390x844');

  // Reset device metrics to desktop
  await client.send('Emulation.clearDeviceMetricsOverride');
  await new Promise(r => setTimeout(r, 300));

  // 3. Valid PNG
  await client.send('DOM.setFileInputFiles', { files: [validPng], nodeId: photoNode.nodeId });
  await new Promise(r => setTimeout(r, 1200));
  results.valid_png = await evalState();

  // 4. Invalid non-image file
  await client.send('DOM.setFileInputFiles', { files: [invalidFile], nodeId: photoNode.nodeId });
  await new Promise(r => setTimeout(r, 1200));
  results.invalid_file = await evalState();
  await takeScreenshot('after_fix_invalid_file_1280x720');

  // 5. Cleared selection
  await client.send('Runtime.evaluate', {
    expression: `(() => {
      const el = document.getElementById('photo');
      el.value = '';
      el.dispatchEvent(new Event('change'));
    })()`
  });
  await new Promise(r => setTimeout(r, 400));
  results.cleared_selection = await evalState();
  await takeScreenshot('after_fix_cleared_selection_1280x720');

  // 6. Replacement flow
  // Select validPng first
  await client.send('DOM.setFileInputFiles', { files: [validPng], nodeId: photoNode.nodeId });
  await new Promise(r => setTimeout(r, 1200));

  // Install MutationObserver to observe synchronous loading state and old preview clearing
  await client.send('Runtime.evaluate', {
    expression: `(() => {
      window.__loadingObserved = false;
      window.__oldCleared = false;
      const pv = document.getElementById('photo-preview');
      const st = document.getElementById('photo-status');
      const observer = new MutationObserver(() => {
        if (st.textContent === 'Loading preview…') window.__loadingObserved = true;
        if (pv.hidden === true) window.__oldCleared = true;
      });
      observer.observe(st, { childList: true, characterData: true, subtree: true });
      observer.observe(pv, { attributes: true, attributeFilter: ['hidden', 'src'] });
    })()`
  });

  // Now replace with origJpg
  await client.send('DOM.setFileInputFiles', { files: [origJpg], nodeId: photoNode.nodeId });
  await new Promise(r => setTimeout(r, 1500));
  const settledRep = await evalState();

  const observed = await client.send('Runtime.evaluate', {
    expression: `({
      loadingObserved: window.__loadingObserved,
      oldCleared: window.__oldCleared
    })`,
    returnByValue: true
  });

  results.replacement = {
    loadingStateObserved: observed.result.value.loadingObserved,
    oldPreviewClearedImmediately: observed.result.value.oldCleared,
    settled: settledRep
  };

  // 7. Reselecting the same file
  // Click #photo resets this.value = ""
  await client.send('Runtime.evaluate', { expression: `document.getElementById('photo').click()` });
  await client.send('DOM.setFileInputFiles', { files: [validPng], nodeId: photoNode.nodeId });
  await new Promise(r => setTimeout(r, 1200));
  const reselectState = await evalState();
  results.reselect_same = {
    reselectEventFired: reselectState.previewHidden === false,
    previewHidden: reselectState.previewHidden,
    status: reselectState.status
  };

  // 8. Tab switch
  await client.send('Runtime.evaluate', { expression: `document.getElementById('tab-text').click()` });
  await new Promise(r => setTimeout(r, 300));
  await client.send('Runtime.evaluate', { expression: `document.getElementById('tab-photo').click()` });
  results.tab_switch = await evalState();

  // 9. End-to-end OCR and clearing prior results
  await client.send('DOM.setFileInputFiles', { files: [origJpg], nodeId: photoNode.nodeId });
  await new Promise(r => setTimeout(r, 1000));
  await client.send('Runtime.evaluate', { expression: `document.getElementById('photo-analyse').click()` });

  let ocrDone = false;
  const start = Date.now();
  while (Date.now() - start < 35000) {
    const s = await client.send('Runtime.evaluate', { expression: `document.getElementById('photo-status').textContent` });
    if (s.result.value.startsWith('Done') || s.result.value.includes('Photo could not be read')) {
      ocrDone = s.result.value.startsWith('Done');
      break;
    }
    await new Promise(r => setTimeout(r, 1000));
  }

  const extractedText = (await client.send('Runtime.evaluate', { expression: `document.getElementById('label-text').value` })).result.value;
  const afterOcrState = await evalState();
  await takeScreenshot('after_fix_ocr_complete_1280x720');

  // Now select a new file (validPng) and check that prior result card is cleared!
  await client.send('DOM.setFileInputFiles', { files: [validPng], nodeId: photoNode.nodeId });
  await new Promise(r => setTimeout(r, 500));
  const afterNewFileState = await evalState();

  results.ocr_end_to_end = {
    ocrCompleted: ocrDone,
    extractedText: extractedText,
    resultCardRendered: afterOcrState.hasResultCard,
    newSelectionClearedPriorResult: afterNewFileState.hasResultCard === false
  };

  client.close();

  const output = {
    timestamp: new Date().toISOString(),
    browser: 'Google Chrome (Headless)',
    results
  };

  console.log(JSON.stringify(output, null, 2));
}

main().catch(err => {
  console.error('RUNNER_ERROR:', err);
  process.exit(1);
});
