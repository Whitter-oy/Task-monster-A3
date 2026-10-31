# Task Monster — Making the Experience

## 1. Starting with an idea

I began with a familiar situation: knowing that an assignment needs to be finished, but finding the whole task too large to start. I wanted to make the next small action feel clearer and more approachable.

This became the idea behind Task Monster. A task becomes a monster, and each small step becomes an attack. The player's action should change something meaningful: the step becomes complete, the monster loses health and the player receives visible feedback. Finishing the whole task should feel different from finishing just one step.

I kept that loop at the center of the project. I considered the visual language of games, but left out shops, paid currency and accounts so that the experience would remain focused on doing real tasks.

## 2. Building the first working loop

I built on the Python lists, dictionaries and state concepts introduced in SD5913. The first prototype supported one task and a list of steps. I used Python dictionaries to store the task and a `done` flag for each step, then used Streamlit to display the controls and current state. Before developing the visual style, I made sure that adding steps, completing them, undoing them and reaching victory worked together.

An important decision was to calculate health from the checklist instead of keeping a separate health value:

```python
maximum = len(task["steps"]) * 100
remaining = maximum - completed_count(task) * 100
```

A four-step quest therefore starts with 400 HP. One completed step leaves 300 HP; Undo restores it to 400. The gem balance follows the same principle: it comes from the number of currently completed steps. This made the relationship between an action and its response easier to explain and kept the values consistent.

The button callback in `app.py` finds the selected quest, changes the step through `toggle_step`, saves the result and requests a feedback effect. The interface then redraws from the new task state. Keeping the saved state separate from the animation helped prevent presentation effects from changing the actual rewards.

## 3. Developing the experience around the loop

After the single-task prototype worked, I expanded it into a quest board, creation screen, battle screen and collection. Multiple quests made the app more useful for returning to unfinished work. I moved task calculations and JSON storage into `game.py`, while keeping the screens and callbacks in `app.py`.

I made the task breakdown part of creation: a new quest needs at least two steps before it can be summoned. Add step and Summon monster became separate actions with different colors and sizes. I placed the unlocked summon button above the step list so it would be easy to reach.

The early monster drawings and simple panels then developed into a consistent purple-and-gold game interface. I refined the rounded lettering, raised buttons, navigation tiles, health bars and species-colored collection cards. The group portrait introduces the characters together, while each quest keeps its own monster.

I also developed the ending of the interaction. The last step opens a celebration dialog with a distinct sound. Closing it returns to the board, and the completed monster becomes a collection card. Opening that card shows a recap rather than an editable battle. This gives each quest a clear ending and leaves a record of what was completed.

## 4. Problems I encountered and how I fixed them

### Progress needed to survive a restart

Session state was enough for the first prototype, but a returning user would need saved progress. I added local JSON storage and an atomic file replacement when saving. If loading fails, the app preserves the original file and displays a warning. This was more careful than silently replacing an unreadable save with an empty adventure.

### Moving steps could target the wrong action

I wanted completed steps to move below unfinished ones, keeping the next action near the top. Sorting the displayed rows introduced a risk: the row's visible position could differ from its original step index. I preserved the original indices when ordering the steps, so Complete and Undo continue to change the correct step after rows move.

### Buttons looked centered in code but not on screen

Repeated screenshot reviews showed that labels such as Add step and Undo sat too low. Centering the outer button did not fix the nested text wrapper. I corrected the inner line box and added a small optical adjustment. Undo also needed an explicit button width so that positioning its label would not collapse the button itself. This taught me to inspect the rendered control rather than assume that one CSS alignment rule was enough.

### Small screens exposed layout problems

Long content, navigation spacing and an oversized completion dialog were harder to judge from one screen size. The dialog's content was constrained, but its outer shell still retained a larger default width. I gave both layers matching viewport limits and allowed long content to scroll. I also checked the page and navigation at narrow phone widths and on desktop, leaving enough space to reach controls at the bottom.

### The date picker followed the browser's language

After deadlines were introduced, the browser's native calendar displayed Chinese month and weekday labels. I replaced it with fixed English month/day names. The time fields later became direct keyboard inputs with quiet labels inside the boxes. I removed repeated timezone suffixes and tightened the spacing, while retaining consistent timezone conversion when saving dates.

### Repeated rendering could repeat feedback

