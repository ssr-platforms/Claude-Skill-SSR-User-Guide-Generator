// Reads one IMPRINT test, read-only: opens it in the editor and copies the editor's own
// data out of its store, plus the gallery the test can pick images from. Nothing is
// clicked, typed or saved.
//
//   node read-test.js <run.json> clone|target <out.json>
const fs = require('fs');
const L = require('./capture-lib');

(async () => {
  const run = L.config();
  const which = process.argv[3];
  const out = process.argv[4];
  const code = which === 'clone' ? run.clone : run.target;
  const s = await L.session(run, `read-${which}-controls.json`);
  try {
    await L.signIn(s.page, `${run.app}/tests/code/${code}`, { okPath: '/tests/code/' });
    const data = await L.readStore(s.page, 'storeData', 'data');
    if (!data) throw new Error('could not read the editor store (storeData) — has the editor changed?');
    const title = await s.page.title();
    // The gallery this test can pick from. For the Test to populate, any picture of the Test to
    // clone that is not in it is also looked for in the public library, by name.
    let wanted = [];
    const cloneFile = require('path').join(run.work || '.', 'clone.json');
    if (which === 'target' && fs.existsSync(cloneFile)) {
      const c = JSON.parse(fs.readFileSync(cloneFile, 'utf8')).data;
      wanted = [...(c.products || []), ...(c.prac_products || [])].map((p) => ({ name: p.name, src: p.src }));
    }
    const gallery = await s.page.evaluate(async ([c, wanted]) => {
      const H = { Accept: 'application/json', 'X-Requested-With': 'XMLHttpRequest' };
      const get = async (u) => { try { const r = await fetch(u, { headers: H, credentials: 'same-origin' }); return r.ok ? await r.json() : { reason: 'http ' + r.status }; } catch (e) { return { reason: String(e) }; } };
      const own = await get(`/tests/fluent-gallery/${encodeURIComponent(c)}`);
      const items = own.items || [];
      const file = (u) => String(u || '').split('?')[0].split('/').pop();
      const have = new Set(items.map((i) => file(i.url)));
      const pub = [];
      for (const w of wanted) {
        if (have.has(file(w.src)) || pub.some((i) => file(i.url) === file(w.src))) continue;
        const r = await get(`/tests/fluent-gallery/${encodeURIComponent(c)}/public?page=1&search=${encodeURIComponent(w.name)}`);
        for (const i of (r.items || r.data || [])) if (file(i.url) === file(w.src)) pub.push(i);
      }
      return { items, reason: own.reason || null, public: pub };
    }, [code, wanted]);
    fs.writeFileSync(out, JSON.stringify({ code, title, data, gallery }));
    const n = (data.products || []).length, p = (data.prac_products || []).length;
    console.log(`read ${which} ${code} (${title}): ${n} main products, ${p} practice products, ${gallery.items.length} gallery images`
      + (gallery.public.length ? ` + ${gallery.public.length} from the public library` : '') + (gallery.reason ? ` (gallery: ${gallery.reason})` : ''));
  } finally { await s.finish(); }
})().catch((e) => { console.error(e.message.slice(0, 500)); process.exit(1); });
