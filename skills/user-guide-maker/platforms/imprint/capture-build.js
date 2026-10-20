// Builds the Test to populate FROM SCRATCH in the IMPRINT editor, following the plan that
// plan.js worked out from the Test to clone, and screenshots every step the guide shows.
//
//   node capture-build.js <run.json>        (run.sh capture [--dry] writes run.json)
//
// Phase A — products a category at a time (gallery pick, category, names, prices, layers,
//   items per layer, roles), variants on the cards, shelves for each device, the shelf's look,
//   each pack's height on the shelf.                                     -> Save #1
// Phase B — the practice round, the search task and warnings, screen text, the test flow,
//   the questionnaire, custom code.                                      -> Save #2
// With "dry": true nothing is ever saved: both phases run in one page and the page is closed.
// It refuses a Test to populate that is not blank, and never touches the Test to clone.
const fs = require('fs');
const path = require('path');
const L = require('./capture-lib');

const run = L.config();
const plan = JSON.parse(fs.readFileSync(run.plan, 'utf8'));
if (!run.target || run.target === run.clone) throw new Error('the Test to populate must be a different test from the Test to clone');
const URL = `${run.app}/tests/code/${run.target}`;
const DEVICES = [['Desktop', 'pc', ''], ['Tablet', 'tablet', 'tab'], ['Mobile', 'mobile', 'mobile']];
const HEIGHT_KEY = { pc: 'height', tablet: 'tabHeight', mobile: 'mobileHeight' };
const SEARCH_TYPES = ['Product', 'Category', 'Variant'];

