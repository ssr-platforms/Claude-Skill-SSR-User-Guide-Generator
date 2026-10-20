// The look-only screenshots: panels, menus and dialogs of the finished Test to populate.
//
// SAFETY: this only looks. It never presses Save, never confirms a delete, a restore or a
// theme (Apply theme saves the test), never saves an image or a theme, and never sends the
// AI Assistant a message: every dialog it opens it cancels. Each state is captured on its
// own; one that fails is logged and skipped, never fatal.
//
//   node capture.js <run.json>          (run.sh look)
const L = require('./capture-lib');

const run = L.config();
const URL = `${run.app}/tests/code/${run.target}`;

(async () => {
  const s = await L.session(run, 'controls.json');
  const { ctx, page, snap, warn, extra } = s;
  const rail = page.locator('[data-ide-tour="sidebar-core-rail"]');
  const wait = (ms) => page.waitForTimeout(ms);
  let signed = false;
  const load = async () => {
    if (!signed) { await L.signIn(page, URL, { okPath: '/tests/code/' }); signed = true; }
    else { await page.goto(URL, { waitUntil: 'networkidle', timeout: 90000 }); await wait(5000); }
    const skip = page.getByRole('button', { name: 'Skip tour' });
    if (await skip.isVisible().catch(() => false)) await skip.click();
    await wait(600);
  };
  const openPanel = async (name) => { await rail.getByText(name, { exact: true }).click(); await wait(2200); };
  const step = async (label, fn) => {
    try { await fn(); } catch (e) { warn(`look-only "${label}" skipped: ${e.message.split('\n')[0].slice(0, 160)}`); }
  };

  try {
    await step('editor', async () => {
      await load();
      await snap('ide-final');
      await page.locator('[data-ide-tour="flow-navigation"]').getByRole('button').first().click(); await wait(900);
      await snap('goto-open');
      await page.keyboard.press('Escape');
    });
    await step('tour', async () => {
      await load();
      await page.locator('[data-ide-help-tour-trigger]').click(); await wait(1600);
      await snap('tour-1');
      for (const n of [2, 3]) { await page.getByRole('button', { name: 'Next', exact: true }).last().click(); await wait(1600); await snap('tour-' + n); }
      await page.keyboard.press('Escape');
    });
    await step('whats-new', async () => {
      await load();
      await page.locator('[data-ide-tour="header-whats-new"]').click(); await wait(2000);
      await snap('whats-new');
      await page.keyboard.press('Escape');
    });
    await step('image editor', async () => {        // opened, Crop tried and cancelled; Save Image never pressed
      await load(); await openPanel('Products');
      await page.locator('[data-product-id]').first().getByRole('button', { name: 'Edit', exact: true }).click(); await wait(3000);
      await snap('editor');
      await page.getByRole('button', { name: 'Crop', exact: true }).click(); await wait(1200);
      await snap('editor-crop');
      await page.getByRole('button', { name: 'Cancel', exact: true }).last().click(); await wait(600);
      await page.getByRole('button', { name: 'Close editor' }).click();
    });
    await step('delete', async () => {             // ticked, Delete pressed, then Cancel
      await load(); await openPanel('Products');
      await page.locator('[data-product-id]').first().locator('input[type=checkbox]').check(); await wait(1200);
      await snap('del-selected');
      await page.locator('#SidebarFooter').getByRole('button', { name: 'Delete', exact: true }).click(); await wait(1200);
      await snap('del-confirm');
      await page.getByRole('button', { name: 'Cancel', exact: true }).last().click();
    });
    await step('quick access', async () => {
      await load();
      await page.getByRole('button', { name: 'Open quick access' }).click(); await wait(1500);
      await snap('quick-access');
    });
    await step('test flow', async () => { await load(); await openPanel('Test Flow'); await wait(1500); await snap('testflow'); });
    await step('instructions', async () => {
      await load(); await openPanel('Instructions');
      await snap('instructions');
      await page.mouse.move(300, 600); await page.mouse.wheel(0, 3000); await wait(900);
      await snap('instructions-2');
      await load(); await openPanel('Instructions');
      const row = page.locator('[data-instruction-target="practice"]').first();
      await (await row.count() ? row : page.locator('[data-instruction-target="main"]').first()).click(); await wait(2200);
      await snap('ins-open');
      extra.insOpen = await page.locator('[data-instruction-target="practice"]').count() ? 'practice' : 'main';
    });
    await step('questionnaire', async () => {
      await load(); await openPanel('Questionnaire');
      await snap('questionnaire');
      await page.locator('[data-question-target]').first().click(); await wait(2200);
      await snap('question-open');
    });
    await step('advanced', async () => {
      await load(); await openPanel('Advanced');
      await snap('advanced');
      await page.getByRole('tab', { name: 'JavaScript' }).click(); await wait(900);
      await snap('advanced-js');
    });
    await step('styles', async () => {
      await load();
      const shelf = page.getByRole('button', { name: 'Shelf Style', exact: true });
      if ((await shelf.getAttribute('aria-expanded')) === 'true') { await shelf.click(); await wait(800); }
      await snap('styles');
      for (const [name, label] of [['styles-modal', 'Modal Layout'], ['styles-palette', 'Theme Palette'],
                                   ['styles-radius', 'Radius & Border'], ['styles-typography', 'Typography']]) {
        const head = page.getByRole('button', { name: label, exact: true });
        await head.click(); await wait(1200); await snap(name); await head.click(); await wait(700);
      }
    });
    await step('themes', async () => {             // the Apply dialog is cancelled: Apply theme saves the test
      await load(); await openPanel('Themes'); await wait(2500);
      await snap('themes');
      const apply = page.getByRole('button', { name: /^Apply .+ to this study$/ }).first();
      extra.theme = ((await apply.getAttribute('aria-label')) || '').replace(/^Apply /, '').replace(/ to this study$/, '');
      await apply.click(); await wait(1500);
      await snap('theme-apply');
      await page.getByRole('button', { name: 'Cancel', exact: true }).last().click();
    });
    await step('save as theme', async () => {      // named, then Cancel
      await load();
      await page.getByRole('button', { name: 'More save options' }).click(); await wait(900);
      await snap('kebab');
      await page.getByText('Save as theme', { exact: true }).click(); await wait(3500);
      await page.getByPlaceholder(/Supermarket wood shelf/).fill(`${run.target} shelf`); await wait(500);
      await snap('save-theme-named');
      await page.getByRole('button', { name: 'Cancel', exact: true }).last().click();
    });
    await step('recent changes', async () => {     // a version opened, Restore pressed, then Cancel — never Restore
      await load();
      await page.getByRole('button', { name: 'More save options' }).click(); await wait(800);
      await page.getByText('Recent changes', { exact: true }).click(); await wait(2500);
      await snap('recent');
      await page.locator('tbody tr').first().click(); await wait(1500);
      await snap('recent-detail');
      await page.getByRole('button', { name: 'Restore', exact: true }).first().click(); await wait(1200);
      await snap('recent-confirm');
      await page.getByRole('button', { name: 'Cancel', exact: true }).last().click();
    });
    await step('devices', async () => {
      await load();
      await page.getByRole('button', { name: 'Tablet', exact: true }).click(); await wait(2500); await snap('device-tablet');
      await page.getByRole('button', { name: 'Mobile', exact: true }).click(); await wait(2500); await snap('device-mobile');
      await page.getByRole('button', { name: 'Screen dimensions' }).click(); await wait(900); await snap('device-list');
      await page.keyboard.press('Escape');
    });
    await step('simulate', async () => {           // runs in the preview; nothing is recorded
      await load();
      await page.locator('[data-ide-tour="simulate"]').click(); await wait(3000);
      if (await page.getByText('Before you simulate').isVisible().catch(() => false)) {
        await snap('sim-preflight');
        await page.getByRole('button', { name: 'Simulate anyway' }).click();
      }
      await wait(7000); await snap('sim-run');
      await page.getByRole('button', { name: 'Back to editing' }).first().click().catch(() => {});
    });
    await step('preview', async () => {            // the live page, in a new tab
      await load();
      const pop = ctx.waitForEvent('page', { timeout: 15000 }).catch(() => null);
      await rail.getByText('Preview', { exact: true }).click(); await wait(2000);
      if (await page.getByText('Open a version of your test').isVisible().catch(() => false)) {
        await snap('preview-modal');
        await page.getByRole('button', { name: /Open live page/ }).click();
      }
      const p = await pop;
      if (p) { await p.waitForLoadState('networkidle', { timeout: 60000 }).catch(() => {}); await p.waitForTimeout(9000); await snap('preview-live', p); await p.close(); }
    });
    await step('assistant', async () => {          // its welcome screen only: no message is sent
      await load();
      await page.locator('[data-ide-tour="ai-assistant-trigger"]').click(); await wait(2500);
      await snap('assistant');
    });
  } finally {
    await s.finish();
  }
})().catch((e) => { console.error(e.message.slice(0, 400)); process.exit(1); });
