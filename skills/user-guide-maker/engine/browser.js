// Shared launcher. Runs under WINDOWS Node (see SKILL.md for why): Windows Chrome,
// headless, with a persistent profile in the work folder so a one-time sign-in
// token is spent only once and the session is kept between runs.
//
// CHROME_EXE overrides the browser; otherwise the usual install places are tried.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright-core');

const W = __dirname;
const CANDIDATES = [
  process.env.CHROME_EXE,
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
  process.env.LOCALAPPDATA && path.join(process.env.LOCALAPPDATA, 'Google\\Chrome\\Application\\chrome.exe'),
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
  '/usr/bin/google-chrome', '/usr/bin/chromium', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
].filter(Boolean);

function chromePath() {
  const hit = CANDIDATES.find((p) => { try { return fs.existsSync(p); } catch { return false; } });
  if (!hit) throw new Error('No Chrome or Edge found: set CHROME_EXE to the browser executable');
  return hit;
}

async function open({ width = 1600, height = 900, scale = 2 } = {}) {
  const ctx = await chromium.launchPersistentContext(path.join(W, 'profile'), {
    executablePath: chromePath(),
    headless: true,
    viewport: { width, height },
    deviceScaleFactor: scale,
  });
  const page = ctx.pages()[0] || await ctx.newPage();
  page.setDefaultTimeout(20000);
  return { ctx, page, W };
}

module.exports = { open, W, chromePath };
