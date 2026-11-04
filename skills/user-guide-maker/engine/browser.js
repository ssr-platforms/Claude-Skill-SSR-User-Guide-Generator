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

// The account every guide is captured as: its name shows in the screenshots (Recent changes,
// Analysis, the account menu) and its role decides which panels appear, so the guide must show
// what an ordinary customer sees. run.json's "user" (GUIDE_USER in guide.env) overrides the name;
// the account must never be root.
const DEFAULT_USER = 'Joe Bloggs';
function guideUser() {
  try { return JSON.parse(fs.readFileSync(path.join(W, 'run.json'), 'utf8')).user || DEFAULT_USER; } catch { return DEFAULT_USER; }
}

// Throws unless the signed-in user is the guide user and is not root. Reads the Inertia page
// props: IMPRINT passes `user_info`, IMPACT shares `auth.user`.
async function checkUser(page, expected = guideUser()) {
  const who = await page.evaluate(() => {
    const app = document.querySelector('#app');
    let p = app?.__vue_app__?.config?.globalProperties?.$page?.props;
    if (!p && app?.dataset?.page) { try { p = JSON.parse(app.dataset.page).props; } catch { /* not Inertia */ } }
    const u = p && (p.user_info || p.auth?.user);
    return u ? { name: u.name ?? null, role: u.role ?? null } : null;
  });
  const fix = `Sign in as "${expected}" (a non-root account): delete the browser profile in ${path.join(W, 'profile')} `
    + 'to end the current session, then mint a token for that user (see the platform profile).';
  if (!who) throw new Error('Could not tell who is signed in (no user in the page props). ' + fix);
  if (String(who.name).trim() !== expected) throw new Error(`Signed in as "${who.name}", not "${expected}". ` + fix);
  if (String(who.role).toLowerCase() === 'root') throw new Error(`"${who.name}" is a root user: guides must be captured as a non-root user. ` + fix);
  return who;
}

module.exports = { open, W, chromePath, guideUser, checkUser };
