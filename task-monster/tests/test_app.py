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
from game import CATEGORIES, create_task, health, is_defeated, load_tasks, save_tasks, toggle_step

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
        self.app.button(key=key).click().run()
        self.assertFalse(self.app.exception)

    def click(self, label):
        next(b for b in self.app.button if b.label == label).click().run()
        self.assertFalse(self.app.exception)

    def add_task(self, title, steps=("第一步", "第二步")):
        self.button("nav_create")
        self.app.text_input(key="new_title").set_value(title).run()
        for step in steps:
            next(f for f in self.app.text_input if f.label == "添加一个小步骤").set_value(step)
            self.click("＋ 添加步骤")
        self.click("⚔  召唤怪兽，开始挑战")
        return self.app.session_state["tasks"][-1]["id"]

    def test_empty_inputs_and_multiple_tasks(self):
        self.button("nav_create")
        self.click("⚔  召唤怪兽，开始挑战")
        self.assertIn("任务名称", self.app.warning[0].value)
        next(f for f in self.app.text_input if f.label == "添加一个小步骤").set_value("   ")
        self.click("＋ 添加步骤")
        self.assertIn("不能为空", self.app.warning[0].value)
        self.app.text_input(key="new_title").set_value("学习").run()
        self.click("⚔  召唤怪兽，开始挑战")
        self.assertIn("步骤", self.app.warning[0].value)
        first = self.add_task("复习考试")
        second = self.add_task("跑步运动", ("穿鞋",))
        self.assertNotEqual(first, second)
        self.assertEqual(len(self.app.session_state["tasks"]), 2)
        self.assertNotEqual(*[t["category"] for t in self.app.session_state["tasks"]])
        self.button("nav_home")
        self.assertEqual(len([b for b in self.app.button if b.label == "进入战斗  →"]), 2)

    def test_attack_gallery_and_undo_are_consistent(self):
        task_id = self.add_task("完成 A3")
        self.button(f"attack_{task_id}_0")
        self.assertEqual(health(self.app.session_state["tasks"][0]), (100, 200))
        self.button(f"attack_{task_id}_1")
        self.assertTrue(is_defeated(self.app.session_state["tasks"][0]))
        self.button("nav_gallery")
        self.assertTrue(any("只怪兽已击败" in m.value and "01" in m.value for m in self.app.markdown))
        self.button(f"trophy_{task_id}")
        self.button(f"attack_{task_id}_0")
        self.assertEqual(health(self.app.session_state["tasks"][0]), (100, 200))
        self.button("nav_gallery")
        self.assertFalse(any(b.label == "查看战绩" for b in self.app.button))
        self.button("nav_home")
        self.assertTrue(any(b.key == f"enter_{task_id}" for b in self.app.button))

    def test_progress_survives_new_session(self):
        task_id = self.add_task("整理房间")
        self.button(f"attack_{task_id}_0")
        restored = AppTest.from_file(str(APP)).run()
        self.assertFalse(restored.exception)
        self.assertEqual(health(restored.session_state["tasks"][0]), (100, 200))

    def test_abandon_requires_confirmation_and_keeps_other_tasks(self):
        first = self.add_task("学习")
        second = self.add_task("跑步")
        button = next(b for b in self.app.button if b.label == "放弃并移除")
        self.assertTrue(button.disabled)
        self.app.checkbox(key=f"confirm_{second}").check().run()
        self.click("放弃并移除")
        self.assertEqual([t["id"] for t in self.app.session_state["tasks"]], [first])

    def test_broken_save_is_not_overwritten(self):
        self.file.write_text("broken json")
        app = AppTest.from_file(str(APP)).run()
        self.assertTrue(app.warning)
        self.assertEqual(self.file.read_text(), "broken json")
        self.assertEqual(load_tasks(self.file)[0], [])

    def test_level_health_and_storage_validation(self):
        task = create_task("写作品", ["一步", "两步", "三步"])
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
        self.assertNotEqual(monster_svg("学习", "a", 0), monster_svg("学习", "a", .75))
        self.assertNotEqual(monster_svg("学习", "a", .75), monster_svg("学习", "a", trophy=True))


if __name__ == "__main__":
    unittest.main()
