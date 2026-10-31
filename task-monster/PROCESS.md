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

## 30 October 2026: interaction hierarchy and reward feedback

The author requested a smaller dock, selected-tab-only labels and playful transitions. The dock was reduced from 106px to 74px, with a short icon bounce and enough page-end clearance. Labels remain accessible to assistive technology when visually hidden.

The author also found button lettering hard to read. The previous multiple text shadows and heavy synthetic weight were removed. Typography now uses Arial with shared sizes of 11, 13, 15, 20 and 26 pixels, rather than many local sizes. Green means add/complete, gold means summon or a major continuation, muted purple means undo/back, and red means remove/abandon.

The large collection count panel was removed. Defeated monsters now appear in three columns as framed cards, with level stars and a star-shaped button to reopen each quest. Text descriptions remain available through the button label and tooltip.

Creation no longer previews a monster. The app requires at least two steps before showing Summon monster, and the model also rejects new single-step quests. Old single-step saves remain readable. Add step is a small aligned action; each draft has a red trash action on the right. Completed battle steps use a purple gem badge and a compact Undo action instead of a green check box and a full-width green button.

XP was replaced with a purple gem wallet derived from completed steps, at 10 gems per step. Undo reverses the reward and cannot accumulate extra gems. A small JavaScript presentation effect animates five original SVG gems from the completed step to the wallet, then pulses the wallet; Python remains responsible for all reward values and persistence. Reduced-motion preferences skip the flight.

Verification: twelve local regression checks passed, including the two-step gate, hidden preview, legacy saves, rewards, undo/re-completion, persistence and consumption of the reward event after one render. Browser checks confirmed only one visible tab label, a 74px dock, no button text shadows, an approximately 78px Add step button and right-aligned red removal actions. At 320px and 1280px viewports the page and dock edges matched and the final action could scroll above the dock. During the browser reward test, five flying gem elements were visible and the wallet moved from 130 to 140, with undo returning it to 130. Demonstration data was isolated from personal saves.

## Visual refinement after the second screenshot review

The author requested rounder cartoon lettering, clearer spacing and more game-like frames. The interface now uses a rounded system-font stack with the existing five-size scale, while keeping text shadows disabled for readability. Bevels, inset highlights, gold studs and plaque headings replace plain outlines. The homepage uses Ember Dragon and contains its summon action inside the hero card.

The creation form's built-in submit hint and character counter overlapped the input on small screens. These overlays are now hidden; the 120-character limit and empty-input validation still apply. Add step is centered in a compact fixed-width column. The surprise information box was removed without exposing the monster before creation. Collection actions were changed from star-only icons to explicit View quest labels following the author's revised preference.

Only the three primary screens show the dock. A battle has a small arrow Back button and remembers whether it was entered from Quests or Collection; a newly summoned quest returns to Quests. Local AppTest checks now cover this navigation, alongside the existing validation, persistence and reward checks (13 passing checks). Browser inspection used fictional tasks to verify the focused input, card labels, hero action, rounded type and navigation. This is implementation verification and author feedback, not the required trial with another person.

## Grouped panels, stronger cartoon type and original sound

Following the author's third screenshot review, the interface switched from device-dependent rounded fonts to bundled Lilita One by Juan Montoreano. Its original SIL Open Font License is included. The wallet became a compact dark capsule with an overlapping purple gem. Undo now uses a centered grey-purple bevel. The homepage tagline, separate completion plaque and View collection shortcut were removed. Active quests and battle steps now each sit inside one large framed container, with distinct inner cards.

**AI sound work:** Codex composed an original eight-bar melody in C major at 112 BPM and wrote oscillator-based Web Audio synthesis. Triangular melody notes, a soft bass and quiet chord tones form a repeating background track. Navigation and summon cues differ; successful attacks trigger a short low hit followed by a three-note gem chime, while undo descends. This is AI-authored composition rendered with code, not audio generated by a dedicated music model. No existing music, sampled recordings, external services or course example audio were copied. The author requested AI-generated music; this available procedural approach was explicitly described during development.

