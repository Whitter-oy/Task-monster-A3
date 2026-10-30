# Task Monster · Quest Adventure

A game-inspired task tool for students who need help starting large tasks. A task becomes a monster, its steps become attacks, and a completed task becomes a collectible card.

## Run

Open a terminal in this directory:

```bash
uv sync --locked
uv run streamlit run app.py
```

Open the URL printed by Streamlit, normally http://localhost:8501. Press Ctrl+C to stop. To update a running app, stop it, run the commands again, and refresh the browser. Python 3.13 is selected in `.python-version`; `uv.lock` records dependencies.

## Play

- **Quests:** browse active monsters, level, health and progress, then select **Enter battle**.
- **Summon:** name a task, choose a type or **Auto-detect**, and add at least two steps. The small green Add step action is separate from the gold Summon monster action. Red trash buttons remove draft steps. The monster stays a surprise until summoning.
- **Level and health:** a quest has 2–24 steps. Each step adds one level and 100 HP.
- **Battle:** finish a step in real life, then choose **Complete & strike!**. Health and progress update with visual feedback. Each completed step awards 10 purple gems; a short animation sends gems to the wallet. A weakened monster changes expression. Use **Undo** if needed.
- **Collection:** completed quests appear as cards. The **View quest** button below each card opens its quest; undoing completion returns the quest to the board.
- **Abandon:** expand **Quest options**, confirm the checkbox, and remove only that quest.

## Screenshots

Fictional demonstration tasks, not records of user testing:

<img src="assets/screenshots/home.jpg" width="220" alt="Quest board" /> <img src="assets/screenshots/battle.jpg" width="220" alt="Monster battle" /> <img src="assets/screenshots/gallery.jpg" width="220" alt="Monster collection" />

[Creation page](assets/screenshots/create.jpg) · [Grouped steps and sound switches](assets/screenshots/steps.jpg).

## Sound

Use **Music off** or **SFX off** near the wallet to enable each channel. Both start muted. Music continues through page changes; mute either channel at any time. Reloading the browser resets both to off. Background music pauses while the tab is hidden. Visual feedback remains usable without sound or Web Audio support.

The original eight-bar, 112 BPM C-major melody and effects were composed by Codex and rendered procedurally with the browser's Web Audio oscillators. This is AI-assisted composition and code synthesis, not output from a music-generation model or an external music service. No account, recording, microphone or paid service is needed. Navigation, summoning, damage, gems and undo use distinct cues. See `assets/audio.js` in the app folder for the score and synthesis.

## Storage and errors

Tasks save automatically to `local_data/tasks.json`, which is ignored by Git. Reopening reads this file. Legacy category identifiers are converted to English without changing user-entered text.

Empty input and too many steps produce messages. An unreadable or unsupported save is preserved. Stop the app, back up the file, repair or move it, then restart and refresh. If writing fails, the current session can continue with a warning. Atomic replacement avoids incomplete JSON after interrupted saves.

## Limitations

This is a single-user local prototype with one shared save per server, not a public multi-user service. There are no accounts, cloud sync or concurrent-edit protection. Task names affect decorations and types select six species. Classification uses local rules, not AI, and can be overridden manually. Steps cannot be edited after summoning. Damage is equal per step, completion is self-reported, and the gem balance is completed steps × 10. Undoing a step or abandoning its quest reverses the corresponding rewards.

Active quests and battle steps are each grouped in a single framed panel. Completed monsters remain in Collection; battles show their final state without an extra completion panel.

The responsive web interface has a 460px phone frame, an aligned icon dock and space below long content. It is not a native app. Navigation bounce, monster motion and reward flights respect reduced-motion preferences. The three-column collection uses framed artwork, level stars and labelled View quest actions. The dock appears on the three primary screens; battles have a game-style Back button that returns to the screen they were opened from.

## Optional local checks

```bash
uv run --locked python -m unittest discover -s tests -v
```

Tests cover multiple tasks, damage, undo, collection, persistence, invalid saves and legacy migration. No GitHub automatic-check workflow is configured. With Node.js installed, audio scheduling checks can also be run using `node --test tests/audio.test.cjs`. Tests do not replace a real user trial.

## Credits and next steps

The project builds on SD5913 concepts: lists/dictionaries, functions, state, Streamlit and JSON. `art.py` contains original monster and navigation SVGs; Lilita One by Juan Montoreano is bundled under the SIL Open Font License (see assets/fonts/OFL.txt). Reference game screenshots informed style, but their assets were not copied. Codex assisted with design, code, verification and documentation; see PROCESS.md.

Before submission, complete a real trial with another person, record the observation and design decision, follow the run instructions from a fresh terminal, and verify signed-out access to the public repository.
