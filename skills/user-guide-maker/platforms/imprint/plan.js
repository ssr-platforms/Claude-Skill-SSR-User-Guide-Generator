// Works out, from the Test to clone and the Test to populate (both read by read-test.js),
// everything capture-build.js does, and the examples content.py quotes. Pure: no browser.
//
//   node plan.js <clone.json> <target.json> <plan.json>
//
// Products are added a category at a time (one gallery pick per category), each matched to
// the Test to populate's gallery by its picture, not its name. Style, settings and screen text
// are only changed where the two tests differ. End links are never copied: they belong to the
// Test to clone's survey.
const fs = require('fs');

const [cloneFile, targetFile, outFile] = process.argv.slice(2);
if (!outFile) { console.error('usage: node plan.js <clone.json> <target.json> <plan.json>'); process.exit(2); }
const CL = JSON.parse(fs.readFileSync(cloneFile, 'utf8'));
const TG = JSON.parse(fs.readFileSync(targetFile, 'utf8'));
const d = CL.data, t = TG.data;
const warnings = [];

// ------------------------------------------------------------------ helpers
const pathOf = (u) => { try { return decodeURIComponent(new URL(u, 'http://x').pathname); } catch { return String(u || ''); } };
const fileOf = (u) => pathOf(u).split('/').pop();
const canon = (v) => (v && typeof v === 'object' && !Array.isArray(v)
  ? Object.keys(v).sort().reduce((o, k) => ((o[k] = canon(v[k])), o), {}) : Array.isArray(v) ? v.map(canon) : v);
const same = (a, b) => JSON.stringify(canon(a ?? null)) === JSON.stringify(canon(b ?? null));
const num = (v) => (v === '' || v == null || isNaN(+v) ? null : +v);
const html = (h) => String(h ?? '').replace(/\s+/g, ' ').trim().replace(/^<p>([^<]*)<\/p>$/, '$1');

const tabOf = (scope) => (scope === 'survey' ? 'This survey' : scope === 'public' ? 'Public' : 'Project-wide');
const gallery = (TG.gallery.items || []).map((i) => ({ ...i, tab: tabOf(i.scope) }))
  .concat((TG.gallery.public || []).map((i) => ({ ...i, tab: 'Public' })));
const lc = (x) => String(x || '').trim().toLowerCase();
function image(src, name) {
  const p = pathOf(src), f = fileOf(src);
  let hit = gallery.find((i) => pathOf(i.url) === p) || gallery.find((i) => fileOf(i.url) === f);
  if (!hit) {                                  // the picture was replaced in the gallery: fall back to its name
    hit = gallery.find((i) => lc(i.name) === lc(name)) || gallery.find((i) => lc(name).startsWith(lc(i.name) + ' '));
    if (hit) warnings.push(`"${name}" matched the gallery image "${hit.name}" by name — its picture may differ from the Test to clone's`);
  }
  return hit ? { gallery: hit.name, tab: hit.tab, thumb: hit.thumbnail_url || hit.url, url: hit.url } : null;
}
const nameOf = (list, id) => {
  if (id == null || String(id) === '1') return null;            // 1 is N/A
  const x = (list || []).find((c) => String(c.id) === String(id));
  return x ? x.name : null;
};
const ordered = (list) => {
  const l = [...(list || [])];
  return l.every((p) => p.index != null) ? l.sort((a, b) => a.index - b.index) : l;
};

// ------------------------------------------------------------------ products
const missing = [];
function item(p, cats, vars) {
  const img = image(p.src, p.name);
  if (!img) missing.push(p.name);
  const st = p.style || {};
  const heights = {};
  for (const [dev, k] of [['pc', 'height'], ['tablet', 'tabHeight'], ['mobile', 'mobileHeight']]) {
    const v = parseFloat(st[k]);
    if (v > 0) heights[dev] = v;
  }
  const overrides = {};
  for (const k of ['tabLayers', 'mobileLayers', 'tabCount', 'mobileCount']) {
    const base = k.endsWith('Layers') ? +p.layers || 1 : +p.count || 1;
    if (num(p[k]) != null && +p[k] !== base) overrides[k] = +p[k];
  }
  return {
    name: p.name, code: p.code, src: p.src, ...(img || { gallery: null, tab: null, thumb: null }),
    price: p.tag == null ? '' : String(p.tag), layers: +p.layers || 1, count: +p.count || 1,
    type: +p.type === 0 ? 0 : 1, category: nameOf(cats, p.category), variant: nameOf(vars, p.variant),
    heights, overrides,
  };
}
function batchesOf(items) {
  const out = [];
  for (const it of items) {
    if (!it.gallery) continue;                                    // cannot be picked: reported as missing
    let b = out.find((x) => x.category === it.category);
    if (!b) out.push(b = { category: it.category, items: [] });
    b.items.push(it);
  }
  return out;
}
const main = ordered(d.products).map((p) => item(p, d.category, d.variant));
const mainBatches = batchesOf(main);

