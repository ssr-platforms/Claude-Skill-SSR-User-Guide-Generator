# IMPRINT profile

Complete and data-driven: give it the Test to clone and the Test to populate and it builds
the whole guide (about 150 slides). Built and proven on `gnrzvKEd` → `k5FG6YFo` (October 2026).

## Facts

| | |
|---|---|
| Dev URL | `http://imprint.test` (repository `~/ssr/imprint`, container `imprint`) |
| Editor | `/tests/code/{code}` (8-character codes). `/tests/design/{code}` is only the preview iframe |
| Tests | `imprint.tests`: `config` (live), `draft_config`, `survey_id` (Fluent survey uuid) |
| Sign-in | middleware `auth_fluent` (`app/Http/Middleware/FluentAuth.php`): a one-time `?uid=` `App\Models\RedirectToken` on connection `mysql_auth` (Fluent's database) |
| Store | Pinia `storeData`, key `data`: `products`, `prac_products`, `category`, `prac_category`, `variant`, `prac_variant`, `settings`, `instructions`, `questions`, `style`, `advance` |
| Gallery | `GET /tests/fluent-gallery/{code}` (this survey + project-wide), `GET /tests/fluent-gallery/{code}/public?search=` |
| Saving | **Save** / **Live Now** publishes; no autosave (only the Save button and Restore write) |
| History | More save options (⋮) → Recent changes → a version → Restore → Confirm Restore |
| Tour hooks | `data-ide-tour="…"`, `[data-ide-help-tour-trigger]`, `data-instruction-target`, `data-question-target`, `data-flow-step`, `#fluentGalleryDialog`, `#batchAddDialog`, `#copyToRoundDialog`, `#SidebarController`, `#SidebarFooter` |

## Sign-in (ask the user before minting a token)

The browser profile in the work folder keeps the session. When a run says *Not signed in*,
the user can paste an unopened "open in IMPRINT" link (its `uid`), or approve minting one in the
**local dev** database for their Fluent user id and the Fluent component of the Test to
populate:

```bash
# the component id: SELECT c.id FROM fluent.components c JOIN fluent.surveys s ON s.id=c.survey_id
#                   WHERE s.uuid=(SELECT survey_id FROM imprint.tests WHERE code='<populate>') AND c.type='imprint';
docker exec -w /app imprint php artisan tinker --execute='$t=\Illuminate\Support\Str::random(24); \App\Models\RedirectToken::create(["token"=>$t,"user_id"=><USER>,"component_id"=><COMPONENT>,"used"=>false]); echo "TOKEN=".$t.PHP_EOL;' \
  | grep -o 'TOKEN=[A-Za-z0-9]*' | cut -d= -f2 | tr -d '\n' > "$WIN_WORK/.token"
```

The next script spends it. Never print or commit it.

## What the plan clones

Main-round products a category at a time (gallery pick → category → names, prices, layers,
items per layer, target/filler), variants (on the cards), each pack's height on the shelf
(per device), shelves and products per shelf (per device, both rounds), the backdrop, shelf
frame, posts, price tags (currency, colours, blur), palette, corners, font, pop-up text size,
the practice round (copied from the main round with its targets, or added like the main
round), search type and count, exclusion, error threshold, idle timeout, inter-trial
interval, screen text and shared strings that differ, the test flow (welcome / practice /
main), the questionnaire and its questions, custom CSS/JS (root accounts).

Not cloned (reported as warnings): end links (they belong to the reference's survey), per-device
layers / items-per-layer overrides, per-device top depth, Modal Width of screens.

## Gotchas

- The Quick Tour opens by itself the first time a test is opened; the scripts press **Skip tour**.
- Rail items are `div`s: click them by text. Gallery tabs' accessible names are their tooltips
  ("Only this study can use it", "Every survey in this project", "Any team on the platform").
- In Select Category / Select Variant, clicking an entry chooses it **and closes the pop-up**.
- Sliders have a number box beside them: fill it and press Enter.
- Colour pickers take an 8-digit hex (colour + opacity) in `.vc-color-input input`.
- Pack heights: hover `.prod[data-fit-id=<product id>]` in `iframe.iframe-container`, drag a
  `.resize[pos=top]` handle. The preview is scaled, so the script learns pixels-per-percent
  from each drag and re-reads the store after each drop. Clicking a pack opens its card.
- "Add question" adds a question to the list without opening it.
- "Use the Main Round's products instead" sits outside `#fluentGalleryDialog`.
- Applying a theme saves the test — the look-only capture cancels the Apply dialog.
- The "How do I Add an IMPRINT Component to a Survey?" slides are the template's own (Fluent
  screens); recapturing them needs a Fluent login.
