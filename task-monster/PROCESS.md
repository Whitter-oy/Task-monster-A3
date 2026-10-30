# Development process

## Starting idea and first prototype

Task Monster is for students who know what they need to do but find a large task difficult to start. Breaking a task into small actions makes the next action clearer, while a monster's health provides visible progress.

The first version supported one task, adding/removing steps, completion and undo, health, victory and a confirmed reset. A list of dictionaries stored each step and a Boolean flag. Streamlit session state preserved values across reruns. Health was calculated from the flags rather than independently decreased, keeping undo consistent.

Initial local AppTest checks covered empty input, button identity after deletion, completion, undo, victory and reset. These were program checks, not a user trial.

## AI tools and decisions

Codex helped discuss ideas, connect them to classroom concepts, write/refactor Python, design CSS and original SVGs, test the interaction and draft documentation.

**Kept:** a checklist connected to monster health. The action/feedback relationship is explainable: mark a step complete, recalculate health, render the new state.

**Changed or rejected:** JSON persistence was postponed in the first prototype to validate the main loop, then added during the multi-task revision. Shops, paid currency and other systems shown in reference games were omitted because they distract from completing real tasks. XP is derived from currently completed steps, so repeatedly undoing and completing cannot accumulate extra rewards.

The project author still needs to review and understand the code and add their own observations and final decisions. No participants or trial observations have been invented.

## Development history

The repository started with the working prototype and documentation. Meaningful changes were saved as real commits with descriptions of the changes. The history was not backfilled to pretend earlier development happened.

## Automatic-check experiment and removal

The author asked about A2's green checks. Inspection of A2's workflow and the course checker on `sd5913/pfad`'s `2026` branch found support for A1 and A2. Codex added a separate custom workflow and local tests instead of changing the course assignment parameter to 3.

The first cloud run failed because `setup-uv@v9` could not be resolved. Correcting the action version to the official release found at the time produced a passing run. The author then clarified that A3 did not require automatic checking and preferred its removal. The workflow was removed; optional local tests and the genuine commit/run history remain. No automatic GitHub check is configured.

References:

- [A2 workflow](https://github.com/Whitter-oy/HK-rainfall-2025/blob/main/.github/workflows/check.yml)
- [Course checker](https://github.com/sd5913/pfad/blob/2026/assignments/check.py)
- [GitHub Python workflows](https://docs.github.com/en/actions/tutorials/build-and-test-code/python)
- [uv with GitHub Actions](https://docs.astral.sh/uv/guides/integration/github/)

## 30 October 2026: mobile game and multiple quests

The author found the first interface too simple and supplied card, dungeon and gallery references. The flow became multiple quests, one monster for each, higher levels for more steps, visible damage after completing steps, and a collection of defeated monsters.

The single-task list became four screens: quest board, summon, battle and collection. Python and Streamlit were retained. `game.py` separates task and JSON logic, while `art.py` draws six original SVG species. Type selects the species and task name affects decoration; reference characters and assets were not copied.

Level equals the number of steps, with 100 HP per step. Local progress saves outside Git using atomic JSON replacement. Seven local checks passed for multiple tasks, health/undo, collection, session recovery, abandonment, malformed saves and SVG states. A separate browser demonstration verified health going from 300/400 to 200/400, 100/400 and 0/400, followed by collection entry.

Screenshots use fictional demonstration tasks and states from a separate save file, not a real user trial. Neither demonstration saves nor personal task data is committed.

## 30 October 2026: English, layout and navigation corrections

The author requested English throughout the submitted project. Labels, names, validation messages, documentation, test examples and screenshots were translated. Legacy task types migrate to English; user-entered titles and steps are preserved.

The author supplied screenshots showing that the phone background ended while long content continued, the dock did not align with the page, and lower controls were hidden. The phone background was moved to the scrolling main container, page and dock now share a width with border-box sizing, and an explicit end spacer leaves room for the dock. Phone and desktop widths and the end of long pages are checked in the browser.

Verification: nine local regression checks passed, including migration of legacy saves and an already-open creation screen. Browser measurements at 320px and 390px phone widths and a 1280px desktop viewport found matching page/dock edges and no horizontal overflow. On desktop the phone and dock were both 460px wide at x=410. At the bottom of a three-step creation page, the final action ended above the dock; the battle footer was also reachable above it. Updated screenshots use English-only demonstration tasks.

Buttons were changed to bright green and gold with highlights and raised edges. Three navigation tabs now have original SVG sword, scroll and shield icons, and a raised orange active tab. Their artwork was drawn in code rather than extracted from the supplied references.

This feedback came from the project author during development. It does not replace the required trial with at least one other person.

## User trial — still to complete

Ask another person to create a quest and complete a step before explaining how the app works. Record the real observation and decision without identifying them.

- Task given to the participant:
- What they attempted before any explanation:
- Where they hesitated or made a mistake:
- Improvement made, or reason to retain the design:

## Remaining submission work

Complete the real user trial and observation-based decision. Run the documented commands from a fresh terminal, try the relevant error case, and verify signed-out access to the public repository before submitting its URL to Canvas.
