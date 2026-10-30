import html
import base64
import os
from pathlib import Path

import streamlit as st

from art import monster_svg, navigation_svg
from game import CATEGORIES, category_for, completed_count, create_task, health, is_defeated, load_tasks, save_tasks, toggle_step, normalize_category

ROOT = Path(__file__).resolve().parent
DATA_FILE = Path(os.environ.get("TASK_MONSTER_DATA_FILE", ROOT / "local_data" / "tasks.json"))
st.set_page_config(page_title="Task Monster · Quest Adventure", page_icon="⚔️", layout="centered", initial_sidebar_state="collapsed")
icon_css = "\n".join(
    f'.st-key-nav_{page} button::before{{background-image:url("data:image/svg+xml;base64,{base64.b64encode(navigation_svg(page).encode()).decode()}");}}'
    for page in ("home", "create", "gallery")
)
st.markdown(f"<style>{(ROOT / 'assets' / 'game.css').read_text()}{icon_css}</style>", unsafe_allow_html=True)

if "tasks" not in st.session_state:
    tasks, error = load_tasks(DATA_FILE)
    st.session_state.update(tasks=tasks, page="home", selected=None, draft=[], storage_error=error, notice=None, effect=None)

# Keep an already-open creation screen usable after the language update.
if "new_category" in st.session_state:
    selected_category = normalize_category(st.session_state.new_category)
    st.session_state.new_category = selected_category if selected_category in CATEGORIES else "Auto-detect"


def markup(content):
    st.markdown(content, unsafe_allow_html=True)


def esc(value):
    return html.escape(str(value))


def navigate(page, task_id=None):
    st.session_state.page = page
    st.session_state.selected = task_id
    st.session_state.effect = None


def persist():
    # A damaged file is preserved rather than overwritten with an empty session.
    if st.session_state.storage_error:
        return
    try:
        save_tasks(DATA_FILE, st.session_state.tasks)
    except OSError:
        st.session_state.storage_error = "Could not save progress. You can keep playing in this session; check folder permissions."


def attack(task_id, index):
    task = next(t for t in st.session_state.tasks if t["id"] == task_id)
    was_done = task["steps"][index]["done"]
    toggle_step(task, index)
    st.session_state.effect = "undo" if was_done else "attack"
    persist()


def drop_draft(index):
    st.session_state.draft.pop(index)


def abandon(task_id):
    st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task_id]
    persist()
    navigate("home")


tasks = st.session_state.tasks
for task in tasks:
    task["category"] = normalize_category(task["category"])
active = [t for t in tasks if not is_defeated(t)]
defeated = [t for t in tasks if is_defeated(t)]
finished_steps = sum(completed_count(t) for t in tasks)
markup(f'<div class="topbar"><div class="brand">TASK MONSTER<small>TURN TO-DOS INTO ADVENTURES</small></div><div class="gem-count"><span class="gem">◆</span> {finished_steps * 10} <span style="font-size:9px;color:#a89aba">XP</span></div></div>')
if st.session_state.storage_error:
    st.warning(st.session_state.storage_error + " Session mode is active. The original save will not be overwritten.")
if st.session_state.notice:
    st.success(st.session_state.notice)
    st.session_state.notice = None

page = st.session_state.page

if page == "home":
    markup('<div class="page-heading"><h1>Quest board</h1><span>QUEST BOARD</span></div><div class="subcopy">Every small step is a battle worth winning.</div>')
    markup(f'<div class="hero"><span class="hero-label">YOUR NEXT ADVENTURE</span><h2>Big quest?<br>Small steps.</h2><p>Break it down. Finish a step.<br>Land your next hit.</p><div class="hero-art">{monster_svg("Other", "hero")}</div></div>')
    if st.button("Summon a new quest", type="primary", use_container_width=True):
        navigate("create")
        st.rerun()
    markup(f'<div class="stats"><div class="stat"><strong>{len(active):02d}</strong><small>Active quests</small></div><div class="stat"><strong>{len(defeated):02d}</strong><small>Monsters defeated</small></div><div class="stat"><strong>{finished_steps:02d}</strong><small>Steps completed</small></div></div>')
    markup(f'<div class="section-line"><h2>Active quests</h2><small>{len(active)} quests</small></div>')
    if not active:
        markup('<div class="empty-state"><div class="empty-icon">✧</div><h3>Your next adventure starts here</h3><p>Name a real task and add a few small steps.<br>Your first monster is waiting.</p></div>')
    for task in active:
        name, _, color, shade = CATEGORIES[task["category"]]
        hp, maximum = health(task)
        ratio = hp / maximum
        with st.container(key=f"quest_{task['id']}"):
            markup(f'<div class="quest-banner" style="--accent:{color};--shade:{shade}"><span class="tag">{esc(task["category"])} / {name}</span><span class="level">Lv. {len(task["steps"]):02d}</span><h3>{esc(task["title"])}</h3><div class="monster-mini">{monster_svg(task["category"],task["title"],1-ratio)}</div><div class="hp-line"><div class="hp-track"><div class="hp-fill" style="width:{ratio*100}%"></div></div><div class="hp-label"><span>HP {hp} / {maximum}</span><span>{completed_count(task)}/{len(task["steps"])} steps</span></div></div></div>')
            st.button("Enter battle", key=f"enter_{task['id']}", on_click=navigate, args=("battle", task["id"]), use_container_width=True)

