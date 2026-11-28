const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");

async function main() {
  const cases = JSON.parse(fs.readFileSync(0, "utf8"));
  const html = fs.readFileSync(path.resolve(__dirname, "../../web_preview/dist/index.html"), "utf8");
  const browser = await chromium.launch({ executablePath: process.env.FOODSCAN_BROWSER });
  try {
    const page = await browser.newPage();
    await page.setContent(html);
    for (const [text, expected] of cases) {
      await page.fill("#label-text", text);
      await page.click("#analyse");
      const actual = await page.locator("#result").evaluate((result) => [
        result.querySelector(".classification-status").textContent,
        result.querySelector(".classification-reason")?.textContent ?? null,
        result.querySelector(".text-completeness").textContent,
        [...result.querySelectorAll(".ingredient-name")].map((name) => [
          name.textContent, name.parentElement.querySelector(".ingredient-quantity")?.textContent ?? null,
        ]),
      ]);
      assert.deepEqual(actual, expected, text);
    }
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
