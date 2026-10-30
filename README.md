# Task Monster

**Turn to-dos into adventures.** A small, mobile-style quest tool for students who find large tasks difficult to start. Break a real task into steps, complete each step to attack a monster, and collect the monster when the whole quest is finished.

## Screenshots

<img src="task-monster/assets/screenshots/home.jpg" width="220" alt="Quest board" /> <img src="task-monster/assets/screenshots/battle.jpg" width="220" alt="Monster battle" /> <img src="task-monster/assets/screenshots/gallery.jpg" width="220" alt="Monster collection" />

These screenshots use fictional demonstration tasks and completion states. They are not evidence of a user trial.

[Creation page](task-monster/assets/screenshots/create.jpg) · [Grouped steps and sound switch](task-monster/assets/screenshots/steps.jpg) · [Victory](task-monster/assets/screenshots/victory.jpg) · [Read-only recap](task-monster/assets/screenshots/review.jpg).

## Run locally

Install [uv](https://docs.astral.sh/uv/getting-started/installation/). From the repository root, run:

```bash
cd task-monster
uv sync --locked
uv run streamlit run app.py
```

Python 3.13 is selected by `.python-version`; `uv.lock` records exact dependency versions. Open the local URL printed in the terminal, normally http://localhost:8501. Keep the terminal running. Press **Ctrl+C** to stop the app. After updating an already running copy, stop it, run the commands again, and refresh the browser.

## Interaction

1. Choose **Summon**, enter a quest name, optionally choose a deadline date/time in Hong Kong time, and select a type or use **Auto-detect**.
2. Add 2–24 small steps. Each step adds one monster level and 100 HP. The summon button appears above the step list after two steps are added, and the monster is revealed only after creation.
3. The **Quests** screen shows all active monsters. Choose **Enter battle** for a task.
4. Finish a step in real life, then press **Complete & strike!**. Health decreases, progress updates, and the monster reacts. Completed steps move to the bottom in completion order. Use **Undo** while the quest is active after an accidental completion.
5. Completing every step adds the monster to **Collection**. Choose **View quest** below a card to reopen its quest. A celebration dialog appears after the final step; dismiss it to return home. Completed quests are read-only.

The interface stays within a 460px phone-style frame on desktop and adapts to narrower screens. Its compact square bottom navigation uses original vector icons, reveals a label only for the selected tab, and leaves space for the end of long pages. Battle screens hide the dock and provide a game-style Back arrow. Type uses the bundled Lilita One cartoon font and a shared five-size scale.

## Files and development

- [Detailed instructions and limitations](task-monster/README.md)
- [Process, decisions, AI use and user-trial status](task-monster/PROCESS.md)
- [Interface](task-monster/app.py), [task and storage logic](task-monster/game.py), [artwork rendering and icons](task-monster/art.py)
- [Dependency metadata](task-monster/pyproject.toml) and [lockfile](task-monster/uv.lock)

[Active-card deadlines](task-monster/assets/screenshots/deadlines.jpg), [English calendar](task-monster/assets/screenshots/calendar.jpg).

## Deadlines

The optional date and time controls sit below Quest Name. Deadlines are saved in UTC and displayed in Hong Kong time on active quest cards, without a timezone suffix. Past deadlines are allowed and labelled OVERDUE. Existing tasks without a deadline show No deadline set; they are not assigned an invented date. The custom calendar uses fixed English month and weekday names. The date, hour and minute controls do not depend on the browser locale. Deadline labels and values share one row.

## Sound

Use **Sound off** beside the wallet to enable background music and effects together. The game starts muted. Sound continues through page changes; use the same switch to mute everything. Reloading resets sound to off. Background music pauses while the tab is hidden. Visual feedback remains usable without sound or Web Audio support.

The original eight-bar, 112 BPM C-major melody and effects were composed by Codex and rendered procedurally with the browser's Web Audio oscillators. This is AI-assisted composition and code synthesis, not output from a music-generation model or an external music service. No account, recording, microphone or paid service is needed. Navigation, summoning, damage, gems, undo and victory use distinct cues. See `assets/audio.js` in the app folder for the score and synthesis.

## Storage and limitations

Progress is saved to `task-monster/local_data/tasks.json`. This directory is ignored by Git, so personal tasks are not uploaded. Existing category names from the first prototype are migrated to English; user-entered task names and step text are preserved as written.

This is a single-user local prototype, with one shared save file per server. It has no accounts, cloud sync or concurrent-edit protection. Different browsers connected to the same server share that file. Quest classification uses local English keywords and deterministic rules, not an AI service. Six species are available; similar tasks may have similar monsters. All steps deal equal damage, and the app relies on the player to report real completion. The purple gem balance equals completed steps × 10 and decreases when a completion is undone. Abandoning a quest removes its contribution to this balance.

## Optional local verification

From the `task-monster` directory:

```bash
uv run --locked python -m unittest discover -s tests -v
```

There is no GitHub automatic-check workflow. With Node.js installed, run the optional audio checks with `node --test tests/audio.test.cjs` from the app directory. Program tests do not replace a real user trial or the marker's judgement.

## Credits and submission status

Python lists, dictionaries, functions, state and Streamlit concepts build on SD5913 classroom material. Monster artwork and the group portrait were supplied by the project author on 31 October 2026. Optimized transparent WebP files are bundled in task-monster/assets/monsters with source filenames and hashes in SOURCES.json. Hurt and weak expression variants were created with OpenAI built-in image generation from those supplied designs. Prompts are recorded in assets/monsters/EXPRESSION-PROMPTS.json. Navigation and feedback icons are original SVG drawn in code. Lilita One by Juan Montoreano is bundled under the SIL Open Font License; its license is included in task-monster/assets/fonts/OFL.txt. Game screenshots supplied by the project author informed visual direction; their characters, icons and other assets were not copied. Codex assisted with design, code, testing and documentation; see PROCESS for decisions and revisions.

A real trial with at least one other person and the resulting observation-based decision still need to be recorded before submission. Git history records actual revisions.