**Kept and changed:** the AI suggestion to separate music and effects switches was kept so players can choose either channel. Autoplay was rejected: both channels begin muted and require a deliberate click. Music state lives on the parent browser page so Streamlit rerenders do not restart the tune. Hiding the tab mutes background music and returning resumes scheduling. Audio failure leaves all task interactions available.

Verification included 13 passing Python/AppTest checks and two dependency-free Node audio checks for opt-in playback, scheduling, mute, rerender persistence and reward-event deduplication. Browser checks exercised both switches and an attack/reward update using fictional data. This verification does not replace the required independent user trial.

## Completion flow and collection recap revision

The author asked for one unified Sound switch, a smaller HUD, creation steps grouped in the same frame as active quests, consistent button-label alignment and species-colored collection cards. Those changes replace the previous separate Music/SFX controls and shared card color. Back now precedes the task title and summon notice.

Active quests keep pending steps first. Completing a step appends it below earlier completions; undo returns it to the pending group. Original step indices stay stable so moving a card cannot attack a different step. Per-step completion timestamps determine this order and are saved with the quest. Older saves remain readable.

Completing the last step stores the quest's UTC completion time and opens a styled celebration dialog. Its close button, Escape/outside dismissal and explicit Back to quests action use the same callback to return home. A new ascending victory fanfare is distinct from ordinary hit/gem cues. A pending dialog does not replay the fanfare on rerender. Collection now opens a read-only recap: no health bar, Undo, strike or abandon actions. The recap displays the saved completion time in Hong Kong time, or a clear unavailable message for legacy data without a timestamp.

Verification: 14 Python/AppTest checks and two Node audio checks passed. Browser interaction verified final-step dialog opening, closing its X to return home, master sound on/off across routes, read-only recap controls, and different species colors. Screenshots still use fictional demonstration tasks. No independent user trial is claimed.

## Compact controls and viewport correction

The latest author review identified that Add step still appeared low despite a centered outer button. Browser measurement showed its nested inline Markdown line box introduced the offset. The label now uses a block line box positioned at the button center, with a one-pixel optical adjustment. The unlocked Summon monster action is placed before the first draft step.

The celebration content had been constrained while the native modal shell retained a wider default size. Both layers now share a responsive width, capped at 400px, with viewport height limits and scrolling for unusually long content. Browser checks confirmed matching shell/content rectangles and visible close/action controls at 1280×720 and 320×568. Sound on/off measured the same 83×25px at a 390px viewport; only color and icon change. The sound control has a little more space below the wallet. Back retains its accessible name while showing only an original arrow icon.

The home banner now shows three original monsters and a slightly higher summon action. Navigation uses individual square game tiles with a raised selected state. Fourteen existing application checks passed; interaction behavior and saves remain compatible. Screenshot checks use fictional tasks, not an independent user trial.

## Restored palette and six-monster banner

At the author's request, square navigation tiles now use the original purple/gold palette. Their bottom edges align with the viewport edge; the dock itself has a transparent background and no shadow, so gaps reveal content and do not intercept interaction. At 390×844, all three button bottoms measured exactly 844px. The home banner combines all six original species with varied scale, rotation and overlapping layers. A 320px browser check found no horizontal overflow.

The unlocked summon action now precedes its steps/level/HP summary, followed by the draft step cards. Major interface headings use uppercase via presentation styles; saved task names are preserved. Updated home, creation and collection screenshots use fictional tasks.

## Supplied character artwork and optional quest deadlines

On 31 October 2026 the author supplied a transparent group portrait and six finished monster PNGs. These now replace the code-drawn monster bodies across the home banner, quest cards, battles, collection, recaps and victory dialog. Original navigation and feedback icons remain. The assets were resized for phone display and converted to transparent WebP; the supplied designs were not regenerated. Source filenames and SHA-256 hashes are recorded in assets/monsters/SOURCES.json. The author has not specified the generation tool used for those supplied images, so this process does not invent an AI-image provenance claim. Runtime tilt, dimming, sweat and sparkle overlays provide damage/victory feedback while using the supplied illustrations.

