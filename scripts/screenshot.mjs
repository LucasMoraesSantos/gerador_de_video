import fs from 'node:fs/promises';
import path from 'node:path';
import { chromium } from 'playwright';

const targetUrl = process.env.SCREENSHOT_URL || 'http://127.0.0.1:8000';
const outFile = process.env.SCREENSHOT_FILE || 'artifacts/ui-home.png';

const outDir = path.dirname(outFile);
await fs.mkdir(outDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

try {
  await page.goto(targetUrl, { waitUntil: 'networkidle', timeout: 60_000 });
  await page.screenshot({ path: outFile, fullPage: true });
  console.log(`Screenshot salvo em: ${outFile}`);
} finally {
  await browser.close();
}
