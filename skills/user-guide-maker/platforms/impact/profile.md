# IMPACT profile (worked example)

Built for one reference: the IMPACT User Guide cloned `ABUVANIDYQ` into `SO2GKM679H`
("Snack Shelf Test") in October 2026 (73 slides). The scripts work and are adapted to the
engine (`run.json`, dry runs), but the **reference's data is written into
`capture-build.js`** — there is no `read-test.js` / `plan.js` yet. For a new Test to clone,
either set those constants from it, or (better) write a `read-test.js` and `plan.js` the way
the IMPRINT profile does and make `capture-build.js` read the plan
(`references/new-platform.md`).

## Facts

| | |
|---|---|
| Dev URL | `http://impact.test` (repository `~/ssr/impact`, container `impact`) |
| Editor | `/survey/{code}` (10-character codes) |
| Tests | `App\Models\Test`: `images` (the stimuli and their grids, cells, groups), `global_settings`, `instructions`, `result_settings` |
| Sign-in | one-time `?uid=` `App\Models\RedirectToken` (`token` is short — 24 characters fits; `component_id` is required) |
| Saving | **SAVE** (it only looks upper-case); every save is a version in Recent changes |
| History | More actions (⋮) → Recent changes → a version → RESTORE THIS VERSION |
| Hooks | `id="tour-*"` (`#tour-stimuli`, `#tour-toolbar`, `#tour-stage-view`, `#tour-target-bar`, `#tour-sidebar`, `#tour-right-sidebar`, `#tour-save`, `#tour-devices`), `#how-it-works-btn`, `.stage-tab`, `.tool-group`, `.bar-group`, `div[data-instruction-target]` |
| Preview | opens `/app/{code}?id=test` in a new tab and runs the **saved** test |

## The reference data in `capture-build.js`

`STIMULUS` (the gallery image's name), `TOP_SHELF` / `BOTTOM_SHELF` (boxes of the packs, in
CSS px of the stage, where active cells are painted), `LOGO_STROKES` (priority cells),
`GROUPS` (cell group names, one per pack), the grid size (`30 × 20`), trials (`50`), the target
icon (`Crosscut`) and its strengths, and the welcome text. Read them from the Test to clone's
`images[0]` (grid, active/priority cells, groups) and `global_settings`.

## Sign-in (ask the user before minting a token)

```bash
docker exec -w /app impact php artisan tinker --execute='$t=\Illuminate\Support\Str::random(24); \App\Models\RedirectToken::create(["token"=>$t,"user_id"=><USER>,"component_id"=><COMPONENT>,"used"=>false]); echo "TOKEN=".$t.PHP_EOL;' \
  | grep -o 'TOKEN=[A-Za-z0-9]*' | cut -d= -f2 | tr -d '\n' > "$WIN_WORK/.token"
```

## `reset-test.sh`

Puts a demo test back to a saved blank snapshot **and deletes its Recent Changes**. It writes to
the local database: ask the user first, and never point it at the Test to clone.

## Gotchas

- Accessible names are the visible labels, not the tooltips: `Save`, `Cell Groups`,
  `Target Cells`, `New group`, `Create group`.
- After creating a cell group the panel stays in "Assigning <group>"; `+ New group` returns
  only after **Done**.
- Preview runs the saved test — save first; the welcome card slides in, so wait for START.
- The dump rows here use `c` (classes) rather than the engine's `cls`; `content.py` reads `c`.
