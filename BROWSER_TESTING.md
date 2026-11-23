# Browser reliability checks

These checks test result ownership when switching, replacing or cancelling photo/text inputs. The reader is mocked. Passing them does not establish real OCR accuracy, full label preservation or correct NOVA placement.

## Reproducible setup

Use Python 3.12+ and Node.js 20+ with npm. From the repository root:

```sh
python -m pip install -e '.[dev]'
npm ci
npx playwright install chromium
python scripts/fetch_tesseract_assets.py
python scripts/build_web_preview.py
npm run test:provenance
```

The npm lockfile pins Playwright and its dependencies. The asset-fetch script separately pins the existing Tesseract packages. On Linux, browser system libraries may also be needed. Install them using Playwright's documented platform prerequisites for your environment. Nothing installs implicitly during the gate.

An already installed Chromium can be selected with `--browser /path/to/chromium` or `FOODSCAN_BROWSER=/path/to/chromium`. Otherwise the gate uses the Chromium installed by Playwright, without a machine-specific hard-coded path. No NODE_PATH workaround is needed after npm ci.

```sh
python scripts/run_provenance_check.py --out-dir /tmp/foodscan-browser-evidence
python -m pytest -q tests/test_result_source_provenance.py tests/test_provenance_runner.py
```

The gate first verifies that the built page exactly matches current sources, using the existing acceptance runner's rebuild comparison. It then serves the built page on localhost only. It does not contact production, publish evidence, alter tracked regression material or install anything. By default evidence goes in a new temporary directory and its path is printed. The 22 check records, screenshot and browser logs are kept there.

Exit codes: 0 means exactly 22 checks passed; 1 means a check failed or execution was incomplete; 2 means setup is missing. Missing setup is never reported as a passing check. The existing pytest wrapper also fails on missing setup rather than silently skipping this reliability gate.

## Limits

This is a narrow deterministic gate, not the entire browser acceptance suite. It does not settle the known millet photo section/code tradeoff. The broader real-label acceptance runner remains `scripts/run_browser_acceptance_18.py` and retains its own build-identity and actual-OCR checks. No CI workflow is enabled here, avoiding assumptions about private-repository runner billing. Nothing about application runtime behavior or ingredient placement changes in this batch.
