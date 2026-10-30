"""Task state and local JSON storage, independent of the Streamlit interface."""

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

CATEGORIES = {
    "Study": ("Night Owl", "owl", "#ad91ff", "#413366"),
    "Work": ("Clockwork Golem", "golem", "#70d9ee", "#235869"),
    "Fitness": ("Ember Dragon", "dragon", "#ff9277", "#713f4d"),
    "Life": ("Forest Sprout", "plant", "#a5e276", "#3e6147"),
    "Creative": ("Muse Ghost", "ghost", "#f5a1d6", "#66446f"),
    "Other": ("Stardust Slime", "slime", "#b7a1ff", "#494475"),
}
KEYWORDS = {
    "Study": ("study", "exam", "revise", "course", "read", "homework", "a3"),
    "Work": ("work", "email", "meeting", "report"),
    "Fitness": ("run", "fitness", "gym", "exercise", "walk"),
    "Life": ("clean", "room", "laundry", "groceries", "tidy"),
    "Creative": ("design", "draw", "art", "write", "photo", "create"),
}

# Compatibility with category identifiers used by the first prototype.
LEGACY_CATEGORIES = dict(zip(
    ("\u5b66\u4e60", "\u5de5\u4f5c", "\u8fd0\u52a8", "\u751f\u6d3b", "\u521b\u4f5c", "\u5176\u4ed6"),
    CATEGORIES,
))


def normalize_category(category):
    return LEGACY_CATEGORIES.get(category, category)


def category_for(title):
    for category, words in KEYWORDS.items():
        if any(word in title.lower() for word in words):
            return category
    return list(CATEGORIES)[int(hashlib.sha256(title.encode()).hexdigest()[:8], 16) % 6]


def validate_inputs(title, step_titles, category, minimum_steps=2):
    title = title.strip()
    steps = [s.strip() for s in step_titles]
    if not title or len(title) > 60:
        raise ValueError("Enter a quest name with 1–60 characters.")
    if not minimum_steps <= len(steps) <= 24 or any(not s or len(s) > 120 for s in steps):
        raise ValueError(f"Add {minimum_steps}–24 steps, each with 1–120 characters.")
    if category == "Auto-detect":
        category = category_for(title)
    if category not in CATEGORIES:
        raise ValueError("Choose a valid quest type.")
    return title, steps, category


def create_task(title, step_titles, category="Auto-detect"):
    title, steps, category = validate_inputs(title, step_titles, category)
    return {
        "id": uuid4().hex, "title": title, "category": category,
        "steps": [{"title": s, "done": False} for s in steps],
        "created_at": datetime.now(timezone.utc).isoformat(), "completed_at": None,
    }


def completed_count(task):
    return sum(1 for step in task["steps"] if step["done"])


def gem_balance(tasks):
    """Derived rewards cannot be farmed by undoing and repeating a step."""
    return sum(completed_count(task) for task in tasks) * 10


def is_defeated(task):
    return completed_count(task) == len(task["steps"])


def health(task):
    maximum = len(task["steps"]) * 100
    return maximum - completed_count(task) * 100, maximum


def toggle_step(task, index):
    step = task["steps"][index]
    step["done"] = not step["done"]
    now = datetime.now(timezone.utc).isoformat()
    step["completed_at"] = now if step["done"] else None
    task["completed_at"] = now if is_defeated(task) else None


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
            task["category"] = normalize_category(task.get("category"))
            # Keep single-step quests saved by older releases usable.
            validate_inputs(task["title"], [s["title"] for s in task["steps"]], task["category"], minimum_steps=1)
        return tasks, None
    except (OSError, ValueError, KeyError, TypeError):
        return [], "Could not read the local save. The original file is preserved. Back it up or repair it before reopening."


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


def ordered_steps(task):
    return sorted(enumerate(task["steps"]), key=lambda item: (item[1]["done"], item[1].get("completed_at") or "", item[0]))