elif page == "create":
    markup('<div class="page-heading"><h1>Summon a monster</h1><span>NEW QUEST</span></div><div class="subcopy">Name your quest. Make the first step easy to start.</div>')
    title = st.text_input("Quest name", key="new_title", placeholder="e.g. Finish my A3 project", max_chars=60)
    category = st.selectbox("Quest type", ["Auto-detect"] + list(CATEGORIES), key="new_category")
    chosen = category_for(title.strip()) if category == "Auto-detect" else category
    name, _, color, shade = CATEGORIES[chosen]
    level = len(st.session_state.draft)
    markup(f'<div class="quest-banner" style="--accent:{color};--shade:{shade}"><span class="tag">MONSTER PREVIEW · {chosen}</span><span class="level">Lv. {level:02d}</span><h3>{name}</h3><div class="species">1 step = 1 level + 100 HP<br>More steps, a higher-level monster</div><div class="monster-mini">{monster_svg(chosen,title)}</div></div>')
    markup('<div class="section-line"><h2>Quest steps</h2><small>Aim for 3–5 · max. 24</small></div>')
    with st.form("add_step_form", clear_on_submit=True):
        draft_title = st.text_input("Add a small step", placeholder="e.g. Sketch the three main screens", max_chars=120)
        add = st.form_submit_button("Add step", use_container_width=True)
    if add:
        if not draft_title.strip():
            st.warning("A step cannot be empty. Add one small action you can take.")
        elif len(st.session_state.draft) >= 24:
            st.warning("A quest can have up to 24 steps. Try splitting it into two quests.")
        else:
            st.session_state.draft.append(draft_title.strip())
            st.rerun()
    for i, step in enumerate(st.session_state.draft):
        with st.container(key=f"step_draft_{i}"):
            markup(f'<div class="step-line"><span class="step-number">{i+1:02d}</span><div class="step-copy">{esc(step)}</div></div>')
            st.button("Remove step", key=f"remove_draft_{i}", on_click=drop_draft, args=(i,))
    if st.button("Summon monster", type="primary", use_container_width=True):
        try:
            task = create_task(title, st.session_state.draft, category)
        except ValueError as error:
            st.warning(str(error))
        else:
            tasks.append(task)
            persist()
            st.session_state.draft = []
            st.session_state.notice = f"{task['title']} is ready for battle!"
            navigate("battle", task["id"])
            st.rerun()

