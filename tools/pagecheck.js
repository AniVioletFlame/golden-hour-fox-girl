const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const browser = await chromium.launch();
  for (const [name, w, h] of [['desk', 1280, 800], ['phone', 390, 844]]) {
    const page = await browser.newPage({ viewport: { width: w, height: h } });
    const errs = [];
    page.on('pageerror', (e) => errs.push(e.message));
    page.on('console', (m) => m.type() === 'error' && errs.push(m.text()));
    await page.route(/fonts\.(googleapis|gstatic)\.com/, (r) => r.abort());
    await page.goto('file://' + path.resolve(process.argv[2]));
    await page.waitForTimeout(400);
    const m = await page.evaluate(() => {
      const f = document.querySelector('.frame').getBoundingClientRect();
      return { frame: [Math.round(f.width), Math.round(f.height), Math.round(f.top)], sw: document.documentElement.scrollWidth, sh: document.documentElement.scrollHeight };
    });
    console.log(name, JSON.stringify(m), errs);
    await page.screenshot({ path: `page-${name}.png` });
    await page.close();
  }
  await browser.close();
})();
