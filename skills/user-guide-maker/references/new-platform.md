# Writing a profile for a new platform

A profile teaches the engine one platform's editor. Everything else — the template, the
slides, badges, spotlights, contents, rendering, validation — is shared. Start from the
closest existing profile (`platforms/imprint/` is the complete, data-driven one) and copy it
to `platforms/<name>/`, then replace the platform-specific parts below. Work on the copy in
the repository's `docs/user-guide/build/` while you develop; copy it back into the plugin's
`platforms/<name>/` when it works, so the next person gets it.

## 1. Learn the editor (read-only)

Use an Explore agent on the platform's repository for the facts, with file paths:

- the **dev URL** (APP_URL; the traefik host in `~/ssr/docker-compose.yml`) and the **editor
  route** for one test (e.g. `/tests/code/{code}`, `/survey/{code}`); what a test code looks like;
- **sign-in**: the middleware on the editor routes. Most platforms take Fluent's one-time
  `?uid=` RedirectToken (`auth_fluent`); find the model, its connection and required columns
  so the profile can say how to mint one (and the user must approve each one);
- the **store** that holds the open test's data (Pinia: `$pinia._s.get(<id>)`; Vuex differs)
  and its top-level keys;
- the **panels** (left rail), their exact labels, and any tour hooks (`data-ide-tour`,
  `id="tour-*"`) — these make stable selectors;
- **saving**: the button, whether it publishes, and that there is **no autosave** (grep for
  `setInterval`/`debounce` around save calls). The dry run depends on this — if a platform
  autosaves, dry runs are not safe: stop and tell the user;
- **history**: is there a Recent changes / restore drawer;
- **images**: where stimuli come from (Fluent gallery endpoint, uploads);
- whether the repository's `package.json` is `"type": "module"` (the work folder gets its own
  `package.json` with `"type": "commonjs"`, so the scripts stay CommonJS anyway).

Then open the editor and look. A small look-only script that signs in, screenshots and dumps
every visible control (`L.session` + `snap`) answers most questions quickly; view the
screenshots and query the dumps with `engine/q.py`.

## 2. `profile.env`

```
APP_URL=http://<platform>.test
GUIDE_TITLE="<PLATFORM> User Guide"
READ_SCRIPT=read-test.js          # leave out the two lines below if there is no data-driven plan
PLAN_SCRIPT=plan.js
CAPTURES="capture-build.js"      # run in order by `run.sh capture`
LOOK_CAPTURES="capture.js"       # run by `run.sh look`
```

## 3. `read-test.js` (read-only)

Signs in, opens the test, copies the store's data (and anything else the plan needs, such as
the gallery the Test to populate can pick from) into a JSON file. Copy IMPRINT's and change
the editor URL, the store id and the gallery endpoint. It must not click, type or save.

## 4. `plan.js` (pure)

Turns the Test to clone's data into the steps the capture takes, and the examples the guide
quotes. Keep the rules IMPRINT's follows:

- match stimuli to the Test to populate's gallery by **picture** (URL / file name), falling
  back to the name with a warning;
- change only what **differs** from the blank Test to populate (style, settings, text);
- never copy survey-specific links (end links, redirects);
- print a summary the user can check: what will be built, what is **missing**, warnings,
  whether the target is blank.

A profile can start without a plan (the IMPACT example keeps its data at the top of
`capture-build.js`), but a plan is what makes "give me the two codes" work.

## 5. `capture-build.js` (builds the Test to populate)

The from-scratch walkthrough, in the order a person builds a test. Rules:

- refuse a target that is the Test to clone or is not blank (read the store first);
- `snap('<state>')` at every step the guide shows, before and after the action, with
  states named for what they show (`add-gallery`, `cat-typed`, `set-tablet`, …);
- prefer selectors by role and visible label (`getByRole('button', { name })`), tour hooks
  and ids; tag rows you need later (`data-guide-row`) so the dump can find them;
- record anything the text needs in `extra` (a product the walkthrough used, a box measured
  mid-action);
- honour `run.dry`: never press Save in a dry run; save twice in a real run (once mid-way, once
  at the end) so the history drawer has more than one version;
- warn (`s.warn`) and carry on when something optional fails; throw only when going on would
  build the wrong thing.

## 6. `capture.js` (look-only)

Each state in its own `step()`, starting from a fresh load; every dialog opened is cancelled.
Panels, the editor overview, devices, simulate/preview, menus, the history drawer (opened, a
version opened, Restore pressed and **Cancel**ed), the assistant's welcome screen.

## 7. `content.py`

Copy IMPRINT's and keep its helpers (`ov`, `steps`, `section`, `Controls`, `co`, `pad`,
`union`, `eg`). Set `META`, `INTRO` (what the product is and its components), `TOC_INTRO`,
`ACCENT` (the platform's brand colour, hex without `#`; the template's own violet is
`901A8A`) and `TOC`. Then write the sections:

- **Understanding the …** (`ov`): one screenshot, every part numbered, descriptions
  `**Label** – what it does.`; split long lists over slides with `split=[…]`; crop to a panel
  with `crop=[x, y, w, h]` and `place=dict(x=…, y=…, h=…)` (inches on the slide);
- **How do I …?** (`steps`): one step per slide, the list growing, the step's control spotlit
  and outlined; a step can light several boxes (pass a list of boxes).

Look boxes up in the dumps by label (`C(state, s='Save', t='button')`, `tour=`, `role=`,
`row=`, `within=`) rather than typing coordinates; type a box only for things with no single
element (a column, a region), and measure it on the screenshot. Quote the reference's own
values in the examples (`eg(...)` from `plan.json`).

## 8. Try it, then hand it back

`run.sh init` with `--force` after each change to the plugin copy (or edit the copy in
`build/` directly), `read`, `capture --dry`, `look`, `build`, and review every slide. When the
profile works, copy it back to the plugin's `platforms/<name>/`, with its `profile.md` recording
the facts and gotchas you found.
