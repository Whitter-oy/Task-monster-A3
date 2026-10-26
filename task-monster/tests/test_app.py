"""Exercise the actual Streamlit interface without opening a browser."""

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


APP = Path(__file__).resolve().parents[1] / "app.py"


class TaskMonsterTests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(APP)).run()
        self.assertFalse(self.app.exception)

    def click(self, label):
        button = next(b for b in self.app.button if b.label == label)
        button.click().run()
        self.assertFalse(self.app.exception)

    def add_step(self, title):
        field = next(
            f for f in self.app.text_input if f.label == "添加一个具体的小步骤"
        )
        field.set_value(title)
        self.click("添加步骤")

    def start_challenge(self, titles=("画草图", "做原型")):
        self.app.text_input(key="task_input").set_value("完成 A3")
        for title in titles:
            self.add_step(title)
        self.click("开始挑战")

    def toggle(self, step_id):
        self.app.button(key=f"toggle_{step_id}").click().run()
        self.assertFalse(self.app.exception)

    def test_empty_inputs_do_not_start_challenge(self):
        self.click("开始挑战")
        self.assertIn("任务名称", self.app.warning[0].value)
        self.app.text_input(key="task_input").set_value("   ").run()
        self.click("开始挑战")
        self.assertIn("任务名称", self.app.warning[0].value)
        self.add_step("   ")
        self.assertIn("不能为空", self.app.warning[0].value)
        self.assertEqual(len(self.app.session_state["steps"]), 0)
        self.app.text_input(key="task_input").set_value("完成 A3").run()
        self.click("开始挑战")
        self.assertIn("至少一个步骤", self.app.warning[0].value)
        self.assertFalse(self.app.session_state["started"])

    def test_completion_and_undo_update_feedback(self):
        self.start_challenge()
        self.assertEqual(self.app.metric[0].value, "100 / 100")
        self.toggle(0)
        self.assertEqual(self.app.metric[0].value, "50 / 100")
        self.assertEqual(self.app.progress[0].value, 50)
        self.assertEqual(self.app.button(key="toggle_0").label, "撤销")
        self.app.run()
        self.assertEqual(self.app.metric[0].value, "50 / 100")
        self.toggle(0)
        self.assertEqual(self.app.metric[0].value, "100 / 100")
        self.assertEqual(self.app.progress[0].value, 0)

    def test_victory_can_be_undone(self):
        self.start_challenge(titles=("做原型",))
        self.toggle(0)
        self.assertEqual(self.app.metric[0].value, "0 / 100")
        self.assertEqual(self.app.progress[0].value, 100)
        self.assertIn("挑战完成", self.app.success[0].value)
        self.toggle(0)
        self.assertEqual(self.app.metric[0].value, "100 / 100")
        self.assertEqual(len(self.app.success), 0)

    def test_deletion_does_not_mix_up_remaining_buttons(self):
        self.app.text_input(key="task_input").set_value("完成 A3")
        for title in ("画草图", "做原型", "试用"):
            self.add_step(title)
        self.app.button(key="delete_1").click().run()
        self.click("开始挑战")
        self.toggle(2)
        self.assertEqual(self.app.metric[0].value, "50 / 100")
        self.assertEqual(self.app.button(key="toggle_0").label, "完成")
        self.assertEqual(self.app.button(key="toggle_2").label, "撤销")

    def test_reset_requires_confirmation_and_allows_new_challenge(self):
        self.start_challenge()
        self.toggle(0)
        reset = next(b for b in self.app.button if b.label == "重新开始")
        self.assertTrue(reset.disabled)
        self.app.checkbox(key="confirm_reset").check().run()
        self.click("重新开始")
        self.assertEqual(self.app.text_input(key="task_input").value, "")
        self.assertEqual(len(self.app.session_state["steps"]), 0)
        self.start_challenge(titles=("新的步骤",))
        self.assertEqual(self.app.metric[0].value, "100 / 100")
        self.toggle(0)
        self.assertIn("挑战完成", self.app.success[0].value)


if __name__ == "__main__":
    unittest.main()
