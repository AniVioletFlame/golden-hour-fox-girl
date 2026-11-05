// Render the page (or just the painting) to PNG for checking the drawing.
// usage: node shot.js <html> <out.png> [mode] [scale]
//   mode: "frame" (default, painting only, animations paused) | "page" | "crop:x,y,w,h" (viewBox coords)
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const [html, out, mode = 'frame', scale = '1'] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 810, height: 1500 }, deviceScaleFactor: Number(scale) });
  await page.route(/fonts\.(googleapis|gstatic)\.com/, (r) => r.abort());
  await page.goto('file://' + path.resolve(html));
  // freeze animations at their first frame so the still is deterministic
  await page.addStyleTag({ content: '*{animation-play-state:paused!important;animation-delay:0s!important}.mote{opacity:.7!important}.steam{opacity:.8!important}' });
  await page.waitForTimeout(300);
  if (mode === 'page') {
    await page.screenshot({ path: out });
  } else {
    await page.evaluate(() => {
      const f = document.querySelector('.frame');
      f.style.width = '810px'; f.style.height = '1440px'; f.style.borderRadius = '0';
      document.body.style.padding = '0';
    });
    const f = await page.$('.frame');
    if (mode.startsWith('crop:')) {
      const [x, y, w, h] = mode.slice(5).split(',').map(Number);
      const box = await f.boundingBox();
      await page.screenshot({ path: out, clip: { x: box.x + x, y: box.y + y, width: w, height: h } });
    } else {
      await f.screenshot({ path: out });
    }
  }
  await browser.close();
})();
