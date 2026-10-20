// Captures every screenshot the guide uses, plus a dump of each state's visible
// controls (label + box in CSS px) so content.py can place callouts by looking
// controls up by their on-screen label instead of by hand-typed coordinates.
//
// SAFETY: this only looks and opens panels and menus (capture-build.js does the
// editing, on the demo test only). It never presses Save, never confirms a dialog, and never
// touches a `.rc-restore` button. Nothing reaches the saved test.
//
// Run under WINDOWS node from the work folder (run.sh does this):
//   node capture.js <shotsDir> [testCode]
const fs = require('fs'), path = require('path');
const { open, W } = require('./browser');

// run.sh passes its run.json; the old form <shotsDir> [code] still works.
const RUN = (process.argv[2] || '').endsWith('.json') ? JSON.parse(fs.readFileSync(process.argv[2], 'utf8')) : null;
const SHOTS = RUN ? RUN.shots : (process.argv[2] || path.join(W, 'shots'));
const CODE = RUN ? RUN.target : (process.argv[3] || 'SO2GKM679H');
const CLONE = RUN ? RUN.clone : 'ABUVANIDYQ';
const DRY = !!(RUN && (RUN.dry === true || RUN.dry === '1'));
if (CODE === CLONE) throw new Error('the Test to populate must not be the Test to clone');
const URL = `${RUN ? RUN.app : 'http://impact.test'}/survey/${CODE}`;
fs.mkdirSync(SHOTS, { recursive: true });

const dump = (page) => page.evaluate(() => {
  const vis = (e) => {
    const r = e.getBoundingClientRect();
    const st = getComputedStyle(e);
    return r.width > 2 && r.height > 2 && r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < innerWidth
      && st.visibility !== 'hidden' && st.opacity !== '0';
  };
  const sel = '[data-instruction-target],[role=status],button,a,input,select,textarea,label,img,iframe,h1,h2,h3,h4,[role],[id^=tour-],#how-it-works-btn,'
    + '.ide-strip-label,[class*=flow-node],[class*=vue-flow__node],[class*=rc-],[class*=ide-menu],[class*=drawer],[class*=bar-group],[class*=tool-group]';
  return [...document.querySelectorAll(sel)].filter(vis).map((e) => {
    const r = e.getBoundingClientRect();
    const cls = typeof e.className === 'string' ? e.className : '';
    return {
      t: e.tagName.toLowerCase(), id: e.id || '', role: e.getAttribute('role') || '',
      c: cls.split(/\s+/).filter((c) => /^(tool|bar|flow|stage|ide|vue-flow|rc-|drawer)/.test(c)).join(' '),
      s: (e.getAttribute('aria-label') || e.getAttribute('title') || e.innerText || e.value || e.getAttribute('placeholder') || '')
        .replace(/\s+/g, ' ').trim().slice(0, 90),
      b: [r.x, r.y, r.width, r.height].map((v) => Math.round(v)),
    };
  });
});