Streamlit redraws the interface after interactions. I kept sound playback on the parent page and used event identifiers so that a rerender would not replay a reward. Music begins only after a deliberate click and can be muted with one switch. The visual state remains understandable without audio.

## 5. Trying it with classmates and responding to feedback

Two classmates tried the app. The first studies in the same programme and knew the assignment requirements, but did not know the app's theme. I did not explain the app before they used it. The second was unfamiliar with it, so I briefly introduced its purpose before they tried it.

Both operated the app smoothly. I did not observe a specific place where either became stuck. The first trial therefore gave me a useful check of the interface without an app walkthrough; the second showed how someone used it after a brief introduction. These were qualitative observations, with no timing measurements or recorded transcript.

Their feedback suggested setting deadlines for tasks and improving the monster imagery. I responded in two ways:

- **Added optional deadlines.** I placed the date/time controls beneath Quest Name and showed the chosen deadline on each active card. Overdue labels make time context visible. The field remains optional so that a small personal task does not require an artificial due date.
- **Refined the monsters.** I replaced the simpler character bodies with the supplied polished illustrations and group portrait. I then added hurt and weak expressions for all six species, connected to their remaining health. This gives progress a visible emotional change as well as a numerical one.

I retained the main quest → step → battle → collection structure because both classmates could use it smoothly. The feedback helped me make focused improvements without adding another complex system. Names, personal tasks and recordings of the classmates are not included in the project.

## 6. What I learned

The main lesson for me is that a small interaction needs both dependable logic and carefully timed feedback. A health bar, expression and sound can support the same action, but they only make sense when they all come from consistent task state. Deriving health and gems from the checklist made Undo much easier to manage.

I also learned that visual polish can be functional. A separate summon action, a clearer button label or pending steps staying at the top can make the next action easier to understand. Small spacing and alignment problems become much more noticeable on a phone-sized interface. Looking at the rendered result at different widths was more useful than judging the code alone.

The classmate trials helped me distinguish between a flow that needed changing and a feature that could improve it. Both people could use the flow, so I kept its structure and used the feedback to add deadlines and strengthen the character feedback. I would need a longer trial to understand whether the app actually helps someone return to tasks over time; smooth operation alone does not establish that outcome.

Finally, I became more aware of the difference between testing the implementation and observing a person. The 20 local Python checks and two sound checks cover repeatable behavior such as input validation, Undo, saving and calendar entry. They complement the classmate observations, but answer different questions. The screenshots use a separate fictional save so that documenting the product does not expose anyone's real tasks.

## 7. How I used AI

I used **Codex** to help develop the idea, plan the interaction, write and refactor Python/Streamlit code, refine CSS and original SVG icons, run checks, inspect the browser result and draft documentation. I reviewed the outputs through screenshots and requested specific changes to layout, navigation, button alignment, dates, sound and artwork. The classmate trial details in this document came from my own report; the agent did not observe those sessions.

One suggestion I kept was deriving health and rewards from completion flags. It supported the intended interaction and made the result easier to reason about. I also kept the small checklist/battle loop as the core of the experience.

Some suggestions changed during iteration. Separate Music and SFX controls became one Sound switch because the extra distinction took up space without helping this small app. Simple tilt and dimming effects later became actual hurt/weak illustrations because facial expressions communicated health more clearly. I deferred persistence until the first loop worked, then added it when the app grew into multiple quests. Shops, paid currency and automatic audio playback were left out to keep attention on tasks and preserve control over sound.

For images, I supplied the finished monster originals and group portrait. The generation tool for those original files was not recorded. OpenAI built-in image generation later produced two expression variants per species while preserving the supplied character designs. I inspected the results before they were split into separate transparent WebP assets. The available image provenance and prompts remain in [SOURCES.json](task-monster/assets/monsters/SOURCES.json) and [EXPRESSION-PROMPTS.json](task-monster/assets/monsters/EXPRESSION-PROMPTS.json).

For sound, Codex composed an original eight-bar melody and short interaction cues, then implemented them with Web Audio oscillators. This was AI-assisted composition and code synthesis, rather than a recording produced by a dedicated music-generation model. The runtime app does not call an AI service. AI helped me build and revise the experience, while the decisions about what to keep were guided by the task loop, my reviews and the classmates' feedback.
