"""Local regression checks; no GitHub workflow is configured."""
import json
import os
import tempfile
import unittest
from datetime import date, time, datetime, timezone
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree
from streamlit.testing.v1 import AppTest
from art import monster_svg, monster_state
from game import CATEGORIES, create_task, health, is_defeated, load_tasks, save_tasks, toggle_step, gem_balance, deadline_details

APP = Path(__file__).resolve().parents[1] / "app.py"


class TaskMonsterTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.file = Path(self.directory.name) / "tasks.json"
        self.environment = patch.dict(os.environ, {"TASK_MONSTER_DATA_FILE": str(self.file)})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.app = AppTest.from_file(str(APP)).run()
        self.assertFalse(self.app.exception)

    def button(self, key):
        if key.startswith("nav_") and self.app.session_state["page"] in ("battle", "review"):
            if self.app.session_state.get("pending_victory"):
                self.app.button(key="finish_celebration").click().run()
            else:
                self.app.button(key="back_to_quests").click().run()
        self.app.button(key=key).click().run()
        self.assertFalse(self.app.exception)

    def click(self, label):
        next(b for b in self.app.button if b.label == label).click().run()
        self.assertFalse(self.app.exception)

    def add_task(self, title, steps=("First step", "Second step")):
        self.button("nav_create")
        self.app.text_input(key="new_title").set_value(title).run()
        for step in steps:
            next(f for f in self.app.text_input if f.label == "Add a small step").set_value(step)
            self.click("Add step")
        self.click("Summon monster")
        return self.app.session_state["tasks"][-1]["id"]

    def test_two_step_gate_and_mystery_before_summoning(self):
        self.button("nav_create")
        self.assertFalse(any(b.label == "Summon monster" for b in self.app.button))
        self.assertFalse(any('<div class="monster-mini"' in m.value or "MONSTER PREVIEW" in m.value for m in self.app.markdown))
        next(f for f in self.app.text_input if f.label == "Add a small step").set_value("   ")
        self.click("Add step")
        self.assertIn("cannot be empty", self.app.warning[0].value)
        for index in range(2):
            next(f for f in self.app.text_input if f.label == "Add a small step").set_value(f"Action {index}")
            self.click("Add step")
            self.assertEqual(any(b.label == "Summon monster" for b in self.app.button), index == 1)
        self.click("Summon monster")
        self.assertIn("quest name", self.app.warning[0].value)
        self.button("remove_draft_0")
        self.assertFalse(any(b.label == "Summon monster" for b in self.app.button))

    def test_multiple_tasks(self):
        first = self.add_task("Revise for exams")
        second = self.add_task("Go for a run", ("Put on trainers", "Run for ten minutes"))
        self.assertNotEqual(first, second)
        self.assertEqual(len(self.app.session_state["tasks"]), 2)
        self.assertNotEqual(*[t["category"] for t in self.app.session_state["tasks"]])
        self.button("nav_home")
        self.assertEqual(len([b for b in self.app.button if b.label == "Enter battle"]), 2)

    def test_victory_returns_home_and_collection_is_read_only(self):
        task_id = self.add_task("Finish A3")
        self.button(f"attack_{task_id}_0")
        self.assertEqual(health(self.app.session_state["tasks"][0]), (100, 200))
        self.button(f"attack_{task_id}_0")
        self.assertEqual(health(self.app.session_state["tasks"][0]), (200, 200))
        self.button(f"attack_{task_id}_0")
        self.button(f"attack_{task_id}_1")
        self.assertTrue(is_defeated(self.app.session_state["tasks"][0]))
        self.assertTrue(self.app.session_state["tasks"][0]["completed_at"])
        self.button("finish_celebration")
        self.assertEqual(self.app.session_state["page"], "home")
        self.assertIsNone(self.app.session_state["pending_victory"])
        self.button("nav_gallery")
        self.button(f"trophy_{task_id}")
        self.assertEqual(self.app.session_state["page"], "review")
        self.assertFalse(any(b.label in ("Undo", "Abandon quest", "Complete & strike!") for b in self.app.button))
        self.assertFalse(any('<div class="battle-hp"' in m.value for m in self.app.markdown))
        self.assertFalse(any("HKT" in m.value for m in self.app.markdown))
        self.button("back_to_quests")
        self.assertEqual(self.app.session_state["page"], "gallery")

    def test_completed_steps_move_to_bottom_without_changing_attack_index(self):
        task_id = self.add_task("Read a book", ("First", "Second", "Third"))
        self.button(f"attack_{task_id}_1")
        from game import ordered_steps
        self.assertEqual([i for i,s in ordered_steps(self.app.session_state["tasks"][0])], [0,2,1])
        self.button(f"attack_{task_id}_0")
        self.assertEqual([i for i,s in ordered_steps(self.app.session_state["tasks"][0])], [2,1,0])
        self.button(f"attack_{task_id}_1")
        self.assertEqual([i for i,s in ordered_steps(self.app.session_state["tasks"][0])], [1,2,0])

    def test_progress_survives_new_session(self):
        task_id = self.add_task("Clean my room")
        self.button(f"attack_{task_id}_0")
        restored = AppTest.from_file(str(APP)).run()
        self.assertFalse(restored.exception)
        self.assertEqual(health(restored.session_state["tasks"][0]), (100, 200))

    def test_abandon_requires_confirmation_and_keeps_other_tasks(self):
        first = self.add_task("Study")
        second = self.add_task("Run")
        button = next(b for b in self.app.button if b.label == "Abandon quest")
        self.assertTrue(button.disabled)
        self.app.checkbox(key=f"confirm_{second}").check().run()
        self.click("Abandon quest")
        self.assertEqual([t["id"] for t in self.app.session_state["tasks"]], [first])

    def test_broken_save_is_not_overwritten(self):
        self.file.write_text("broken json")
        app = AppTest.from_file(str(APP)).run()
        self.assertTrue(app.warning)
        self.assertEqual(self.file.read_text(), "broken json")
        self.assertEqual(load_tasks(self.file)[0], [])

    def test_level_health_and_storage_validation(self):
        task = create_task("Create an artwork", ["Step one", "Step two", "Step three"])
        self.assertEqual(health(task), (300, 300))
        toggle_step(task, 0)
        save_tasks(self.file, [task])
        self.assertEqual(load_tasks(self.file)[0], [task])
        bad = {"version": 1, "tasks": [{**task, "steps": [{"title": "x", "done": "false"}]}]}
        self.file.write_text(json.dumps(bad))
        self.assertIsNotNone(load_tasks(self.file)[1])
        with self.assertRaises(ValueError):
            create_task("x", [])

    def test_supplied_monsters_are_distinct_valid_svg_with_damage_states(self):
        drawings = [monster_svg(category, "example") for category in CATEGORIES]
        self.assertEqual(len(set(drawings)), 6)
        for drawing in drawings:
            ElementTree.fromstring(drawing)
        self.assertNotEqual(monster_svg("Study", "a", 0), monster_svg("Study", "a", .75))
        self.assertNotEqual(monster_svg("Study", "a", .75), monster_svg("Study", "a", trophy=True))

    def test_legacy_category_migrates_without_changing_user_content(self):
        task = create_task("My existing task", ["My existing step", "Another step"])
        task["steps"] = task["steps"][:1]
        task["category"] = "\u5b66\u4e60"
        save_tasks(self.file, [task])
        tasks, error = load_tasks(self.file)
        self.assertIsNone(error)
        self.assertEqual(tasks[0]["category"], "Study")
        self.assertEqual(tasks[0]["title"], "My existing task")
        self.assertEqual(tasks[0]["steps"][0]["title"], "My existing step")

    def test_gems_follow_completions_and_cannot_be_farmed(self):
        task_id = self.add_task("Finish A3")
        self.assertEqual(gem_balance(self.app.session_state["tasks"]), 0)
        self.button(f"attack_{task_id}_0")
        self.assertEqual(gem_balance(self.app.session_state["tasks"]), 10)
        self.assertTrue(any("reward = " in frame.proto.srcdoc for frame in self.app.get("iframe")))
        self.assertFalse(any("✓" in m.value for m in self.app.markdown))
        self.app.run()
        self.assertFalse(any("reward = " in frame.proto.srcdoc for frame in self.app.get("iframe")))
        self.button(f"attack_{task_id}_0")
        self.assertEqual(gem_balance(self.app.session_state["tasks"]), 0)
        self.button(f"attack_{task_id}_0")
        self.assertEqual(gem_balance(self.app.session_state["tasks"]), 10)
        restored = AppTest.from_file(str(APP)).run()
        self.assertFalse(restored.exception)
        self.assertEqual(gem_balance(restored.session_state["tasks"]), 10)

    def test_battle_has_back_button_without_primary_navigation(self):
        task_id = self.add_task("Finish a project")
        self.assertFalse(any((b.key or "").startswith("nav_") for b in self.app.button))
        self.button("back_to_quests")
        self.assertEqual(self.app.session_state["page"], "home")
        self.button(f"enter_{task_id}")
        self.button(f"attack_{task_id}_0")
        self.button(f"attack_{task_id}_1")
        self.assertFalse(any(b.label == "View collection" for b in self.app.button))
        self.assertFalse(any('<div class="victory-banner"' in m.value for m in self.app.markdown))
        self.button("finish_celebration")
        self.button("nav_gallery")
        self.button(f"trophy_{task_id}")
        self.button("back_to_quests")
        self.assertEqual(self.app.session_state["page"], "gallery")

    def test_every_species_changes_expression_and_undo_restores_it(self):
        for category in CATEGORIES:
            states = [monster_svg(category, damage=damage) for damage in (0, .25, .75)]
            self.assertEqual(len(set(states)), 3)
            for state, drawing in zip(("healthy", "hurt", "weak"), states):
                self.assertIn(f'data-monster-state="{state}"', drawing)
                ElementTree.fromstring(drawing)
            self.assertIn('data-monster-state="collected"', monster_svg(category, damage=1, trophy=True))
        task = create_task("Read", ["One", "Two", "Three"])
        toggle_step(task, 0)
        toggle_step(task, 1)
        self.assertEqual(monster_state(1-health(task)[0]/health(task)[1]), "weak")
        toggle_step(task, 1)
        self.assertEqual(monster_state(1-health(task)[0]/health(task)[1]), "hurt")
        toggle_step(task, 0)
        self.assertEqual(monster_state(1-health(task)[0]/health(task)[1]), "healthy")

    def test_deadline_widgets_save_hong_kong_time_and_show_on_active_card(self):
        self.button("nav_create")
        self.app.text_input(key="new_title").set_value("Prepare a presentation").run()
        self.app.selectbox(key="deadline_month").select("November").run()
        self.app.number_input(key="deadline_year").set_value(2026).run()
        self.button("deadline_day_2026_11_1")
        self.app.text_input(key="deadline_hour_text").set_value("23").run()
        self.app.text_input(key="deadline_minute_text").set_value("59").run()
        for step in ("Draft the slides", "Rehearse"):
            next(f for f in self.app.text_input if f.label == "Add a small step").set_value(step)
            self.click("Add step")
        self.click("Summon monster")
        task=self.app.session_state["tasks"][0]
        self.assertIsNone(self.app.session_state["new_due_date"])
        self.assertEqual(task["due_at"], "2026-11-01T15:59:00+00:00")
        self.assertEqual(load_tasks(self.file)[0][0]["due_at"],task["due_at"])
        self.button("nav_home")
        self.assertTrue(any("01 Nov 2026 · 23:59" in m.value for m in self.app.markdown))

    def test_keyboard_deadline_rejects_invalid_time_without_saving(self):
        self.button("nav_create")
        self.app.text_input(key="new_title").set_value("Plan tomorrow").run()
        self.app.selectbox(key="deadline_month").select("November").run()
        self.app.number_input(key="deadline_year").set_value(2026).run()
        self.button("deadline_day_2026_11_1")
        for step in ("Plan", "Review"):
            next(f for f in self.app.text_input if f.label == "Add a small step").set_value(step)
            self.click("Add step")
        for hour, minute in (("24", "00"), ("23", "60"), ("", "30"), ("ab", "15")):
            self.app.text_input(key="deadline_hour_text").set_value(hour)
            self.app.text_input(key="deadline_minute_text").set_value(minute)
            self.click("Summon monster")
            self.assertIn("Enter an hour", self.app.warning[0].value)
            self.assertEqual(self.app.session_state["tasks"], [])
        self.app.text_input(key="deadline_hour_text").set_value("9")
        self.app.text_input(key="deadline_minute_text").set_value("05")
        self.click("Summon monster")
        self.assertEqual(self.app.session_state["tasks"][0]["due_at"], "2026-11-01T01:05:00+00:00")

    def test_english_calendar_handles_leap_day_and_clear(self):
        self.button("nav_create")
        self.assertEqual(len(self.app.date_input), 0)
        self.assertEqual(len(self.app.time_input), 0)
        self.app.selectbox(key="deadline_month").select("February").run()
        self.app.number_input(key="deadline_year").set_value(2028).run()
        self.button("deadline_day_2028_2_29")
        self.assertEqual(self.app.session_state["new_due_date"], date(2028,2,29))
        self.app.number_input(key="deadline_year").set_value(2027).run()
        self.assertFalse(any(b.key == "deadline_day_2027_2_29" for b in self.app.button))
        self.button("clear_deadline")
        self.assertIsNone(self.app.session_state["new_due_date"])

    def test_deadline_optional_legacy_and_overdue_status(self):
        task=create_task("Read", ["One", "Two"], due_at="2026-10-31T10:00:00+08:00")
        label,overdue=deadline_details(task,datetime(2026,10,31,3,tzinfo=timezone.utc))
        self.assertTrue(overdue)
        self.assertIn("10:00",label)
        self.assertFalse(deadline_details(task,datetime(2026,10,31,1,tzinfo=timezone.utc))[1])
        task.pop("due_at")
        save_tasks(self.file,[task])
        restored,error=load_tasks(self.file)
        self.assertIsNone(error)
        self.assertEqual(deadline_details(restored[0]),("No deadline set",False))
        self.assertIsNone(create_task("Read",["One","Two"])["due_at"])

    def test_invalid_deadline_is_rejected_and_invalid_save_preserved(self):
        for bad in ("not a date", "2026-11-01T12:00:00",123):
            with self.assertRaises(ValueError):
                create_task("Read",["One","Two"],due_at=bad)
        task=create_task("Read",["One","Two"])
        task["due_at"]="bad date"
        save_tasks(self.file,[task])
        before=self.file.read_bytes()
        self.assertIsNotNone(load_tasks(self.file)[1])
        self.assertEqual(self.file.read_bytes(),before)

    def test_new_single_step_tasks_are_rejected(self):
        with self.assertRaises(ValueError):
            create_task("Too small", ["Only one step"])

    def test_open_legacy_creation_screen_remains_usable(self):
        self.app.session_state["page"] = "create"
        self.app.session_state["new_category"] = "\u5b66\u4e60"
        self.app.run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.selectbox(key="new_category").value, "Study")


if __name__ == "__main__":
    unittest.main()