(async () => {
  const { ctx, page } = await open();
  const controls = {};
  const extra = {};
  page.on('pageerror', (e) => console.log('PAGEERROR', e.message.slice(0, 160)));

  const snap = async (name) => {
    await page.mouse.move(800, 3);
    await page.waitForTimeout(900);
    await page.screenshot({ path: path.join(SHOTS, name + '.png') });
    controls[name] = await dump(page);
    console.log('captured', name);
  };
  const load = async () => {
    let url = URL;
    const tokenFile = path.join(W, '.token');   // spent once; see profile.md
    if (fs.existsSync(tokenFile)) { url += '?uid=' + fs.readFileSync(tokenFile, 'utf8').trim(); fs.unlinkSync(tokenFile); }
    await page.goto(url, { waitUntil: 'networkidle', timeout: 90000 });
    await page.waitForTimeout(2500);
    if (!page.url().includes('/survey/') || /verification|not defined|login/i.test(await page.title())) throw new Error('Not signed in (landed on ' + page.url() + '). Mint a token: see PROGRESS.md.');
    const skip = page.getByRole('button', { name: 'Skip tour' });
    if (await skip.isVisible().catch(() => false)) await skip.click();
    await page.locator('#tour-stage-view').getByText('Stimuli').first().click();
    await page.waitForTimeout(1500);
  };
  const box = async (loc) => {
    const b = await loc.first().boundingBox();
    return b && [b.x, b.y, b.width, b.height].map((v) => Math.round(v));
  };

  try {
    // --- the IDE at rest, Stimuli view
    await load();
    await snap('ide');
    // the stage strip is one card around both tiers: their nearest common ancestor
    extra.strip = await page.evaluate(() => {
      const a = document.querySelector('#tour-toolbar'), s = document.querySelector('#tour-stage-view');
      let e = a; while (e && !e.contains(s)) e = e.parentElement;
      const r = e.getBoundingClientRect(); return [r.x, r.y, r.width, r.height].map(Math.round);
    });

    // --- Target view
    await page.locator('#tour-stage-view').getByText('Target').first().click();
    await page.waitForTimeout(2500);
    await snap('target');

    // --- side panels (each from a fresh load, so nothing carries over)
    for (const [name, label] of [['testflow', 'Test Flow'], ['instructions', 'Instructions'], ['settings', 'Settings'], ['advanced', 'Advanced']]) {
      await load();
      await page.locator('#tour-sidebar').getByRole('button', { name: label, exact: true }).click();
      await page.waitForTimeout(2200);
      await snap(name);
    }

    // --- the parts of those panels below the fold (scrolling and collapsing a
    //     section are view state, not edits)
    const openPanel = async (label) => {
      await load();
      await page.locator('#tour-sidebar').getByRole('button', { name: label, exact: true }).click();
      await page.waitForTimeout(2000);
    };
    const scrollAt = async (x, y, dy) => {
      await page.mouse.move(x, y);
      await page.mouse.wheel(0, dy);
      await page.waitForTimeout(900);
    };
    await openPanel('Instructions');
    await scrollAt(300, 600, 3000);
    await snap('instructions-2');
    await openPanel('Instructions');
    await page.getByText('Welcome Message', { exact: true }).first().click();
    await page.waitForTimeout(2200);
    await snap('instruction-detail');
    await openPanel('Settings');
    await page.getByText('Timing', { exact: true }).first().click();
    await page.getByText('Hints', { exact: true }).first().click();
    const endLinks = page.getByText('End links', { exact: true }).first();   // v1.17+
    if (await endLinks.count()) await endLinks.click();
    await page.waitForTimeout(800);
    await snap('settings-hints');

    // --- right panel: Styles tab, collapsed, then each section opened on its own
    await load();
    await page.getByRole('tab', { name: 'Styles', exact: true }).click();
    await page.waitForTimeout(1800);
    await snap('styles');
    for (const [name, label] of [['styles-palette', 'Theme Palette'], ['styles-background', 'Page Background'],
                                 ['styles-radius', 'Radius & Border'], ['styles-typography', 'Typography']]) {
      const head = page.locator('#tour-right-sidebar').getByText(label, { exact: true }).first();
      await head.click();                       // open
      await page.waitForTimeout(1200);
      await snap(name);
      await head.click();                       // and close again, so the next one opens alone
      await page.waitForTimeout(600);
    }

    // --- Device View: tablet, mobile, and the resolution list
    await load();
    await page.getByRole('button', { name: 'Tablet preview' }).click();
    await page.waitForTimeout(2200);
    await snap('device-tablet');
    await page.getByRole('button', { name: 'Mobile preview' }).click();
    await page.waitForTimeout(2200);
    await snap('device-mobile');
    await page.locator('#tour-devices button.ide-field').first().click();
    await page.waitForTimeout(900);
    await snap('device-list');

    // --- Configure Icons dialog (opened and closed; nothing in it is touched)
    await load();
    await page.locator('#tour-stage-view').getByText('Target').first().click();
    await page.waitForTimeout(2000);
    await page.locator('#tour-target-bar').getByRole('button', { name: /configure/i }).last().click();
    await page.waitForTimeout(2000);
    await snap('configure-icons');
    await page.keyboard.press('Escape');

    // --- switching a round off in Test Flow (in this throwaway tab only; never saved)
    await load();
    await page.locator('#tour-sidebar').getByRole('button', { name: 'Test Flow', exact: true }).click();
    await page.waitForTimeout(2200);
    await page.getByLabel('Practice round', { exact: true }).first().click({ force: true });
    await page.waitForTimeout(1500);
    await snap('round-off');

    // --- Quick Tour ("How it works"): the first three steps
    await load();
    await page.locator('#how-it-works-btn').click();
    await page.waitForTimeout(1500);
    await snap('tour-1');
    for (const n of [2, 3]) {
      await page.getByRole('button', { name: /^next/i }).last().click();
      await page.waitForTimeout(1300);
      await snap('tour-' + n);
    }
    await page.keyboard.press('Escape');

    // --- What's New panel
    await load();
    await page.getByRole('button', { name: /^What's New/ }).click();
    await page.waitForTimeout(2000);
    await snap('whats-new');
    await page.keyboard.press('Escape');

    // --- AI Assistant dock: its welcome screen only (no message is sent)
    await load();
    await page.getByRole('button', { name: 'Open AI Assistant' }).first().click();
    await page.waitForTimeout(2500);
    await snap('assistant');

    // --- kebab menu -> Recent changes drawer -> one version opened
    await load();
    await page.locator('#tour-save label[aria-label="More actions"]').click();
    await page.waitForTimeout(700);
    await snap('kebab');
    await page.getByRole('menuitem', { name: /Recent changes/ }).click();
    await page.waitForTimeout(2000);
    await snap('recent');
    await page.locator('.rc-row-wrap [role=button]').first().click();
    await page.waitForTimeout(1500);
    await snap('recent-detail');

  } finally {
    fs.writeFileSync(path.join(SHOTS, 'controls.json'), JSON.stringify({ controls, extra }));
    await ctx.close();
  }
})().catch((e) => { console.error(e.message); process.exit(1); });
