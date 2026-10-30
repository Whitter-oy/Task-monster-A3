"""Local regression checks; no GitHub workflow is configured."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree
from streamlit.testing.v1 import AppTest
from art import monster_svg
from game import CATEGORIES, create_task, health, is_defeated, load_tasks, save_tasks, toggle_step, gem_balance

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
        if key.startswith("nav_") and self.app.session_state["page"] == "battle":
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

    def test_attack_gallery_and_undo_are_consistent(self):
        task_id = self.add_task("Finish A3")
        self.button(f"attack_{task_id}_0")
        self.assertEqual(health(self.app.session_state["tasks"][0]), (100, 200))
        self.button(f"attack_{task_id}_1")
        self.assertTrue(is_defeated(self.app.session_state["tasks"][0]))
        self.button("nav_gallery")
        self.assertTrue(any("trophy-stars" in m.value for m in self.app.markdown))
        self.assertFalse(any("collection-intro" in m.value for m in self.app.markdown))
        self.assertEqual(len([b for b in self.app.button if b.label == "View quest"]), 1)
        self.button(f"trophy_{task_id}")
        self.button(f"attack_{task_id}_0")
        self.assertEqual(health(self.app.session_state["tasks"][0]), (100, 200))
        self.button("nav_gallery")
        self.assertFalse(any(b.label == "View quest" for b in self.app.button))
        self.button("nav_home")
        self.assertTrue(any(b.key == f"enter_{task_id}" for b in self.app.button))

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

    def test_original_monsters_are_distinct_valid_svg_with_damage_states(self):
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
        self.click("View collection")
        self.button(f"trophy_{task_id}")
        self.button("back_to_quests")
        self.assertEqual(self.app.session_state["page"], "gallery")

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
