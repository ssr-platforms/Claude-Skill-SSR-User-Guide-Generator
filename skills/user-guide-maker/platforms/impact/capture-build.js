// Builds the guide's demo test FROM SCRATCH in the IDE, screenshotting every step.
//
// Runs against the demo test only (default SO2GKM679H, "Snack Shelf Test"), which
// reset-test.sh puts back to the blank state a new IMPACT component starts in. It
// follows the user's own project (ABUVANIDYQ): same stimulus image from the
// survey's gallery, a 30x20 grid, the products painted active, priority cells,
// 50 trials, the explicit round on, the Crosscut target. Unlike capture.js it DOES
// edit and save — but only this demo test, never ABUVANIDYQ.
//
//   node capture-build.js <shotsDir> [demoCode]
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
const STIMULUS = 'Screenshot (7) edited';            // the gallery image ABUVANIDYQ uses
const WELCOME = 'Welcome to IMPACT! Thank you for taking part in this survey. Your feedback is very important to us.';

// The packs on the stimulus, in CSS px of the stage (image spans y 354-766 at this viewport)
const TOP_SHELF = [[526, 372, 634, 526], [662, 372, 760, 526], [794, 372, 902, 526], [942, 372, 1048, 526], [1082, 372, 1170, 526]];
const BOTTOM_SHELF = [[538, 574, 634, 718], [666, 574, 754, 718], [794, 574, 884, 718], [914, 574, 1016, 718], [1042, 574, 1154, 718]];
const LOGO_STROKES = { x0: 548, x1: 620, ys: [392, 412, 432] };   // across the "Chippy" logo
const GROUPS = ['Chippy', 'Chiz Curls', 'Cracklings', 'Crispy Patata', 'Mr. Chips', 'Nova', 'NutriStar', 'Piatos', 'Ri-Chee', 'SweetCorn'];

fs.mkdirSync(SHOTS, { recursive: true });
const dump = (page) => page.evaluate(() => {
  const vis = (e) => { const r = e.getBoundingClientRect(); const st = getComputedStyle(e);
    return r.width > 2 && r.height > 2 && r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < innerWidth && st.visibility !== 'hidden' && st.opacity !== '0'; };
  const sel = '[data-instruction-target],[role=status],button,a,input,select,textarea,label,img,iframe,h1,h2,h3,h4,li,[role],[id^=tour-],.ProseMirror,[class*=rc-],[class*=ide-menu],[class*=bar-group],[class*=tool-group]';
  return [...document.querySelectorAll(sel)].filter(vis).map((e) => { const r = e.getBoundingClientRect(); const cls = typeof e.className === 'string' ? e.className : '';
    return { t: e.tagName.toLowerCase(), id: e.id || '', role: e.getAttribute('role') || '',
      c: cls.split(/\s+/).filter((c) => /^(tool|bar|flow|stage|ide|vue-flow|rc-|ProseMirror)/.test(c)).join(' '),
      s: (e.getAttribute('aria-label') || e.getAttribute('title') || e.innerText || e.value || e.getAttribute('placeholder') || '').replace(/\s+/g, ' ').trim().slice(0, 90),
      b: [r.x, r.y, r.width, r.height].map((v) => Math.round(v)) }; });
});

