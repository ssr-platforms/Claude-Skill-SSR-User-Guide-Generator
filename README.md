# userguide-maker

A Claude Code plugin that builds a step-by-step **PowerPoint user guide** for a Split Second
Research platform, in the house *Layout User Guide Template* style.

You give it two tests:

- **Test to clone** — a finished test to copy. It is only ever read.
- **Test to populate** — a new, empty test of the same platform, in which the guide is built.

Claude rebuilds the Test to clone inside the Test to populate through the platform's real
editor, screenshots every step, and turns the screenshots into annotated slides: numbered
callouts, spotlit controls and a linked table of contents. Test creation comes first; extra
functions (Advanced, history rollback, the AI assistant) come last.

## Install

Check the [Requirements](#requirements) first. Then install from GitHub, inside a Claude Code
session:

```
/plugin marketplace add ssr-platforms/Claude-Skill-SSR-User-Guide-Generator
/plugin install userguide-maker@ssr-userguide-maker
```

Or from a terminal:

```bash
claude plugin marketplace add ssr-platforms/Claude-Skill-SSR-User-Guide-Generator
claude plugin install userguide-maker@ssr-userguide-maker
```

Restart Claude Code, or run `/reload-plugins`. Then check that
`/userguide-maker:make-user-guide` shows up when you type `/`.

**Update** to the latest version:

```
/plugin marketplace update ssr-userguide-maker
```

**Uninstall:** `/plugin uninstall userguide-maker@ssr-userguide-maker`

### Install from a local folder (for developing the plugin)

Point the marketplace at a clone of this repository instead:

```bash
# WSL / Linux / macOS
claude plugin marketplace add "/mnt/e/S4 Platforms/claude/userguide-maker"
# Windows
claude plugin marketplace add "E:\S4 Platforms\claude\userguide-maker"

claude plugin install userguide-maker@ssr-userguide-maker
```

Claude Code reads the plugin straight from that folder. Run `/reload-plugins` and your edits
reach every session.

## Use

Open Claude Code in the platform's repository (e.g. `~/ssr/imprint`) and either run

```
/userguide-maker:make-user-guide <test-to-clone> <test-to-populate>
```

or just ask: *"Make a user guide: clone ABcd1234 into EFgh5678."* Claude detects the platform
from the repository, reads both tests, shows the plan, does a **dry run** (nothing saved), and
asks before saving anything into the Test to populate. The deck lands in
`docs/user-guide/<PLATFORM> User Guide.pptx`, with slide previews and a `PROGRESS.md` beside it.

## Platforms

| Platform | Profile |
|---|---|
| IMPRINT | complete and data-driven — the two test codes are all it needs |
| IMPACT | worked example (built for one reference); adapt its data constants |
| EXPRESS, IMPRESS, ACT, FAST, IMPULSE, … | Claude writes the profile on first use, following `skills/user-guide-maker/references/new-platform.md`, and it can be copied back into `platforms/` for everyone |

The deck builder, renderer, browser and review tools are shared by every platform; only the
editor-specific steps live in `skills/user-guide-maker/platforms/<name>/`.

## Requirements

- Windows with WSL (the set-up the SSR dev stack uses): Windows **Node.js**, **Google Chrome**
  (or Edge) and **PowerPoint**; in WSL, `python3` with `lxml` and `Pillow`.
  Elsewhere set `NODE_EXE`, `CHROME_EXE` and `WIN_WORK`; without PowerPoint previews come from
  LibreOffice.
- The platform running locally (e.g. `http://imprint.test`) and a way to sign in to its editor
  (a one-time Fluent sign-in link; Claude asks before creating one).

## Safety

The Test to clone is never written to. Nothing is saved into the Test to populate before a dry
run has been reviewed and you have said yes — saving publishes it. The Test to populate must be
blank. Sign-in tokens are treated as credentials. Look-only screenshots open dialogs and cancel
them. End links are never copied.

## Layout

```
.claude-plugin/plugin.json, marketplace.json
commands/make-user-guide.md                     the slash command
src/Layout User Guide Template.pptx             the house template
skills/user-guide-maker/SKILL.md                what Claude follows
skills/user-guide-maker/engine/                 run.sh, build.py, capture-lib.js, browser.js,
                                                render-measure.ps1, q.py, sheet.py
skills/user-guide-maker/platforms/<name>/       one profile per platform
skills/user-guide-maker/references/             new-platform.md, writing-and-qa.md, progress-template.md
```
