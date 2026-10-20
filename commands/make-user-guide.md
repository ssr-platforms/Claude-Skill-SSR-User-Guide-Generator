---
description: Build a step-by-step PowerPoint user guide by cloning one test into another in the platform's editor
argument-hint: <test-to-clone> <test-to-populate> [platform]
---

Use the **user-guide-maker** skill to build the user guide for this repository's platform.

- Test to clone: `$1`
- Test to populate: `$2`
- Platform: `$3` (if blank, detect it from the repository; ask if it cannot be told)

If the Test to clone or the Test to populate is missing, ask for it before doing anything else.
Follow the skill's workflow in order and keep to its safety rules: the Test to clone is only ever read,
and nothing is saved into the Test to populate until a dry run has been reviewed and the user has said yes.
