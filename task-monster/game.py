"""Task state and local JSON storage, independent of the Streamlit interface."""

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

CATEGORIES = {
    "学习": ("夜读魔枭", "owl", "#ad91ff", "#413366"),
    "工作": ("齿轮石像", "golem", "#70d9ee", "#235869"),
    "运动": ("烈焰幼龙", "dragon", "#ff9277", "#713f4d"),
    "生活": ("森林芽灵", "plant", "#a5e276", "#3e6147"),
    "创作": ("灵感幽灵", "ghost", "#f5a1d6", "#66446f"),
    "其他": ("星尘史莱姆", "slime", "#b7a1ff", "#494475"),
}
KEYWORDS = {
    "学习": ("学习", "作业", "考试", "复习", "课程", "读书", "study", "exam", "a3"),
    "工作": ("工作", "邮件", "会议", "报告", "work", "email"),
    "运动": ("跑步", "运动", "健身", "散步", "run", "gym"),
    "生活": ("整理", "清洁", "房间", "买菜", "洗", "clean"),
    "创作": ("设计", "画", "创作", "写", "摄影", "design", "draw"),
}


def category_for(title):
    for category, words in KEYWORDS.items():
        if any(word in title.lower() for word in words):
            return category
    return list(CATEGORIES)[int(hashlib.sha256(title.encode()).hexdigest()[:8], 16) % 6]


def create_task(title, step_titles, category="自动识别"):
    title = title.strip()
    steps = [s.strip() for s in step_titles]
    if not title or len(title) > 60:
        raise ValueError("请填写 1–60 字的任务名称。")
    if not 1 <= len(steps) <= 24 or any(not s or len(s) > 120 for s in steps):
        raise ValueError("请添加 1–24 个步骤，每步为 1–120 字。")
    if category == "自动识别":
        category = category_for(title)
    if category not in CATEGORIES:
        raise ValueError("请选择有效的任务类型。")
    return {
        "id": uuid4().hex, "title": title, "category": category,
        "steps": [{"title": s, "done": False} for s in steps],
        "created_at": datetime.now(timezone.utc).isoformat(), "completed_at": None,
    }


def completed_count(task):
    return sum(1 for step in task["steps"] if step["done"])


def is_defeated(task):
    return completed_count(task) == len(task["steps"])


def health(task):
    maximum = len(task["steps"]) * 100
    return maximum - completed_count(task) * 100, maximum


def toggle_step(task, index):
    step = task["steps"][index]
    step["done"] = not step["done"]
    task["completed_at"] = datetime.now(timezone.utc).isoformat() if is_defeated(task) else None


def load_tasks(path):
    if not path.exists():
        return [], None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or payload.get("version") != 1:
            raise ValueError("unsupported version")
        tasks = payload["tasks"]
        if not isinstance(tasks, list):
            raise ValueError("invalid tasks")
        ids = set()
        for task in tasks:
            if not isinstance(task, dict) or not isinstance(task.get("id"), str):
                raise ValueError("invalid task")
            if task["id"] in ids:
                raise ValueError("duplicate task")
            ids.add(task["id"])
            if not isinstance(task.get("title"), str) or not isinstance(task.get("steps"), list):
                raise ValueError("invalid fields")
            for step in task["steps"]:
                if not isinstance(step, dict) or not isinstance(step.get("title"), str) or type(step.get("done")) is not bool:
                    raise ValueError("invalid step")
            create_task(task["title"], [s["title"] for s in task["steps"]], task.get("category"))
        return tasks, None
    except (OSError, ValueError, KeyError, TypeError):
        return [], "未能读取本机存档。原文件已保留；请先备份或修复它，再重新打开。"


def save_tasks(path, tasks):
    """Replace atomically so an interrupted save does not leave half a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            json.dump({"version": 1, "tasks": tasks}, handle, ensure_ascii=False, indent=2)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