(async () => {
  const s = await L.session(run, 'build-controls.json');
  const { page, snap, warn, extra } = s;
  const gallery = () => page.locator('#fluentGalleryDialog');
  const batch = () => page.locator('#batchAddDialog');
  const rail = page.locator('[data-ide-tour="sidebar-core-rail"]');
  const wait = (ms) => page.waitForTimeout(ms);
  const esc = (x) => String(x).replace(/\\/g, '\\\\').replace(/"/g, '\\"');
  const state = () => L.readStore(page, 'storeData', 'data');
  const openPanel = async (name) => { await rail.getByText(name, { exact: true }).click(); await wait(1800); };
  const closePanel = async () => {
    const x = page.getByRole('button', { name: /^Close .+ panel$/ }).first();
    if (await x.isVisible().catch(() => false)) { await x.click(); await wait(1200); }
  };
  const device = async (name) => { await page.getByRole('button', { name, exact: true }).first().click(); await wait(2500); };
  const round = async (name) => { await page.locator('#SidebarController').getByRole('button', { name, exact: true }).click(); await wait(1200); };
  const setNumber = async (input, value) => {
    await input.click(); await input.fill(String(value)); await input.press('Enter'); await input.press('Tab'); await wait(500);
  };
  const reEsc = (x) => String(x).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  // the number box of the slider labelled `label` (labels may carry a device icon after the text)
  const numberAfter = (label) => page.getByText(new RegExp('^\\s*' + reEsc(label))).first().locator('xpath=following::input[@type="number"][1]');
  const typeColour = async (hex8) => {
    const hexIn = page.locator('.vc-color-input input').last();
    await hexIn.click(); await hexIn.fill(hex8); await hexIn.press('Enter'); await wait(600);
  };
  const closePicker = async () => {
    const head = page.getByText(/Color Picker$/).last();
    if (await head.isVisible().catch(() => false)) await head.locator('xpath=following::button[1]').click();
    await wait(500);
  };
  const pickColour = async (label, nth, value) => {
    const hex = await L.toHex8(page, value);
    if (!hex) return warn(`could not read the colour "${value}" for ${label}`);
    const btn = page.getByRole('button', { name: `Choose ${label}`, exact: true }).nth(nth);
    if (!(await btn.count())) return warn(`no "${label}" colour swatch found`);
    await btn.scrollIntoViewIfNeeded(); await btn.click(); await wait(900);
    await typeColour(hex);
  };
  const setToggle = async (label, on) => {
    const box = page.getByText(label, { exact: true }).first().locator('xpath=ancestor::label[1]//input[@type="checkbox"]');
    if (!(await box.count())) return warn(`no "${label}" switch found`);
    if ((await box.isChecked()) !== on) { await box.click({ force: true }); await wait(600); }
  };
  const setRich = async (editor, htmlText) => {   // a TipTap editor: replace its content, keeping the formatting
    const ok = await editor.evaluate((el, h) => {
      const ed = el.editor;
      if (!ed) return false;
      ed.commands.setContent(h, { emitUpdate: true });
      return true;
    }, htmlText).catch(() => false);
    if (!ok) {
      await editor.click(); await page.keyboard.press('Control+A');
      await page.keyboard.type(String(htmlText).replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim(), { delay: 3 });
    }
    await wait(300);
  };
  const dismiss = async () => {                   // "That picture is already on this shelf"
    const got = page.getByRole('button', { name: 'Got it', exact: true });
    if (await got.isVisible().catch(() => false)) { warn('a picture was already in the round and was left out'); await got.click(); await wait(800); }
  };
  // cosmetic steps warn and carry on; the core of the test (products, rounds, settings, questions) stops the run
  const optional = async (label, fn) => {
    try { await fn(); } catch (e) { warn(`${label} not copied: ${e.message.split('\n')[0].slice(0, 160)}`); await page.keyboard.press('Escape').catch(() => {}); }
  };
  const save = async (shotBefore, shotAfter) => {
    if (shotBefore) await snap(shotBefore);
    if (run.dry) { console.log('(dry run: not saved)'); return; }
    await page.locator('[data-ide-tour="save-actions"]').getByRole('button', { name: /^(Save|Live Now)$/ }).click();
    await wait(5000);
    if (shotAfter) await snap(shotAfter);
    const close = page.getByRole('button', { name: 'Close', exact: true });
    if (await close.isVisible().catch(() => false)) { await close.click(); await wait(1000); }
  };

  // ------------------------------------------------------------------ products, a gallery pick at a time
  const created = { category: new Set(), variant: new Set() };
  async function pickImages(items, shots) {
    await page.getByRole('button', { name: 'New product' }).first().click();
    await wait(3500);
    if (shots) await snap('add-gallery');
    let tab = null;
    for (const it of items) {
      if (it.tab !== tab) {
        tab = it.tab;
        await gallery().getByText(tab, { exact: false }).first().click();
        await wait(2800);
        if (shots && it === items[0]) await snap('add-project');
      }
      if (tab === 'Public') {
        const search = gallery().getByPlaceholder(/Search/);
        await search.fill(it.gallery); await wait(2500);
      }
      let tile = gallery().locator(`button:has(img[src="${esc(it.thumb)}"])`).first();
      if (!(await tile.count())) tile = gallery().getByText(it.gallery, { exact: true }).first();
      if (!(await tile.count())) { warn(`"${it.gallery}" is not in the gallery's ${tab} tab: ${it.name} skipped`); it.skipped = true; continue; }
      await tile.scrollIntoViewIfNeeded(); await tile.click(); await wait(250);
    }
    if (shots) {                                   // show the picks: back to the first image's tab
      if (items[0].tab !== tab) { await gallery().getByText(items[0].tab, { exact: false }).first().click(); await wait(2500); }
      if (items[0].tab === 'Public') { await gallery().getByPlaceholder(/Search/).fill(items[0].gallery); await wait(2500); }
      const firstTile = gallery().locator(`button:has(img[src="${esc(items[0].thumb)}"])`).first();
      if (await firstTile.count()) await firstTile.evaluate((e) => e.scrollIntoView({ block: 'center' }));
      await wait(600);
      await snap('add-selected');
    }
    await page.getByRole('button', { name: /^Add \d+ images?$/ }).click();
    await wait(2500);
    // tag each row with its product's name, in pick order
    const names = items.filter((i) => !i.skipped).map((i) => i.name);
    await page.evaluate((nm) => {
      const inputs = [...document.querySelectorAll('#batchAddDialog input')].filter((i) => i.value && i.placeholder !== '0.00' && i.type === 'text');
      inputs.forEach((inp, k) => {
        let e = inp; while (e && !e.querySelector('[aria-label="Remove"]')) e = e.parentElement;
        if (e && nm[k]) e.setAttribute('data-guide-row', nm[k]);
      });
    }, names);
  }
  async function chooseCategory(name, shots) {
    await batch().getByRole('button', { name: 'N/A' }).first().click();
    await wait(1000);
    if (shots) await snap('cat-open');
    if (!created.category.has(name)) {
      await page.getByText(/^\+?\s*Add category$/i).first().click();
      await wait(1500);
      if (shots) await snap('cat-modal');
      const box = page.getByPlaceholder('e.g. Snacks');
      await box.fill(name); await wait(400);
      if (shots) await snap('cat-typed');
      await box.locator('xpath=following::button[1]').click();
      await wait(1500);
      if (shots) await snap('cat-added');
      created.category.add(name);
    }
    await page.getByRole('button', { name, exact: true }).last().click();      // chooses it (and closes the pop-up)
    await wait(1000);
    if (await page.getByText('Select Category', { exact: true }).isVisible().catch(() => false)) {
      await page.getByText('Select Category', { exact: true }).locator('xpath=following::button[1]').click();
      await wait(800);
    }
    if (shots) await snap('cat-applied');
  }
  async function fillRows(items) {
    for (const it of items) {
      if (it.skipped) continue;
      const row = batch().locator(`[data-guide-row="${esc(it.name)}"]`);
      if (!(await row.count())) { warn(`no row for ${it.name} in New Products`); continue; }
      if (it.gallery !== it.name) await row.locator('input[type=text]').first().fill(it.name);
      if (it.price !== '') await row.getByPlaceholder('0.00').fill(it.price);
      const plus = row.getByRole('button', { name: '+', exact: true });
      for (let i = 1; i < it.layers; i++) await plus.nth(0).click();
      for (let i = 1; i < it.count; i++) await plus.nth(1).click();
      if (it.type === 0) await row.getByRole('button', { name: 'Filler', exact: true }).click();
      if (Object.keys(it.overrides || {}).length) warn(`${it.name} has its own layers / items per layer on tablet or mobile — not copied`);
      await wait(100);
    }
  }
  async function addBatches(batches, shots) {
    for (let bi = 0; bi < batches.length; bi++) {
      const b = batches[bi];
      const first = shots && bi === 0;
      await pickImages(b.items, first);
      if (first) await snap('new-products');
      if (b.category) await chooseCategory(b.category, first);
      await fillRows(b.items);
      await wait(500);
      if (first) {   // the list scrolls: its top (names, prices), then its foot
        const live = b.items.filter((i) => !i.skipped);
        await batch().locator(`[data-guide-row="${esc(live[0].name)}"]`).evaluate((e) => e.scrollIntoView({ block: 'nearest' }));
        await wait(500); await snap('np-filled');
        await batch().locator(`[data-guide-row="${esc(live[live.length - 1].name)}"]`).evaluate((e) => e.scrollIntoView({ block: 'nearest' }));
        await wait(500); await snap('np-filled-2');
      }
      await batch().getByRole('button', { name: /^Add \d+ products?$/ }).click();
      await wait(3000);
      await dismiss();
      if (first) await snap('np-progress');
      const done = page.getByRole('button', { name: 'Done', exact: true });
      await done.waitFor({ state: 'visible', timeout: 60000 }).catch(() => {});
      if (await done.isVisible().catch(() => false)) await done.click();
      await wait(2500);
      await dismiss();
    }
  }

  try {
    await L.signIn(page, URL, { okPath: '/tests/code/' });
    const skip = page.getByRole('button', { name: 'Skip tour' });
    if (await skip.isVisible().catch(() => false)) await skip.click();
    await wait(800);
    const before = await state();
    if ((before.products || []).length || (before.prac_products || []).length) {
      throw new Error(`${run.target} is not blank (${(before.products || []).length} products): the Test to populate must be a new, empty test`);
    }
    await snap('new-test');

    // ================================================================ PHASE A
    await openPanel('Products');
    await snap('products-empty');
    await addBatches(plan.main, true);
    await wait(1500);
    await snap('products-full');

    // ---- variants, on the product cards
    await page.evaluate(() => document.querySelectorAll('[data-product-id]').forEach((c) => {
      const n = c.querySelector('input[type=text]'); if (n) c.setAttribute('data-guide-card', n.value);
    }));
    let firstVariant = true;
    for (const v of plan.variants) {
      for (const product of v.products) {
        const card = page.locator(`[data-guide-card="${esc(product)}"]`);
        if (!(await card.count())) { warn(`no card for ${product} to give it the variant ${v.name}`); continue; }
        await card.scrollIntoViewIfNeeded(); await wait(500);
        if (firstVariant) { await snap('var-card'); extra.variantCard = product; }
        const chip = card.locator('div.grid', { has: page.getByText('Variant', { exact: true }) }).locator('.glass-well').first();
        await chip.click(); await wait(1500);
        if (firstVariant) await snap('var-modal');
        if (!created.variant.has(v.name)) {
          const box = page.getByPlaceholder('e.g. Zero Sugar');
          await box.fill(v.name); await wait(400);
          if (firstVariant) await snap('var-typed');
          await box.locator('xpath=following::button[1]').click(); await wait(1500);
          if (firstVariant) await snap('var-added');
          created.variant.add(v.name);
        }
        await page.getByRole('button', { name: v.name, exact: true }).last().click(); await wait(1200);
        if (await page.getByText('Select Variant', { exact: true }).isVisible().catch(() => false)) {
          await page.getByText('Select Variant', { exact: true }).locator('xpath=following::button[1]').click(); await wait(800);
        }
        if (firstVariant) { await snap('var-applied'); firstVariant = false; }
      }
    }
    await closePanel();

    // ---- shelves and products per shelf, for each device and round
    await openPanel('Settings');
    for (const [label, key] of [['Main Round', 'main'], ['Practice Round', 'practice']]) {
      const want = plan.settings[key];
      if (!want || want.shelves == null) continue;
      await round(label);
      for (const [dev, , pre] of DEVICES) {
        await device(dev);
        const shot = key === 'main' ? `set-${dev.toLowerCase()}` : null;
        if (shot) await snap(shot + '-before');
        const sk = pre ? pre + 'Shelves' : 'shelves', pk = pre ? pre + 'ProductsPerShelves' : 'productsPerShelves';
        if (want[sk] != null) await setNumber(numberAfter('Number of shelves'), want[sk]);
        if (want[pk] != null) await setNumber(numberAfter('Products per shelf'), want[pk]);
        await wait(1200);
        if (shot) await snap(shot);
      }
    }
    await round('Main Round'); await device('Desktop');
    await closePanel();

    // ---- the shelf's look (Style panel): only what differs from the Test to populate
    const st = plan.style;
    const styles = page.locator('[data-ide-tour="style-sections"]');
    await snap('look-before');
    await optional('the backdrop', async () => {
    if (st.backdrop && st.backdrop.type === 'color') {
      await page.getByRole('tab', { name: 'Plain colour' }).click(); await wait(1500);
      await snap('bg-plain');
      const hex = await L.toHex8(page, st.backdrop.color);
      const swatch = await page.evaluate((h) => {
        const toHex = (c) => { const m = /rgba?\(([^)]+)\)/.exec(c); if (!m) return ''; const [r, g, b] = m[1].split(',').map((x) => parseInt(x, 10)); return [r, g, b].map((n) => n.toString(16).padStart(2, '0')).join(''); };
        const r = [...document.querySelectorAll('button[role=radio].backdrop-swatch, [role=radiogroup] button[role=radio]')]
          .find((b) => toHex(getComputedStyle(b).backgroundColor) === h.slice(0, 6));
        return r ? r.getAttribute('aria-label') : null;
      }, hex);
      if (swatch) { await page.getByRole('radio', { name: swatch, exact: true }).click(); extra.backdrop = { mode: 'swatch', label: swatch }; }
      else {
        await page.getByRole('button', { name: 'Choose', exact: true }).first().click(); await wait(900);
        await typeColour(hex); await closePicker(); extra.backdrop = { mode: 'custom', label: '#' + hex.slice(0, 6).toUpperCase() };
      }
      await wait(1500); await snap('bg-picked');
    } else if (st.backdrop && st.backdrop.type === 'image') {
      await page.getByRole('tab', { name: 'Picture' }).click(); await wait(1200);
      await page.getByRole('button', { name: 'Grid view' }).click(); await wait(1200);
      await snap('bg-grid');
      const imgs = styles.locator(`img[src*="${esc(st.backdrop.image)}"]`);
      let picked = false;
      for (let i = 0; i < await imgs.count() && !picked; i++) {
        const im = imgs.nth(i);
        if (await im.isVisible()) { await im.scrollIntoViewIfNeeded(); await im.click(); picked = true; }
      }
      for (let i = 0; !picked && i < 60; i++) {    // carousel view: step to it
        const next = page.getByRole('button', { name: 'Next background' }).last();
        if (!(await next.count())) break;
        await next.click(); await wait(400);
        for (let k = 0; k < await imgs.count() && !picked; k++) if (await imgs.nth(k).isVisible()) { await imgs.nth(k).click(); picked = true; }
      }
      if (picked) { await wait(1500); extra.backdrop = { mode: 'image' }; }
      else warn(`the backdrop picture ${st.backdrop.image} was not found in the background library`);
      if (st.backdrop.brightness != null) await setNumber(numberAfter('Brightness'), Math.round(st.backdrop.brightness * 100));
      await snap('bg-picked');
    }
    });
    const fr = st.frame;
    await optional('the shelf frame', async () => {
    if (fr.colours.length || fr.numbers.length || fr.toggles.length) {
      const anchor = page.getByRole('button', { name: 'Choose Front Color' }).first();
      if (await anchor.count()) { await anchor.scrollIntoViewIfNeeded(); await wait(600); }
      await snap('frame-section');
      for (const t of fr.toggles) await setToggle(t.label, t.on);
      let firstC = true;
      for (const c of fr.colours) {
        await pickColour(c.label, c.nth, c.value);
        if (firstC) { await snap('frame-picker'); extra.framePicker = c.label; firstC = false; }
      }
      await closePicker();
      for (const n of fr.numbers) await setNumber(numberAfter(n.label), n.value);
      await snap('frame-done');
      if (fr.deviceDepth.tablet != null || fr.deviceDepth.mobile != null) warn('the Test to clone sets its own top depth on tablet or mobile — not copied');
    }
    });
    await optional('the posts', async () => {
    if (st.post.colours.length || st.post.show != null) {
      const anchor = page.getByRole('button', { name: 'Choose Background Color' }).first();
      if (await anchor.count()) await anchor.scrollIntoViewIfNeeded();
      if (st.post.show != null) await setToggle('Show post area', st.post.show);
      for (const c of st.post.colours) await pickColour(c.label, c.nth, c.value);
      await closePicker();
      await snap('post-done');
    }
    });
    const pt = st.pricetag;
    await optional('the price tags', async () => {
    if (pt.currency || pt.colours.length || pt.blur != null) {
      if (pt.currency) {
        const sel = page.getByText('Currency', { exact: true }).first().locator('xpath=following::button[1]');
        await sel.scrollIntoViewIfNeeded(); await sel.click(); await wait(800);
        const opt = page.getByRole('option', { name: new RegExp(`\\(${pt.currency}\\)`) }).first();
        if (await opt.count()) await opt.click();
        else { const o2 = page.getByText(new RegExp(`\\(${pt.currency}\\)`)).last(); if (await o2.count()) await o2.click(); else warn(`currency ${pt.currency} not found`); }
        await wait(800);
        if (pt.custom) {
          const left = page.getByText('Left Symbol', { exact: true }).locator('xpath=following::input[1]');
          const right = page.getByText('Right Symbol', { exact: true }).locator('xpath=following::input[1]');
          if (await left.count()) await left.fill(pt.custom.left);
          if (await right.count()) await right.fill(pt.custom.right);
        }
      }
      for (const c of pt.colours) await pickColour(c.label, c.nth, c.value);
      await closePicker();
      if (pt.blur != null) await setToggle('Blur Content', pt.blur);
      await snap('price-done');
    }
    });
    const section = async (name, fn) => {
      const head = page.getByRole('button', { name, exact: true }).first();
      await head.scrollIntoViewIfNeeded(); await head.click(); await wait(1200);
      try { await fn(); } catch (e) { warn(`${name}: ${e.message.split('\n')[0]}`); }
      await head.click(); await wait(600);
    };
    if (st.palette.length) await section('Theme Palette', async () => { for (const c of st.palette) await pickColour(c.label, c.nth, c.value); await closePicker(); });
    if (st.radius.length) await section('Radius & Border', async () => {
      for (const r of st.radius) await page.getByRole('button', { name: `${r.group} — ${r.label}`, exact: true }).click();
    });
    if (st.font) await section('Typography', async () => {
      await page.getByText('Font family', { exact: true }).locator('xpath=following::button[1]').click(); await wait(800);
      const o = page.getByRole('option', { name: new RegExp('^' + st.font) }).first();
      if (await o.count()) await o.click(); else { const t2 = page.getByText(new RegExp('^' + st.font)).last(); if (await t2.count()) await t2.click(); else warn(`font ${st.font} not offered`); }
    });
    if (Object.keys(st.modal).length) await section('Modal Layout', async () => {
      if (st.modal.fontSize != null) { const i = page.getByText('Font Size', { exact: false }).first().locator('xpath=following::input[1]'); await i.fill(String(st.modal.fontSize)); await i.press('Enter'); }
      if (st.modal.lineHeight != null) { const i = page.getByText('Line Height', { exact: true }).first().locator('xpath=following::input[1]'); await i.fill(String(st.modal.lineHeight)); await i.press('Enter'); }
      if (st.modal.shadow != null) await setNumber(numberAfter('Shadow'), st.modal.shadow);
    });
    await styles.evaluate((e) => e.scrollTo(0, 0));

    // ---- each pack's height on the shelf, for each device that has one
    await optional('pack heights', async () => {
    const frame = page.frameLocator('iframe.iframe-container');
    const all = plan.main.flatMap((b) => b.items).filter((i) => !i.skipped);
    let shown = false;
    for (const [dev, key] of DEVICES) {
      const todo = all.filter((i) => i.heights && i.heights[key] != null);
      if (!todo.length) continue;
      await device(dev);
      let pxPerPct = 4 * 0.59;                       // learned from each drag: the preview is scaled down
      const idOf = Object.fromEntries((await state()).products.map((p) => [p.name, p.id]));
      const heightOf = async (name) => {
        const p = (await state()).products.find((q) => q.name === name);
        return parseFloat(p?.style?.[HEIGHT_KEY[key]]) || parseFloat(p?.style?.height) || 90;
      };
      for (const it of todo) {
        const target = it.heights[key];
        for (let attempt = 0; attempt < 4; attempt++) {
          const now = await heightOf(it.name);
          if (Math.abs(now - target) < 0.8) break;
          const prod = frame.locator(`.prod[data-fit-id="${idOf[it.name]}"]`);
          if (!(await prod.count())) { warn(`${it.name} is not on the ${dev.toLowerCase()} shelf: its height was not set`); break; }
          await prod.scrollIntoViewIfNeeded().catch(() => {});
          await prod.hover(); await wait(300);
          const pb = await prod.boundingBox();
          const g = await prod.locator('.resize[pos="top"][corner="right"]').boundingBox();
          if (!g || !pb) { warn(`no resize handle for ${it.name}`); break; }
          if (!shown) {
            await wait(400);
            await page.screenshot({ path: path.join(run.shots, 'resize-hover.png') });
            s.controls['resize-hover'] = await L.dump(page);
            extra.resize = { product: it.name, box: [pb.x, pb.y, pb.width, pb.height].map(Math.round), grip: [g.x, g.y, g.width, g.height].map(Math.round) };
          }
          const x = g.x + g.width / 2, y = g.y + g.height / 2;
          const dy = (now - target) * pxPerPct;        // top handle: dragging down makes the pack shorter
          await page.mouse.move(x, y); await page.mouse.down();
          await page.mouse.move(x, y + dy / 2, { steps: 5 }); await page.mouse.move(x, y + dy, { steps: 5 });
          await page.mouse.up(); await wait(1200);
          const after = await heightOf(it.name);
          if (Math.abs(after - now) > 1 && after > 10.5 && after < 99.5) pxPerPct = Math.abs(dy / (after - now));
          if (!shown) {
            const pb2 = await prod.boundingBox();
            await page.screenshot({ path: path.join(run.shots, 'resize-done.png') });
            s.controls['resize-done'] = await L.dump(page);
            extra.resize.after = pb2 ? [pb2.x, pb2.y, pb2.width, pb2.height].map(Math.round) : extra.resize.box;
            shown = true; console.log('captured resize-hover, resize-done');
          }
        }
      }
    }
    });
    await page.mouse.move(800, 3); await wait(1200);
    await closePanel();                               // clicking a pack opens its card
    await device('Tablet'); await snap('ide-tablet');
    await device('Mobile'); await snap('ide-mobile');
    await device('Desktop'); await snap('ide');
    await save(null, 'saved');

    // ================================================================ PHASE B
    // ---- the practice round
    const pr = plan.practice;
    if (pr.mode === 'copy') {
      await openPanel('Products');
      await round('Practice Round');
      await snap('prac-empty');
      await page.getByRole('button', { name: 'New product' }).first().click(); await wait(3500);
      await snap('prac-gallery');
      await page.getByText(/Round's products instead/).first().click(); await wait(2500);
      await snap('copy-modal');
      const copy = page.locator('#copyToRoundDialog');
      if (pr.startFiller) { await copy.getByRole('button', { name: 'All Filler', exact: true }).click(); await wait(800); await snap('copy-filler'); }
      const flip = pr.startFiller ? pr.targets : pr.fillers;
      const role = pr.startFiller ? 'Target' : 'Filler';
      let firstFlip = true;
      for (const name of flip) {
        const label = copy.getByText(name, { exact: true }).first();
        if (!(await label.count())) { warn(`${name} is not in the copy list`); continue; }
        await label.scrollIntoViewIfNeeded();
        const btn = label.locator(`xpath=ancestor::*[.//button[normalize-space()="${role}"]][1]`).getByRole('button', { name: role, exact: true });
        await btn.click(); await wait(500);
        if (firstFlip) { const b = await btn.boundingBox(); extra.copyFlip = { name, role, box: b && [b.x, b.y, b.width, b.height].map(Math.round) }; firstFlip = false; }
      }
      await snap('copy-target');
      await copy.getByRole('button', { name: /^Replace the / }).click(); await wait(3000);
      await snap('copy-progress');
      const done = page.getByRole('button', { name: 'Done', exact: true });
      if (await done.isVisible().catch(() => false)) { await done.click(); await wait(2000); }
      if (pr.remove.length) {
        await page.evaluate(() => document.querySelectorAll('[data-product-id]').forEach((c) => {
          const n = c.querySelector('input[type=text]'); if (n) c.setAttribute('data-guide-card', n.value);
        }));
        for (const name of pr.remove) {
          const cb = page.locator(`[data-guide-card="${esc(name)}"] input[type=checkbox]`).first();
          if (await cb.count()) { await cb.scrollIntoViewIfNeeded(); await cb.check(); }
        }
        await page.locator('#SidebarFooter').getByRole('button', { name: 'Delete', exact: true }).click(); await wait(1000);
        await page.getByRole('button', { name: 'Delete', exact: true }).last().click(); await wait(1500);
      }
      await snap('prac-full');
      await round('Main Round');
      await closePanel();
    } else if (pr.mode === 'batch') {
      await openPanel('Products');
      await round('Practice Round');
      await addBatches(pr.batches, false);
      await round('Main Round');
      await closePanel();
    }

    // ---- the search task, warnings and timing
    await openPanel('Settings');
    for (const [label, key] of [['Main Round', 'main'], ['Practice Round', 'practice']]) {
      const want = plan.settings[key];
      if (!want || want.categorySearch == null) continue;
      const main = key === 'main';
      await round(label);
      if (main) await snap('search-before');
      await page.getByText('Search type', { exact: true }).locator('xpath=following::button[1]').click(); await wait(900);
      if (main) await snap('search-open');
      const typeLabel = SEARCH_TYPES[+want.categorySearch] || 'Product';
      const opt = page.getByRole('option', { name: typeLabel, exact: true });
      if (await opt.count()) await opt.click(); else await page.getByRole('listbox').getByRole('button', { name: typeLabel, exact: true }).click();
      await wait(700);
      if (want.productSearch != null) {
        const cur = (await state()).settings[key].productSearch;
        const delta = +want.productSearch - +cur;
        const btn = page.getByText('Search count', { exact: true }).locator(`xpath=following::button[normalize-space()="${delta > 0 ? '+' : '−'}"][1]`);
        for (let i = 0; i < Math.abs(delta); i++) { await btn.click(); await wait(250); }
      }
      if (want.allowMixedCategories != null) await setToggle('Mixed categories per shelf', !!+want.allowMixedCategories);
      if (main) await snap('search-set');
      const errBtn = page.getByRole('button', { name: /^Error handling & warnings/ });
      await errBtn.click(); await wait(1200);
      if (main) await snap('errors-open');
      if (main && want.enableExclusion != null) await setToggle('Exclusion', !!+want.enableExclusion);
      if (main && want.retrialExclusion != null && +want.enableExclusion) await setNumber(numberAfter('Exclusion threshold'), want.retrialExclusion);
      if (want.randomPickErrors != null) await setNumber(numberAfter('Random selection error threshold'), want.randomPickErrors);
      if (want.productSearchTimeout != null) {
        const idle = page.getByText('Idle timeout', { exact: true }).locator('xpath=following::input[1]');
        if (await idle.count()) { await idle.fill(String(want.productSearchTimeout)); await idle.press('Tab'); }
      }
      if (main) await snap('errors-set');
      await errBtn.click(); await wait(600);
      const timing = page.getByRole('button', { name: /^Timing controls/ });
      await timing.click(); await wait(1000);
      if (want.ITI != null) {
        const iti = page.getByText('Inter-trial interval', { exact: true }).locator('xpath=following::input[1]');
        if (await iti.count()) { await iti.fill(String(want.ITI)); await iti.press('Tab'); }
      }
      if (main) await snap('timing-open');
      await timing.click(); await wait(600);
      if (main) {
        const ends = page.getByRole('button', { name: /^End links/ });
        if (await ends.count()) { await ends.click(); await wait(1000); await snap('endlinks-open'); await ends.click(); await wait(600); }
      }
    }
    await round('Main Round');
    await closePanel();

    // ---- screen text (before the test flow, while every screen can still be opened)
    if (plan.screens.length || plan.globals.length) await optional('screen text', async () => {
      await openPanel('Instructions');
      for (const sc of plan.screens) {
        const row = page.locator(`[data-instruction-target="${sc.key}"]`).first();
        if (!(await row.count())) { warn(`no "${sc.label}" screen in Instructions`); continue; }
        await row.click(); await wait(2000);
        const eds = page.locator('.ProseMirror');
        if (sc.text != null) await setRich(eds.nth(0), sc.text);
        if (sc.button != null) await setRich(eds.nth(1), sc.button);
        if (sc.button_delay != null) {
          const del = page.getByText('Button Delay', { exact: true }).locator('xpath=following::input[1]');
          if (await del.count()) { await del.fill(String(sc.button_delay)); await del.press('Tab'); }
        }
        await page.getByRole('button', { name: 'Back to instructions' }).click(); await wait(1200);
      }
      if (plan.globals.length) {
        await page.locator('[data-instruction-target="others"]').first().click(); await wait(1800);
        for (const g of plan.globals) {
          const inp = page.getByText(g.label, { exact: false }).locator('xpath=following::input[1]').first();
          if (await inp.count()) { await inp.fill(g.value); await inp.press('Tab'); } else warn(`no "${g.label}" field in Others`);
        }
        await page.getByRole('button', { name: 'Back to instructions' }).click(); await wait(1200);
      }
      await closePanel();
    });

    // ---- the test flow (welcome / practice / main)
    await openPanel('Test Flow'); await wait(1200);
    await snap('flow');
    const sw = { welcome: 'Welcome message', practice: 'Practice round', main: 'Main round' };
    let flipped = null;
    for (const [k, label] of Object.entries(sw)) {
      if (plan.flow[k] === plan.targetFlow[k]) continue;
      await page.getByRole('switch', { name: label, exact: true }).click(); await wait(1500);
      if (!flipped) { flipped = { key: k, label, on: plan.flow[k] }; await snap('flow-off'); }
    }
    if (!flipped) {          // nothing to change: show the switch anyway, and put it back
      await page.getByRole('switch', { name: 'Welcome message', exact: true }).click(); await wait(1500);
      flipped = { key: 'welcome', label: 'Welcome message', on: !plan.targetFlow.welcome, demo: true };
      await snap('flow-off');
      await page.getByRole('switch', { name: 'Welcome message', exact: true }).click(); await wait(1200);
    }
    extra.flowFlip = flipped;
    await closePanel();

    // ---- the questionnaire
    await openPanel('Questionnaire');
    await snap('q-list');
    const qsw = page.getByRole('switch', { name: 'Show questionnaire' });
    const qs = plan.questions;
    if (qs.length && (await qsw.getAttribute('aria-checked')) !== 'true') { await qsw.click(); await wait(1200); }
    await snap('q-on');
    for (let i = 0; i < qs.length; i++) {
      const q = qs[i];
      if (i === 0) await page.locator('[data-question-target]').first().click();
      else {
        await page.getByRole('button', { name: 'Back to questionnaire' }).click(); await wait(1200);
        if (i === 1) await snap('q-list-1');
        await page.getByRole('button', { name: /^\+?\s*Add question$/ }).last().click(); await wait(1500);
        if (i === 1) await snap('q-added');
        await page.locator('[data-question-target]').last().click();
      }
      await wait(2000);
      if (i === 0) await snap('q-open');
      const panel = page.locator('.ide-instruction').first();
      await panel.locator('input[type=text]').first().fill(q.title);
      const eds = panel.locator('.ProseMirror');
      await setRich(eds.nth(0), q.text);
      await setRich(eds.nth(1), q.button);
      await setRich(eds.nth(2), q.short_text);
      if (q.button_delay != null) {
        const del = panel.getByText('Button Delay', { exact: true }).locator('xpath=following::input[1]');
        if (await del.count()) { await del.fill(String(q.button_delay)); await del.press('Tab'); }
      }
      await wait(1200);
      if (i === 0) await snap('q-filled');
    }
    if (qs.length) { await page.getByRole('button', { name: 'Back to questionnaire' }).click(); await wait(1500); }
    if (!plan.flow.questionnaire && (await qsw.getAttribute('aria-checked')) === 'true') { await qsw.click(); await wait(1000); }
    await snap('q-list-all');
    await closePanel();

    // ---- custom code (Advanced: root accounts only)
    await optional('custom code', async () => { for (const [tab, code] of [['CSS', plan.advanced.css], ['JavaScript', plan.advanced.js]]) {
      if (!code) continue;
      if (!(await rail.getByText('Advanced', { exact: true }).count())) { warn('custom code not copied: the Advanced panel is for root accounts only'); break; }
      await openPanel('Advanced');
      await page.getByRole('tab', { name: tab }).click(); await wait(800);
      const ed = page.locator('.cm-content, .cm-editor, textarea').first();
      await ed.click(); await page.keyboard.press('Control+A'); await page.keyboard.insertText(code); await wait(600);
      await closePanel();
    } });

    extra.state = await state();
    await save('save-before', 'save-done');
    if (!run.dry) await snap('save-after');
  } finally {
    await s.finish();
  }
})().catch((e) => { console.error(e.message.slice(0, 800)); process.exit(1); });
