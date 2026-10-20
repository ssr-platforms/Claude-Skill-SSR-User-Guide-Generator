# {{PLATFORM}} User Guide — progress

Built with the **userguide-maker** plugin (skill `user-guide-maker`). Started {{DATE}}.

| | |
|---|---|
| Test to clone | **{{CLONE}}** — read only, never edited |
| Test to populate | **{{POPULATE}}** — built through the editor; the guide's screenshots are taken from it |
| Deck | `docs/user-guide/<Platform> User Guide.pptx` |
| Inputs and settings | `build/guide.env` |
| The build plan | `build/plan.json` (from `run.sh read`) |
| Every word and callout | `build/content.py` |

## Status

- [ ] `run.sh preflight` passed
- [ ] `run.sh read` — plan reviewed (missing images? warnings?)
- [ ] `run.sh capture --dry` — screenshots reviewed
- [ ] user said yes to saving into the Test to populate
- [ ] `run.sh capture` (saves) and `run.sh look`
- [ ] `run.sh build` — every slide reviewed (`run.sh sheets`)

## Decisions and notes

(record here what the user decided, what was skipped and why, and anything a later session needs)

## How to rebuild

```bash
R=<plugin>/skills/user-guide-maker/engine/run.sh
bash $R read            # re-read both tests and re-plan (read-only)
bash $R capture --dry   # re-take the build screenshots without saving
bash $R look            # look-only screenshots
bash $R build           # the deck, measured, rendered and validated
```
