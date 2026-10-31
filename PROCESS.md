# Task Monster — Development Process

[Return to the project overview and screenshots](README.md)

## Starting idea

I wanted to make a small interactive experience for students who find a large assignment difficult to start. The intended action is simple: break the assignment into small steps, do one in real life, and mark it complete. The program should make that progress visible and make the next step clear.

The first prototype was a checklist connected to a monster's health. It supported one task, adding/removing steps, completion, undo and victory. I kept the scope centered on this loop rather than adding a shop, accounts or unrelated game systems. The final app supports several quests, but each one uses the same interaction.

## Connecting an action to a response

The important state is a list of steps, each with a `done` flag. In [app.py](task-monster/app.py), a **Complete & strike!** button calls `attack(task_id, index)`. That function changes the selected step through `toggle_step`, saves progress and requests the corresponding visual/sound effect. The interface rerenders from the new state.

In [game.py](task-monster/game.py), health is calculated rather than independently reduced:

```python
maximum = len(task["steps"]) * 100
remaining = maximum - completed_count(task) * 100
```

For example, a four-step quest starts with 400 HP. One completed step leaves 300 HP and contributes 10 gems. Undo clears that step's flag, restoring the health and reversing its reward. The balance is derived from current completion flags, so repeatedly undoing/completing cannot farm gems.

The response is meaningful because it changes the saved checklist, health, reward balance, step order and eventual collection state. Feedback includes the health bar, completed-step text, gem animation, changed monster expression and optional sound. The final step stores the completion time, opens a victory dialog and adds the monster to Collection. Dismissing the dialog returns to the board; View quest then opens a read-only recap.

## Classmate trial and response

Two classmates tried the app. These notes summarize the trial and feedback I reported during development; no participant names or recordings are included.

| Trial context | What I observed |
| --- | --- |
| The first classmate studies in the same programme. They knew the assignment requirements, but did not know this app's theme. I did not explain the app before they used it. | They could operate it smoothly without an interface walkthrough. This is the trial conducted without an app explanation. Their familiarity with the assignment is relevant context. |
| The second classmate was unfamiliar with the app. I briefly introduced what it was for before they used it. | They also operated it smoothly. Because I had introduced the purpose, this trial is not presented as entirely unprompted. |

Neither trial revealed a specific point where the classmate became stuck. These are qualitative observations; no timing measurements or step-by-step transcripts were recorded.

Their feedback suggested adding a way to set a task deadline and improving the monster imagery. I responded with two changes:

1. **Optional deadlines.** I added a date and time beneath Quest Name and a visible deadline on each active quest card. Overdue tasks receive a clear label. The field remains optional because not every personal task has a fixed due date. This adds time context without blocking the core checklist loop or adding a notification service.
2. **Monster artwork and feedback.** I replaced the earlier simple character bodies with the supplied polished illustrations and group portrait. I then added hurt and weak expressions for all six species, linked to the same remaining-health calculation. This makes the game's progress more visible while preserving a consistent character identity.

Because both classmates could use the interaction smoothly, I retained the main quest → step → battle → collection flow. The feedback led to focused additions and visual refinements rather than a redesign of the whole experience. The trial supports these design decisions; it does not establish long-term productivity benefits.

## Main design and code iterations

| Change | Reason and resulting behavior |
| --- | --- |
| Single task → multiple quests with local JSON storage | Users can return to unfinished work. The task model and storage logic were separated from the interface. |
| At least two steps before summoning | The creation screen encourages breaking down a large task. A compact Add step action and a separate gold Summon action clarify their different purposes. |
| Pending steps first; completed steps below | The next real-world action stays visible. Sorting preserves original step indices so moving a row does not change which step Undo affects. |
| Completion dialog and read-only collection recap | A final action has an obvious outcome and a clear way back. Completed quests become records rather than editable battles. |
| Optional deadlines and refined character imagery | These respond to classmate feedback, as described above. Deadlines are stored in UTC and displayed in Hong Kong time. |
| English calendar and keyboard time fields | Browser-localized date controls initially displayed Chinese. Fixed English month/day names and direct hour/minute entry keep interface language consistent while preserving user-entered text. |
| Responsive controls, aligned buttons and compact navigation | Screenshot reviews exposed low button lettering, excessive spacing and an oversized modal. The nested text alignment and both modal layers were corrected; narrow-screen layouts were checked. |
| One Sound switch, off by default | A single control is sufficient for this small app. Muting does not remove visual feedback. |

The gem flight is presentation only; Python owns the actual balance. Sound events are deduplicated so a Streamlit rerender does not replay a reward. Reduced-motion preferences skip unnecessary motion. The running app uses no AI endpoint, paid service, microphone or external media host.

