---
name: user-guide-maker
description: Builds a step-by-step PowerPoint user guide for a Split Second Research platform (IMPRINT, IMPACT, EXPRESS, IMPRESS, ACT, FAST, IMPULSE, …) in the house "Layout User Guide Template" style, by cloning a reference test (the "Test to clone") into a blank test (the "Test to populate") through the platform's real editor and screenshotting every step, then annotating the screenshots with numbered callouts. Use when the user asks for a user guide, a how-to deck, a training deck or annotated screenshots of a platform's editor, or gives a "test to clone" and a "test to populate".
---

# User guide maker

Turns a real test into a user guide. The user gives two test codes:

- **Test to clone** — the reference. It is **only ever read**.
- **Test to populate** — a new, empty test of the same platform, ideally in the same Fluent project (so it sees the same gallery images). The guide builds it from scratch in the editor, and every step becomes a slide.

The deck follows the house template (`../../src/Layout User Guide Template.pptx` from this file): cover, contents, introduction, then "Understanding the …" overview slides placed just before the "How do I …?" walkthroughs that use them, ordered as a test is built, with the extra functions (Advanced, Restore a Previous Version, AI assistant, What's New) last.

## What is here

| Path (from this file) | What it is |
|---|---|
| `engine/run.sh` | every step: `init`, `preflight`, `read`, `capture [--dry]`, `look`, `build`, `sheets` |
| `engine/build.py` | template surgery: slides, badges, arrows, spotlights, contents, links (any platform) |
| `engine/capture-lib.js`, `engine/browser.js` | headless Chrome session, sign-in, screenshot + control dump, store reader |
| `engine/render-measure.ps1` | PowerPoint renders the slides and measures text, so lists are evenly spaced |
| `engine/q.py`, `engine/sheet.py` | find a control's box in the dumps; contact sheets for review |
| `platforms/<name>/` | a platform profile: `profile.env`, `profile.md` (facts and gotchas), `read-test.js`, `plan.js`, `capture-build.js`, `capture.js`, `content.py` |
| `references/new-platform.md` | how to write a profile for a platform that has none yet — **read it before starting one** |
| `references/writing-and-qa.md` | the wording, layout and review rules every guide follows |

Profiles today: **imprint** (complete and data-driven: the two codes are all it needs) and **impact** (a worked example built for one reference; adapt its data constants). Every other platform: write a profile with `references/new-platform.md`, starting from the closest existing one.

## Safety rules — never break these

1. **Never write to the Test to clone.** Scripts refuse it as the target; never edit a script to get round that.
2. **Dry run first.** `run.sh capture --dry` builds the clone in the browser and closes the page without saving (the editors have no autosave — confirm that for a new platform before relying on it). Show the user the result and **ask before** the real `run.sh capture`, which saves — and on most platforms saving **publishes** the test.
3. **The Test to populate must be blank.** The capture refuses one that is not. Never empty a test to make it pass: ask the user for a new one.
4. **Sign-in tokens are credentials.** The editors sign in with a one-time Fluent token. Ask the user before minting one (the command is in the profile), store it only in the work folder's `.token`, and never print, log or commit it. The browser profile in the work folder keeps the session afterwards.
5. **Look-only captures only look.** They open dialogs and cancel them: never press Save, confirm a delete or restore, apply or save a theme, or send the AI assistant a message.
6. **Ask before anything that writes to a database** (resetting a test, minting a token, deleting history), and verify which database the command reaches first.
7. **End links are never copied** — they belong to the reference's survey.

## Workflow

Run everything from the platform's repository root; the guide lives in `docs/user-guide/` (set `GUIDE_DIR` to change it). `R=<this skill's folder>/engine/run.sh`.

1. **Inputs — only two.** Ask the user for the **Test to clone** and the **Test to populate** (the test to create the clone in) if they have not given them. Work out the platform yourself from the repository you are in (its folder name, `package.json` or git remote); ask only if that is genuinely unclear. Check `platforms/` for its profile. No profile → `references/new-platform.md` first.
2. **Set up.** `bash $R init <platform> <test-to-clone> <test-to-populate>` — copies the profile into `docs/user-guide/build/` (edit the copies there; `init` never overwrites them unless given `--force`) and writes `build/guide.env` and `PROGRESS.md`.
3. **Preflight.** `bash $R preflight` — template, Node, Python (lxml, Pillow), PowerPoint, the app answering, the work folder. If a later step says *Not signed in*, follow the profile's sign-in section (ask before minting).
4. **Read and plan (read-only).** `bash $R read` — opens both tests in the editor, copies their data out of the editor's store, and works out the plan (`build/plan.json`). Read the summary to the user: products and how they will be picked, anything **missing** from the Test to populate's gallery, warnings, whether the target is blank.
5. **Dry run.** `bash $R capture --dry` → screenshots in `docs/user-guide/screenshots/`. Review them as contact sheets (`bash $R sheets docs/user-guide/screenshots`, then view the printed images). Fix any step that went wrong in `build/capture-build.js` and run again.
6. **Ask, then save.** Show the user the dry-run result and ask before `bash $R capture`: it saves the Test to populate (twice, so Restore a Previous Version has history) and that publishes it.
7. **Look-only screenshots.** `bash $R look` — panels, menus, dialogs, devices, Simulate, preview, assistant.
8. **Build.** `bash $R build` — builds, measures every description in PowerPoint, rebuilds, renders `docs/user-guide/previews/`, validates. Slides whose screenshot is missing are dropped with a warning, and their contents entries with them.
9. **Review every slide.** `bash $R sheets` and look at every sheet: text overflow, a callout on the wrong control, a box off its target, overlapping badges, a dimmed area hiding what the step is about. Fix boxes in `build/content.py` (find them with `python3 engine/q.py docs/user-guide/screenshots <state> <text>`), rebuild, look again. Follow `references/writing-and-qa.md`.
10. **Record.** Update `docs/user-guide/PROGRESS.md` — status, decisions, what was skipped and why — so a later session can continue. Tell the user where the deck is, what the Test to populate now contains, and what was not cloned.

## Platform setup notes

- The scripts drive **Windows Chrome under Windows Node** from WSL (WSL's own Chromium usually lacks libraries), working in `%TEMP%\userguide-maker`; `playwright-core` is copied from the npx cache or installed there. Elsewhere set `NODE_EXE`, `CHROME_EXE` and `WIN_WORK`.
- Rendering and text measurement use **PowerPoint over COM** (`powershell.exe`). Without it previews come from LibreOffice and text heights are estimated (check spacing by eye).
- WSL interop sometimes fails to start a Windows program (`UtilAcceptVsock`); `run.sh` retries those.
- The capture viewport is 1600×900 CSS px at 2× (3200×1800 screenshots). Every box in `content.py` is in those CSS px.

## When something does not work

| Symptom | Do this |
|---|---|
| *Not signed in* | the session expired: the profile's sign-in section (ask before minting a token) |
| `read` finds no store data | the store id changed: check the editor's source, update the profile's `read-test.js` |
| products **missing** from the gallery | the Test to populate's survey cannot see those images: pick a target in the same Fluent project, or ask the user to add the images |
| a control is not found during capture | the UI changed: find the new label with a dump (`q.py`) and fix the selector in `build/capture-build.js` |
| a slide's callout points at the wrong thing | fix its box in `build/content.py`; boxes are looked up by label wherever possible |
| `build` warns *dropped slide* | that screenshot was not captured: see the capture log for the step that failed |
