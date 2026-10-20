# Writing and reviewing a guide

The house User Guide template sets the look; these rules keep every platform's guide
consistent with it and with each other.

## Order

- Getting started (adding the component to a survey, the editor overview, the Quick Tour),
  then **building the test in the order a person does it**, then the look, then checking and
  publishing (devices, simulate, save, live/draft), then the **additional functions last**
  (Advanced, Restore a Previous Version / history rollback, AI assistant, What's New).
- Each "Understanding the …" overview sits just before the "How do I …?" steps that use it.

## Titles

- Only the template's two forms: **Understanding the …** and **How do I …?** (plus "Understanding
  Typography"-style names for a section without "the"). Title Case. No full stop.
- Keep titles short enough to clear the **Table of Contents** button on the title bar
  (about 50 characters); shorten rather than wrap ("How do I Set Each Product's Details?").

## Descriptions

- Overviews: `**Label** – what it does.` The label is the UI's own word, in bold.
- Steps: one action per step, imperative, the UI's words in bold: "Click **Add**." Say what the
  user sees next when it is not obvious.
- Examples quote the reference test's real values: "e.g. **Beers**", "e.g. **2.30**".
- UK spelling (colour, customise, centre). Plain words; no jargon the screen does not use.
- Link related sections with `[[Learn more|slide-key]]` (in the text colour, as the template does).
- Keep each slide's list within the slide: `build.py` warns when descriptions run past the
  bottom — split the overview (`split=[…]`) or shorten the text.

## Screenshots and callouts

- Full-editor screenshots are shown 8" wide; panels and pop-ups are cropped and enlarged.
- Badges sit outside the screenshot, in a column, pointing in with an arrow; never let two
  badges overlap or an arrow cross another badge — stagger them (`at`, `along`).
- In a step, the control being used is spotlit (the rest dimmed) and outlined. Outline the
  whole control, not part of it; for a region (a column, several tiles) outline each piece.
- Never show a credential, a token or a real respondent's data.

## Review checklist (every slide, every build)

Render with `run.sh build`, make contact sheets with `run.sh sheets`, and look at each one:

1. Text inside its box; nothing cut off or overflowing the slide; title clear of the button.
2. Each arrow lands on the control its description names; each box frames it fully.
3. No overlapping badges, no arrow crossing a badge or another arrow.
4. The spotlit area shows what the step is about (a dropdown open, the value typed).
5. The screenshot shows the state the text describes (e.g. the value already typed).
6. Numbering runs 1…n with no gaps; the contents entries all link; no leftover placeholder text.
7. The deck opens: `run.sh build` ends with the validator's verdict — fix anything it reports.

Fix, rebuild, and look again at the slides you changed.
