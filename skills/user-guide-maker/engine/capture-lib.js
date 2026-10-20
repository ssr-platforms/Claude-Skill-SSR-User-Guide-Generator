// Helpers every platform's capture scripts share. Runs under the same Node as browser.js.
//
//   const L = require('./capture-lib');
//   const run = L.config();                       // the run.json run.sh wrote
//   const s = await L.session(run, 'build-controls.json');
//   await L.signIn(s.page, run.app + '/editor/' + code, run);
//   await s.snap('name');                          // name.png + a dump of every visible control
//
// A dump row is { t, id, role, tour, row, s, ph, cls, b }: tag, id, ARIA role, the platform's
// tour / data hook, a row tag the script set, the on-screen label, placeholder, the classes
// matched by CLASS_RE, and the box [x, y, w, h] in CSS px of the 1600x900 viewport.
const fs = require('fs');
const path = require('path');
const { open, W } = require('./browser');

const SELECTOR = [
  'button', 'a', 'input', 'select', 'textarea', 'label', 'img', 'iframe', 'h1', 'h2', 'h3', 'h4', 'li', 'ol', 'tr',
  '[role]', '[id]', '[data-ide-tour]', '[data-ide-help-tour-trigger]', '[data-product-id]', '[data-instruction-target]',
  '[data-question-target]', '[data-flow-step]', '[data-guide-row]', '[data-guide-card]', '[id^=tour-]',
  '.sidebar-icon-menu-wrapper', '.card', '.glass-well', '.ProseMirror', '.range-slider', '.quick-access-row', '.cm-editor',
  '[class*=vue-flow__node]', '[class*=vue-flow__controls]', '[class*=vc-]', '[class*=rc-]', '[class*=tool-group]', '[class*=bar-group]',
].join(',');
const CLASS_RE = '^(ProseMirror|glass-well|vue-flow__|quick-access-row|cm-editor|range-slider|vc-|card$|rc-|tool-|bar-|stage-|ide-)';

function config() {
  const file = process.argv[2] || path.join(W, 'run.json');
  const run = JSON.parse(fs.readFileSync(file, 'utf8'));
  run.dry = run.dry === true || run.dry === '1' || process.env.DRY === '1';
  fs.mkdirSync(run.shots, { recursive: true });
  return run;
}

const dump = (page) => page.evaluate(([sel, classRe]) => {
  const re = new RegExp(classRe);
  const vis = (e) => {
    const r = e.getBoundingClientRect(); const st = getComputedStyle(e);
    return r.width > 2 && r.height > 2 && r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < innerWidth
      && st.visibility !== 'hidden' && st.opacity !== '0';
  };
  return [...document.querySelectorAll(sel)].filter(vis).map((e) => {
    const r = e.getBoundingClientRect();
    const cls = typeof e.className === 'string' ? e.className : '';
    return {
      t: e.tagName.toLowerCase(), id: e.id || '', role: e.getAttribute('role') || '',
      tour: e.getAttribute('data-ide-tour') || e.getAttribute('data-flow-step') || e.getAttribute('data-question-target')
        || e.getAttribute('data-instruction-target') || '',
      row: e.getAttribute('data-guide-row') || e.getAttribute('data-guide-card') || '',
      s: (e.getAttribute('aria-label') || e.getAttribute('title') || e.innerText || e.value || e.getAttribute('placeholder') || '')
        .replace(/\s+/g, ' ').trim().slice(0, 90),
      ph: e.getAttribute('placeholder') || '',
      cls: cls.split(/\s+/).filter((c) => re.test(c)).join(' '),
      b: [r.x, r.y, r.width, r.height].map((v) => Math.round(v)),
    };
  });
}, [SELECTOR, CLASS_RE]);

// One browser session; snap() screenshots and dumps, finish() writes the dump file.
async function session(run, dumpFile) {
  const { ctx, page } = await open();
  const controls = {}, extra = { warnings: [] };
  page.on('pageerror', (e) => console.log('PAGEERROR', e.message.slice(0, 160)));
  page.on('dialog', (d) => d.accept());               // only ever the native "leave this page?" confirm
  const snap = async (name, p = page) => {
    if (p === page) await page.mouse.move(800, 3);
    await p.waitForTimeout(900);
    await p.screenshot({ path: path.join(run.shots, name + '.png') });
    controls[name] = await dump(p);
    console.log('captured', name);
  };
  const warn = (msg) => { extra.warnings.push(msg); console.log('WARNING', msg); };
  const finish = async () => {
    fs.writeFileSync(path.join(run.shots, dumpFile), JSON.stringify({ controls, extra }));
    await ctx.close();
  };
  return { ctx, page, snap, warn, controls, extra, finish };
}

// Opens url, spending the one-time sign-in token in the work folder if there is one.
async function signIn(page, url, { okPath, wait = 5000 } = {}) {
  const tokenFile = path.join(W, '.token');
  let target = url;
  if (fs.existsSync(tokenFile)) {
    target += (url.includes('?') ? '&' : '?') + 'uid=' + fs.readFileSync(tokenFile, 'utf8').trim();
    fs.unlinkSync(tokenFile);
  }
  await page.goto(target, { waitUntil: 'networkidle', timeout: 90000 });
  await page.waitForTimeout(wait);
  if ((okPath && !page.url().includes(okPath)) || /\/login\b/i.test(page.url())) {
    throw new Error('Not signed in (landed on ' + page.url() + '). Mint a sign-in token: see the platform profile.');
  }
}

// Reads a Pinia store's state (read-only).
const readStore = (page, storeId, key) => page.evaluate(([id, k]) => {
  const app = document.querySelector('#app')?.__vue_app__;
  const pinia = app?.config?.globalProperties?.$pinia;
  const store = pinia?._s?.get(id);
  if (!store) return null;
  return JSON.parse(JSON.stringify(k ? store[k] : store.$state));
}, [storeId, key || null]);

// A colour in any CSS notation -> 8-digit hex (no #), via the browser's own parser.
const toHex8 = (page, colour) => page.evaluate((c) => {
  if (!c) return null;
  let s = String(c).trim();
  const m4 = /^#([0-9a-f])([0-9a-f])([0-9a-f])([0-9a-f])?$/i.exec(s);
  if (m4) return (m4[1] + m4[1] + m4[2] + m4[2] + m4[3] + m4[3] + (m4[4] ? m4[4] + m4[4] : 'ff')).toLowerCase();
  const m8 = /^#([0-9a-f]{6})([0-9a-f]{2})?$/i.exec(s);
  if (m8) return (m8[1] + (m8[2] || 'ff')).toLowerCase();
  const cx = document.createElement('canvas').getContext('2d');
  cx.fillStyle = '#000'; cx.fillStyle = s;
  const v = cx.fillStyle;
  if (v.startsWith('#')) return v.slice(1).toLowerCase() + 'ff';
  const m = /rgba?\(([^)]+)\)/.exec(v);
  if (!m) return null;
  const [r, g, b, a = 1] = m[1].split(',').map((x) => parseFloat(x));
  const h = (n) => Math.round(n).toString(16).padStart(2, '0');
  return h(r) + h(g) + h(b) + h(a * 255);
}, colour);

module.exports = { config, session, signIn, readStore, dump, toHex8, W };