The new optional date/time controls appear immediately beneath Quest Name. The selected local deadline is interpreted in Asia/Hong_Kong, normalized to UTC in JSON, then shown in HKT on each active quest card. Overdue tasks are labelled without preventing their creation. Missing deadlines on older saves display No deadline set. Malformed stored deadlines are rejected without overwriting the original save.

Seventeen Python/AppTest checks passed, including deadline widget entry, UTC conversion, save/reload, active-card formatting, overdue status, invalid input and legacy compatibility. Browser checks exercised the calendar and time controls, verified all supplied species and inspected the HKT deadline/overdue cards. All demonstration data is fictional; no independent user trial is claimed.

## English deadline picker and health expressions

The author's next review found Chinese month/day strings inside the browser-localized date picker, low Undo lettering, a distant group portrait and a two-line deadline card. The native date/time widgets were replaced with an English calendar built from Python's calendar module, fixed English month/weekday names, and 24-hour hour/minute selects. Leap years and month lengths use calendar calculations. Clear date restores an optional deadline; successfully summoning clears the draft date. Deadlines still use Asia/Hong_Kong and save in UTC, but the active-card date omits HKT and sits on the label's row.

Undo now centers its nested Markdown line box with a one-pixel optical adjustment and an explicit 48×36px button, so absolute label positioning cannot collapse its width. The group portrait moves four pixels inward; smaller-phone copy scales to avoid overlap.

OpenAI built-in image generation produced a two-frame transparent expression sheet for each of the six supplied species. Each prompt locks the supplied identity, palette, outline and glossy style while changing the eyes, mouth and small pose details. Left frames depict hurt/determined characters; right frames depict exhausted, worried characters with drooping appendages. The sheets were inspected, split into separate frames and optimized to transparent WebP. Exact prompts are saved in assets/monsters/EXPRESSION-PROMPTS.json and provenance in SOURCES.json. The original cheerful artwork remains the full-health and collected state. Damage switches to hurt after any completed step, then weak at 35% HP or less. Undo uses the same recalculated health to restore the correct image. This replaces the prior tilt/dim-only damage treatment.

Nineteen Python/AppTest checks passed, including all species/state selections, undo restoration, English controls, leap-day selection, clearing the date, UTC persistence and legacy saves. Browser checks exercised healthy → hurt → weak → undo transitions, measured Undo at 48×36px with its text center one pixel above the button center, and verified English calendar selection at 390×844 and 320×568. The narrow calendar scrolls internally to reach its lower rows. Screenshots use isolated fictional data; no independent user trial is claimed.

## Compact keyboard time entry

The author requested removal of the completion timestamp's HKT suffix and the deadline helper line. The underlying Hong Kong timezone conversion remains consistent. Hours and minutes now use keyboard text fields with accessible names, faint internal labels and no dropdown or numeric spinner. The deadline title and its three controls sit closer together. Invalid, missing or out-of-range time digits prevent summoning a dated quest instead of silently saving another time; undated quests remain optional.

Twenty Python/AppTest checks passed, including valid keyboard entry, rejected 24-hour/60-minute values, blank/non-numeric input, UTC persistence and completion display without HKT. Browser inspection confirmed aligned 40px controls, direct keyboard input and the revised completion recap. Updated screenshots use fictional demonstration tasks only.

## User trial — still to complete

Ask another person to create a quest and complete a step before explaining how the app works. Record the real observation and decision without identifying them.

- Task given to the participant:
- What they attempted before any explanation:
- Where they hesitated or made a mistake:
- Improvement made, or reason to retain the design:

## Remaining submission work

Complete the real user trial and observation-based decision. Run the documented commands from a fresh terminal, try the relevant error case, and verify signed-out access to the public repository before submitting its URL to Canvas.
