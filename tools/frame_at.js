// usage: node frame_at.js <html> <out.png> <ms> [crop x,y,w,h]
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [html, out, ms, crop = '200,180,610,820'] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 810, height: 1500 } });
  await page.route(/fonts\.(googleapis|gstatic)\.com/, (r) => r.abort());
  await page.goto('file://' + path.resolve(html));
  await page.evaluate((t) => {
    const f = document.querySelector('.frame');
    f.style.width = '810px'; f.style.height = '1440px'; document.body.style.padding = '0';
    for (const a of document.getAnimations()) { a.pause(); a.currentTime = t; }
  }, Number(ms));
  await page.waitForTimeout(150);
  const box = await (await page.$('.frame')).boundingBox();
  const [x, y, w, h] = crop.split(',').map(Number);
  await page.screenshot({ path: out, clip: { x: box.x + x, y: box.y + y, width: w, height: h } });
  await browser.close();
})();