## Mistakes and interruption

The creation flow rejects empty input and invalid hour/minute values. Removing draft steps can lock summoning again when fewer than two remain. Undo corrects an accidental completion while a quest is active; abandoning a quest requires a separate confirmation.

A missing save starts an empty adventure. Invalid JSON, unsupported data or malformed stored deadlines produce a warning and preserve the original file. Atomic file replacement reduces the risk of an interrupted write leaving incomplete JSON. Personal saves remain outside Git. The app is still a single-user prototype: concurrent users and cloud recovery are outside its scope.

## AI tools and decisions

**Codex** assisted with idea development, planning, Python/Streamlit code, CSS, original SVG icons, local checks, browser verification and documentation. I reviewed the interface through repeated screenshots and requested changes to layout, controls, navigation, dates and artwork. This document includes my later report of the classmate trial; the agent did not observe those classmates itself.

**Kept:** the suggestion to derive monster health and rewards from completed-step flags. It makes the interaction explainable and keeps Undo consistent. I also kept the core checklist/battle relationship because it directly communicates progress.

**Changed:** separate Music and SFX controls were initially implemented, then replaced with one Sound switch. The extra distinction added unnecessary interface weight. Initial runtime tilt/dimming was also replaced with actual hurt/weak artwork, because changes to expression communicate health more clearly.

**Rejected or deferred:** shops, paid currency, accounts and other game systems were left out because they distract from the task loop. Persistence was postponed in the first prototype until the core interaction worked, then added for returning users. Automatic sound playback was not used; playback requires a click. A custom GitHub check was briefly tried, then removed after I clarified that I did not want it; the real commit history remains.

**Images:** I supplied the finished group portrait and six original monster images. Their generation tool was not recorded, so it is not attributed to a guessed model. OpenAI built-in image generation was used later to make two expression variants per species, preserving the supplied designs. The transparent results were inspected, split into individual frames and converted to WebP. [SOURCES.json](task-monster/assets/monsters/SOURCES.json) and [EXPRESSION-PROMPTS.json](task-monster/assets/monsters/EXPRESSION-PROMPTS.json) record the available provenance and prompts.

**Sound:** Codex composed an original eight-bar melody and short navigation, attack, gem, undo and victory cues, implemented with Web Audio oscillators. This is AI-assisted composition and code synthesis, not an audio file generated by a dedicated music model. No sampled music or recordings of other people were used.

## Verification and evidence

The current local Python/AppTest suite has 20 passing checks. It covers input validation, multiple quests, health and Undo, reward consistency, final-step collection, read-only recap, navigation, save/reload, malformed files, legacy data, English calendar behavior, leap days and keyboard deadline validation. Two optional Node checks cover the audio engine. These implementation checks are separate from the classmate trial.

Browser verification exercised creation, completion, Undo, the victory dialog and collection. Earlier layout checks included 320px and 390px phone widths and a 1280px desktop viewport. The README now uses nine uniform 390×844 screenshots from an isolated fictional save; these are product demonstrations, not screenshots of classmates' private tasks.

The [README run commands](README.md#run-locally) use the committed dependency metadata and lockfile. The working interaction is available locally without a remote model or media service. Public access was checked with an unauthenticated request: the repository returned its project page and Public badge. Local links to source, screenshots and credits were also checked.

## Credits and development history

The project builds on SD5913 classroom concepts: Python lists and dictionaries, functions, state and Streamlit interaction. It extends those foundations with the quest model, persistence, health/reward calculations, collection, deadlines and custom presentation rather than submitting an unchanged course example.

Monster originals were supplied by the project author; source filenames and hashes are retained. Reference game screenshots informed the design direction, but their assets were not copied. Navigation and feedback icons are original code-drawn SVGs. Lilita One by Juan Montoreano is bundled with its [SIL Open Font License](task-monster/assets/fonts/OFL.txt).

The [commit history](https://github.com/Whitter-oy/Task-monster-A3/commits/main/) records actual revisions. For example, [0308ad4](https://github.com/Whitter-oy/Task-monster-A3/commit/0308ad4a082fa6bdfeddb41ee6e96867125ab561) added English deadline controls and expressive health states, and [6c13c4b](https://github.com/Whitter-oy/Task-monster-A3/commit/6c13c4b03e835acae5987a8288a70a4f35a4dfe4) tightened the keyboard time fields. Earlier process notes remain available through Git history; this root document reorganizes them for assessment rather than inventing a new development timeline.

Before submitting the repository URL on Canvas, I still need to make the final submission myself. Personal information, API keys, local saves and recordings of classmates must stay outside the public repository.