// variants are set on the product cards after adding, in the order they are first used
const variants = [];
for (const it of main) {
  if (!it.variant) continue;
  let v = variants.find((x) => x.name === it.variant);
  if (!v) variants.push(v = { name: it.variant, products: [] });
  v.products.push(it.name);
}

// ------------------------------------------------------------------ practice round
const prac = ordered(d.prac_products);
let practice;
if (!prac.length) practice = { mode: 'none' };
else {
  const codes = new Set(main.map((i) => i.code));
  if (prac.every((p) => codes.has(p.code))) {
    const inPrac = new Set(prac.map((p) => p.code));
    const targets = prac.filter((p) => +p.type !== 0).map((p) => main.find((i) => i.code === p.code).name);
    const fillers = prac.filter((p) => +p.type === 0).map((p) => main.find((i) => i.code === p.code).name);
    practice = { mode: 'copy', targets, fillers, startFiller: fillers.length > targets.length,
      remove: main.filter((i) => !inPrac.has(i.code)).map((i) => i.name), count: prac.length };
  } else {
    practice = { mode: 'batch', batches: batchesOf(prac.map((p) => item(p, d.prac_category, d.prac_variant))) };
  }
}

// ------------------------------------------------------------------ settings and test flow
const ROUND = ['shelves', 'tabShelves', 'mobileShelves', 'productsPerShelves', 'tabProductsPerShelves', 'mobileProductsPerShelves',
  'categorySearch', 'productSearch', 'allowMixedCategories', 'randomPickErrors', 'productSearchTimeout', 'ITI'];
const MAIN_ONLY = ['enableExclusion', 'retrialExclusion'];
const pick = (o, keys) => Object.fromEntries(keys.filter((k) => o && o[k] != null).map((k) => [k, num(o[k]) ?? o[k]]));
const S = d.settings || {}, TS = t.settings || {};
const settings = {
  main: pick(S.main, [...ROUND, ...MAIN_ONLY]), practice: pick(S.practice, ROUND),
  targetMain: pick(TS.main, [...ROUND, ...MAIN_ONLY]), targetPractice: pick(TS.practice, ROUND),
};
const flowOf = (s, q) => ({ welcome: !!+s.enableWelcome, practice: !!+s.enablePractice, main: !!+s.enableMain, questionnaire: !!+((q || {}).enable) });
const flow = flowOf(S, d.questions), targetFlow = flowOf(TS, t.questions);

// ------------------------------------------------------------------ questionnaire
const qlang = Object.keys(d.questions || {}).find((k) => k !== 'enable') || 'en';
const questions = (d.questions?.[qlang] || []).map((q) => ({
  title: q.title || '', text: q.text || '', button: q.button || '', short_text: q.short_text || '',
  button_delay: num(q.button_delay),
}));

// ------------------------------------------------------------------ screen text (only what differs)
const ilang = Object.keys(d.instructions || {})[0] || 'en';
const SCREEN = { welcome: 'Welcome Message', practice: 'Practice Round', main: 'Main Round', main_no_prac: 'Main Round (No Practice)',
  warning: 'Too Slow', warning2: 'Selection Error', screenout: 'Screenout Message', end: 'Complete Message' };
const GLOBAL = { LoadingStep1: 'Loading (Step1)', LoadingStep2: 'Loading (Step2)', LoadingStep3: 'Loading (Step3)', LoadingStep4: 'Loading (Step4)',
  Practice_Trial: 'Practice Round', Main_Trial: 'Main Round', Search_for: 'Search For',
  Product_Chooser_Btn_Instruction: 'Questionnaire Pagination Instruction', ForcePortrait: 'Force Portrait Mode', Saving: 'Saving Data', Saving_failed: 'Saving Failed' };
const ci = d.instructions?.[ilang] || {}, ti = t.instructions?.[ilang] || {};
const screens = [];
for (const [k, label] of Object.entries(SCREEN)) {
  const a = ci.main?.[k], b = ti.main?.[k];
  if (!a) continue;
  const ch = { key: k, label };
  if (a.text != null && html(a.text) !== html(b?.text)) ch.text = a.text;
  if (a.button != null && html(a.button) !== html(b?.button)) ch.button = a.button;
  if (a.button_delay != null && num(a.button_delay) !== num(b?.button_delay)) ch.button_delay = num(a.button_delay);
  if (Object.keys(ch).length > 2) screens.push(ch);
  if (a.style && b?.style && !same(a.style, b.style)) warnings.push(`screen "${label}": its Modal Width differs from the Test to clone and is not copied`);
}
const globals = Object.entries(GLOBAL).filter(([k]) => ci.global?.[k] != null && String(ci.global[k]) !== String(ti.global?.[k] ?? ''))
  .map(([k, label]) => ({ key: k, label, value: String(ci.global[k]) }));

