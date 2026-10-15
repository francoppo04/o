// Renderiza concept/html/*.html a concept/*.png con Chromium (Playwright).
// Uso: node tools/concept/render.js [filtro]
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const root = path.resolve(__dirname, '..', '..');
  const src = path.join(root, 'concept', 'html');
  const filter = process.argv[2] || '';
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1600, height: 900 } });
  for (const file of fs.readdirSync(src).filter(f => f.endsWith('.html') && f.includes(filter)).sort()) {
    await page.goto('file://' + path.join(src, file));
    await page.waitForTimeout(150);
    const el = await page.$('.card, .sheet');
    const out = path.join(root, 'concept', file.replace('.html', '.png'));
    await el.screenshot({ path: out });
    console.log(out);
  }
  await browser.close();
})();