elif page == "battle":
    task = next((t for t in tasks if t["id"] == st.session_state.selected), None)
    if task is None:
        navigate("home")
        st.rerun()
    st.button("Back to quests", on_click=navigate, args=("home",))
    name = CATEGORIES[task["category"]][0]
    hp, maximum = health(task)
    victory = is_defeated(task)
    effect = st.session_state.effect
    markup(f'<div class="battle-title"><h1>{esc(task["title"])}</h1><span class="tag">Lv. {len(task["steps"]):02d}</span></div><div class="subcopy">{task["category"]} realm · {name}</div>')
    markup(f'<div class="battle-hp"><div class="hp-label"><span>MONSTER HP</span><span>{hp} / {maximum}</span></div><div class="hp-track"><div class="hp-fill" style="width:{hp/maximum*100}%"></div></div></div>')
    floating = '<div class="damage">−100 HP</div>' if effect == "attack" else ('<div class="damage">＋100 HP</div>' if effect == "undo" else '')
    markup(f'<div class="arena {"victory" if victory else ""} {"hurt" if effect == "attack" else ""}">{floating}<div class="arena-monster">{monster_svg(task["category"],task["title"],1-hp/maximum,victory)}</div><div class="arena-note">{"QUEST COMPLETE · MONSTER COLLECTED" if victory else "Finish a real-world step, then strike below"}</div></div>')
    if victory:
        markup('<div class="victory-banner"><strong>QUEST COMPLETE!</strong><small>You did it! Your monster is now in the collection.</small></div>')
        st.button("View collection", type="primary", on_click=navigate, args=("gallery",))
    markup(f'<div class="section-line"><h2>Your steps · {completed_count(task)}/{len(task["steps"])}</h2><small>Each step deals 100 damage</small></div>')
    for i, step in enumerate(task["steps"]):
        with st.container(key=f"step_{task['id']}_{i}"):
            markup(f'<div class="step-line {"done" if step["done"] else ""}"><span class="step-number">{"✓" if step["done"] else f"{i+1:02d}"}</span><div class="step-copy">{esc(step["title"])}<small>{"Completed · undo if needed" if step["done"] else "Finish, then strike · −100 HP"}</small></div></div>')
            st.button("Undo step" if step["done"] else "Complete & strike!", key=f"attack_{task['id']}_{i}", type="secondary" if step["done"] else "primary", on_click=attack, args=(task["id"], i), use_container_width=True)
    with st.expander("Quest options"):
        st.caption("Abandoning removes this quest and its progress. Other quests are kept.")
        confirmed = st.checkbox("I confirm I want to abandon this quest", key=f"confirm_{task['id']}")
        st.button("Abandon quest", disabled=not confirmed, on_click=abandon, args=(task["id"],))

elif page == "gallery":
    markup('<div class="page-heading"><h1>Collection</h1><span>MONSTER COLLECTION</span></div><div class="subcopy">Once a challenge. Now part of your story.</div>')
    markup(f'<div class="collection-intro"><span class="medal">✹</span><div><strong>{len(defeated):02d} monsters defeated</strong><small>Every card represents a real quest you finished.</small></div></div>')
    if not defeated:
        markup('<div class="empty-state"><div class="empty-icon">♜</div><h3>Your first trophy is out there</h3><p>Complete every step of a quest<br>to collect its monster card here.</p></div>')
        st.button("Back to quests", on_click=navigate, args=("home",), type="primary")
    for row in range(0, len(defeated), 2):
        columns = st.columns(2)
        for column, task in zip(columns, list(reversed(defeated))[row:row+2]):
            with column:
                name = CATEGORIES[task["category"]][0]
                step_label = "step" if len(task["steps"]) == 1 else "steps"
                markup(f'<div class="trophy"><span class="tag">Lv. {len(task["steps"]):02d} · {task["category"]}</span>{monster_svg(task["category"],task["title"],trophy=True)}<strong>{name}</strong><div class="task-title">{esc(task["title"])}</div><div class="stars">✦ ✦ ✦</div><div class="trophy-foot">DEFEATED · {len(task["steps"])} {step_label} completed</div></div>')
                st.button("View quest", key=f"trophy_{task['id']}", on_click=navigate, args=("battle", task["id"]))

markup('<div class="save-note">LOCAL SAVE · YOUR ADVENTURE, YOUR PACE</div><div class="nav-clearance" aria-hidden="true"></div>')
with st.container(key="bottom_nav"):
    for column, (label, target) in zip(st.columns(3), [("Quests", "home"), ("Summon", "create"), ("Collection", "gallery")]):
        with column:
            st.button(label, key=f"nav_{target}", type="primary" if page == target or (page == "battle" and target == "home") else "secondary", on_click=navigate, args=(target,), use_container_width=True)

# Page changes should not inherit the previous page's scroll position.
route = (page, st.session_state.selected)
if st.session_state.get("rendered_route") != route:
    with st.container(key="route_scroll"):
        st.iframe("""<script>
        setTimeout(() => {
          const main = window.parent.document.querySelector('[data-testid="stMain"]');
          if (main) main.scrollTo({top: 0, behavior: 'instant'});
        }, 100);
        </script>""", height=1)
    st.session_state.rendered_route = route