// ------------------------------------------------------------------ style (only what differs)
const cs = d.style || {}, ts = t.style || {};
const differs = (a, b) => !same(a, b) && !(a == null && b == null);
const colours = (pairs) => pairs.filter(([, , a, b]) => a != null && differs(a, b)).map(([label, nth, value]) => ({ label, nth, value }));
const RADIUS = { '0vmin': 'None', '0.25vmin': 'Extra small', '0.5vmin': 'Small', '1vmin': 'Medium', '2vmin': 'Large', '3vmin': 'Extra large', '99vmin': 'Pill', '4vmin': 'Extra large' };
const PALETTE = { base100: 'Cards', base100Content: 'Text on cards', primary: 'Buttons', primaryContent: 'Button text', secondary: 'Button hover',
  secondaryContent: 'Button hover text', neutral: 'Muted', neutralContent: 'Text on muted', errorColor: 'Error', warningColor: 'Warning', success: 'Success', info: 'Info' };
const sh = cs.shelves || {}, tsh = ts.shelves || {};
const bgType = sh.bgType || (sh.bgImg ? 'image' : 'color');
const style = {
  backdrop: (differs(bgType, tsh.bgType || (tsh.bgImg ? 'image' : 'color')) || (bgType === 'color' ? differs(sh.bg, tsh.bg) : differs(sh.bgImg, tsh.bgImg))
    || (bgType === 'image' && differs(String(sh.brightness), String(tsh.brightness))))
    ? { type: bgType, color: sh.bg, image: sh.bgImg || null, brightness: num(sh.brightness) } : null,
  frame: {
    colours: colours([['Front Color', 0, cs.shelf?.bg, ts.shelf?.bg], ['Top Color', 0, cs.shelf?.shadow, ts.shelf?.shadow],
      ['Shadow Color', 0, cs.shelf?.shadow2, ts.shelf?.shadow2], ['Text Color', 0, cs.shelf?.text, ts.shelf?.text]]),
    toggles: [['Show shelf frame', !+cs.shelf?.hidden, !+ts.shelf?.hidden], ['Show product shadows', !+cs.shelf?.hideProductShadow, !+ts.shelf?.hideProductShadow],
      ['Perspective from eye level', !!+cs.shelf?.perspective, !!+ts.shelf?.perspective]]
      .filter(([, a, b]) => a !== b).map(([label, on]) => ({ label, on })),
    numbers: [['Top depth', cs.shelf?.topDepth, ts.shelf?.topDepth], ['Eye level', cs.shelf?.eyeLevel, ts.shelf?.eyeLevel]]
      .filter(([, a, b]) => num(a) != null && num(a) !== num(b)).map(([label, value]) => ({ label, value: num(value) })),
    deviceDepth: { tablet: num(cs.shelf?.tabTopDepth), mobile: num(cs.shelf?.mobileTopDepth) },
  },
  post: {
    colours: colours([['Background Color', 0, cs.post?.bg, ts.post?.bg], ['Shadow Color', 1, cs.post?.shadow, ts.post?.shadow]]),
    show: !+cs.post?.hidden !== !+ts.post?.hidden ? !+cs.post?.hidden : null,
  },
  pricetag: {
    currency: cs.pricetag?.cs_name && differs(cs.pricetag.cs_name, ts.pricetag?.cs_name) ? cs.pricetag.cs_name : null,
    custom: cs.pricetag?.cs_name === 'CUSTOM' ? { left: cs.pricetag.cs_left || '', right: cs.pricetag.cs_right || '' } : null,
    colours: colours([['Background Color', 1, cs.pricetag?.bg, ts.pricetag?.bg], ['Text Color', 1, cs.pricetag?.text, ts.pricetag?.text]]),
    blur: !!+cs.pricetag?.blurContent !== !!+ts.pricetag?.blurContent ? !!+cs.pricetag?.blurContent : null,
  },
  palette: Object.entries(PALETTE).filter(([k]) => cs.theme?.[k] != null && differs(cs.theme[k], ts.theme?.[k]))
    .map(([k, label]) => ({ label, nth: 0, value: cs.theme[k] })),
  radius: [['Cards & tiles', cs.theme?.radiusBox, ts.theme?.radiusBox], ['Buttons', cs.theme?.radiusSelector, ts.theme?.radiusSelector]]
    .filter(([, a, b]) => a != null && differs(a, b)).map(([group, v]) => ({ group, label: RADIUS[v] || 'Medium' })),
  font: cs.typography?.fontFamily && differs(cs.typography.fontFamily, ts.typography?.fontFamily)
    ? String(cs.typography.fontFamily).split(',')[0].replace(/['"]/g, '').trim() : null,
  modal: Object.fromEntries([['fontSize', 'Font Size'], ['lineHeight', 'Line Height'], ['shadow', 'Shadow']]
    .filter(([k]) => cs.modals?.[k] != null && differs(String(cs.modals[k]), String(ts.modals?.[k])))
    .map(([k]) => [k, parseFloat(cs.modals[k])])),
};
const advanced = { css: (d.advance?.customCSS || '').trim(), js: (d.advance?.customJS || '').trim() };

// ------------------------------------------------------------------ examples for the guide's text
const first = mainBatches.find((b) => b.category) || mainBatches[0] || { category: null, items: [] };
const vFirst = variants[0] || null;
const examples = {
  category: first.category,
  batch: first.items.map((i) => i.name),
  batchGallery: first.items.map((i) => i.gallery),
  tab: (first.items[0] || {}).tab || 'Project-wide',
  otherCategories: mainBatches.filter((b) => b !== first && b.category).map((b) => b.category),
  renamed: first.items.find((i) => i.gallery !== i.name) || null,
  item: first.items[0] || null,
  layered: first.items.filter((i) => i.layers > 1).map((i) => i.name),
  layers: Math.max(1, ...first.items.map((i) => i.layers)),
  count: (first.items.find((i) => i.count > 1) || first.items[0] || { count: 1 }).count,
  hasFiller: first.items.some((i) => i.type === 0),
  variant: vFirst,
  resize: main.find((i) => i.heights.pc && i.gallery) ? main.find((i) => i.heights.pc && i.gallery).name : null,
  practiceTarget: practice.mode === 'copy' ? practice.targets[0] || null : null,
  question: questions[0] || null,
  total: main.filter((i) => i.gallery).length,
};

const plan = {
  clone: { code: CL.code, title: CL.title }, target: { code: TG.code, title: TG.title },
  targetIsBlank: !(t.products || []).length && !(t.prac_products || []).length,
  main: mainBatches, missing, variants, practice, settings, flow, targetFlow, questions, qlang,
  screens, globals, ilang, style, advanced, examples, warnings,
};
fs.writeFileSync(outFile, JSON.stringify(plan, null, 1));

// ------------------------------------------------------------------ summary
const n = mainBatches.reduce((a, b) => a + b.items.length, 0);
console.log(`plan: clone ${CL.code} (${CL.title}) -> populate ${TG.code} (${TG.title})`);
console.log(`  Test to populate is ${plan.targetIsBlank ? 'blank' : 'NOT blank — capture-build.js will refuse it'}`);
console.log(`  main round: ${n} products in ${mainBatches.length} gallery picks: ` + mainBatches.map((b) => `${b.category || 'N/A'} (${b.items.length})`).join(', '));
if (missing.length) console.log(`  MISSING from the Test to populate's gallery (will be skipped): ${missing.join(', ')}`);
console.log(`  variants: ${variants.map((v) => `${v.name} (${v.products.length})`).join(', ') || 'none'}`);
console.log(`  practice round: ${practice.mode}` + (practice.mode === 'copy' ? `, targets ${practice.targets.join(', ') || 'none'}` + (practice.remove.length ? `, then remove ${practice.remove.length}` : '') : ''));
const m = settings.main;
console.log(`  shelves (desktop/tablet/mobile): ${m.shelves}/${m.tabShelves}/${m.mobileShelves} × ${m.productsPerShelves}/${m.tabProductsPerShelves}/${m.mobileProductsPerShelves} per shelf`);
console.log(`  test flow: ` + Object.entries(flow).map(([k, v]) => `${k} ${v ? 'on' : 'off'}`).join(', '));
console.log(`  questions: ${questions.length}` + (questions.length ? ` (${questions.map((q) => q.title).join(', ')})` : ''));
const sc = [style.backdrop && 'backdrop', style.frame.colours.length && 'frame colours', style.frame.numbers.length && 'top depth / eye level',
  style.post.colours.length && 'posts', style.pricetag.currency && 'currency', style.pricetag.colours.length && 'price tag',
  style.palette.length && 'palette', style.radius.length && 'corners', style.font && 'font', Object.keys(style.modal).length && 'pop-up text'].filter(Boolean);
console.log(`  style changes: ${sc.join(', ') || 'none'}`);
console.log(`  screen text changes: ${screens.length} screens, ${globals.length} shared strings`);
for (const w of warnings) console.log('  WARNING ' + w);