(async () => {
  const { ctx, page } = await open();
  const controls = {}, extra = {};
  page.on('pageerror', (e) => console.log('PAGEERROR', e.message.slice(0, 160)));
  const snap = async (name, p = page) => {
    if (p === page) await page.mouse.move(800, 3);
    await p.waitForTimeout(900);
    await p.screenshot({ path: path.join(SHOTS, name + '.png') });
    controls[name] = await dump(p);
    console.log('captured', name);
  };
  const box = async (loc) => { const b = await loc.first().boundingBox(); return b && [b.x, b.y, b.width, b.height].map(Math.round); };
  const drag = async ([x0, y0, x1, y1]) => {
    await page.mouse.move(x0, y0); await page.mouse.down();
    await page.mouse.move(x1, y1, { steps: 15 }); await page.mouse.up();
    await page.waitForTimeout(350);
  };
  const save = async () => {
    if (DRY) { console.log('(dry run: not saved)'); return; }
    await page.getByRole('button', { name: /^save$/i }).click();
    await page.waitForTimeout(3500);
  };

  try {
    let url = URL;
    const tokenFile = path.join(W, '.token');   // spent once; see profile.md   // a one-time Fluent sign-in token, spent here if present
    if (fs.existsSync(tokenFile)) { url += '?uid=' + fs.readFileSync(tokenFile, 'utf8').trim(); fs.unlinkSync(tokenFile); }
    await page.goto(url, { waitUntil: 'networkidle', timeout: 90000 });
    await page.waitForTimeout(2500);
    if (!page.url().includes('/survey/') || /verification|not defined|login/i.test(await page.title())) throw new Error('Not signed in: see PROGRESS.md');
    const skip = page.getByRole('button', { name: 'Skip tour' });
    if (await skip.isVisible().catch(() => false)) await skip.click();
    await page.locator('#tour-stage-view').getByText('Stimuli').first().click();
    await page.waitForTimeout(1200);

    // ---- How do I add a stimulus?
    await snap('new-test');
    await page.getByRole('button', { name: /PICK FROM THE GALLERY/i }).first().click();
    await page.waitForTimeout(3000);
    await snap('add-gallery');
    await page.getByText(STIMULUS, { exact: true }).first().click();
    await page.waitForTimeout(800);
    await snap('add-selected');
    await page.getByRole('dialog').getByRole('button', { name: 'Add', exact: true }).click();
    await page.waitForTimeout(3500);
    await snap('add-done');

    // ---- How do I set up the stimulus grid?
    const name = page.getByRole('textbox', { name: 'Stimulus name' });
    await name.click(); await name.fill('Snack Shelf'); await page.keyboard.press('Tab');
    await snap('grid-name');
    await page.locator('#stim-columns').fill('30'); await page.keyboard.press('Tab');
    await page.locator('#stim-rows').fill('20'); await page.keyboard.press('Tab');
    await page.waitForTimeout(1500);
    await snap('grid-size');

    // ---- How do I paint active cells?
    await page.locator('#tour-toolbar').getByRole('button', { name: 'Box' }).click();
    await snap('active-box');
    await page.locator('#tour-toolbar').getByRole('button', { name: 'Active', exact: true }).click();
    await snap('active-mark');
    for (const r of TOP_SHELF) await drag(r);
    await snap('active-top');
    for (const r of BOTTOM_SHELF) await drag(r);
    await snap('active-bottom');
    extra.topShelf = TOP_SHELF; extra.bottomShelf = BOTTOM_SHELF;

    // ---- How do I paint priority cells?
    await page.locator('#tour-toolbar').getByRole('button', { name: 'Brush' }).click();
    await snap('prio-brush');
    await page.locator('#tour-toolbar').getByRole('button', { name: 'Priority', exact: true }).click();
    await snap('prio-mark');
    for (const y of LOGO_STROKES.ys) {
      await page.mouse.move(LOGO_STROKES.x0, y); await page.mouse.down();
      await page.mouse.move(LOGO_STROKES.x1, y, { steps: 12 }); await page.mouse.up();
      await page.waitForTimeout(200);
    }
    await snap('prio-paint');
    extra.logo = LOGO_STROKES;

    // ---- How do I set the trials and the explicit round?
    await page.locator('#stim-max_trial_size').fill('50'); await page.keyboard.press('Tab');
    await page.waitForTimeout(800);
    await snap('trials');
    await page.locator('#tour-stimuli input[type="checkbox"]').last().click();
    await page.waitForTimeout(800);
    await snap('explicit');
    extra.explicitToggle = await box(page.locator('#tour-stimuli input[type="checkbox"]').last());

    // ---- How do I create cell groups?  One group per pack, named as in ABUVANIDYQ.
    await page.locator('#tour-toolbar').getByRole('button', { name: 'Cell Groups', exact: true }).click();
    await page.locator('#tour-toolbar').getByRole('button', { name: 'Box' }).click();
    await page.waitForTimeout(800);
    await snap('groups-scope');
    const packs = [...TOP_SHELF, ...BOTTOM_SHELF];
    for (let i = 0; i < GROUPS.length; i++) {
      await page.locator('#tour-right-sidebar').getByRole('button', { name: /new group/i }).last().click();
      await page.waitForTimeout(900);
      if (i === 0) await snap('groups-new');
      await page.getByPlaceholder('Logo, Brand Name, Mascot…').fill(GROUPS[i]);
      if (i === 0) await snap('groups-named');
      await page.getByRole('button', { name: 'Create group', exact: true }).click();
      await page.waitForTimeout(900);
      await drag(packs[i]);
      await page.waitForTimeout(500);
      if (i === 0) await snap('groups-first');
      // the panel stays in "Assigning <group>" until Done; New group only returns after it
      await page.locator('#tour-right-sidebar').getByRole('button', { name: /done/i }).last().click();
      await page.waitForTimeout(700);
    }
    await page.waitForTimeout(800);
    await snap('groups-all');
    // back to painting active/priority, so later screenshots show the cells
    await page.locator('#tour-toolbar').getByRole('button', { name: 'Target Cells', exact: true }).click();
    await page.waitForTimeout(800);
    await save();                                     // version 1 in Recent Changes

    // ---- How do I choose the target?
    await snap('target-tab');
    await page.locator('#tour-stage-view').getByText('Target').first().click();
    await page.waitForTimeout(2200);
    await page.locator('#tour-target-bar .bar-group').first().locator('button').first().click();
    await page.waitForTimeout(900);
    await snap('target-picker');
    const option = page.getByRole('option', { name: 'Crosscut' });
    if (await option.count()) await option.first().click(); else await page.getByText('Crosscut', { exact: true }).last().click();
    await page.waitForTimeout(800);
    for (const id of ['#target-strength', '#distractor-strength']) {
      await page.locator(id).evaluate((el) => {
        const v = Number(el.min || 0) + (Number(el.max || 100) - Number(el.min || 0)) * 0.5;
        const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
        set.call(el, String(v)); el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true }));
      });
    }
    await page.waitForTimeout(1200);
    await snap('target-set');

    // ---- How do I edit the welcome message?
    await page.locator('#tour-stage-view').getByText('Stimuli').first().click();
    await page.waitForTimeout(1200);
    await snap('ins-rail');
    await page.locator('#tour-sidebar').getByRole('button', { name: 'Instructions', exact: true }).click();
    await page.waitForTimeout(2000);
    await snap('ins-list');
    await page.getByText('Welcome Message', { exact: true }).first().click();
    await page.waitForTimeout(2200);
    await snap('ins-open');
    const editor = page.locator('.ProseMirror').first();
    await editor.click(); await page.keyboard.press('Control+A'); await page.keyboard.type(WELCOME, { delay: 5 });
    await page.waitForTimeout(1200);
    await snap('ins-edited');

    // ---- How do I save the test?  (closes the panel first so the header is clear)
    await page.locator('#tour-sidebar').getByRole('button', { name: 'Instructions', exact: true }).click();
    await page.waitForTimeout(1000);
    await snap('save-before');
    await save();
    await snap('save-after');

    // ---- How do I preview the test?  (Preview opens the saved test in the Engine, in a new tab)
    await snap('preview-rail');
    const [popup] = await Promise.all([
      ctx.waitForEvent('page'),
      page.locator('#tour-sidebar').getByRole('button', { name: 'Preview', exact: true }).click(),
    ]);
    await popup.waitForLoadState('networkidle', { timeout: 60000 }).catch(() => {});
    // the welcome card slides in: wait for its button, then for the animation to settle
    await popup.getByText(/START/i).first().waitFor({ state: 'visible', timeout: 30000 }).catch(() => {});
    await popup.waitForTimeout(4000);
    await snap('preview-engine', popup);
    extra.previewUrl = popup.url();
    await popup.close();
  } finally {
    fs.writeFileSync(path.join(SHOTS, 'build-controls.json'), JSON.stringify({ controls, extra }));
    await ctx.close();
  }
})().catch((e) => { console.error(e.message.slice(0, 400)); process.exit(1); });
