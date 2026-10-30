import html
import json
import base64
import os
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

from art import monster_svg, navigation_svg, gem_svg, star_svg, remove_svg
from game import CATEGORIES, category_for, completed_count, create_task, health, is_defeated, load_tasks, save_tasks, toggle_step, normalize_category, gem_balance, ordered_steps

ROOT = Path(__file__).resolve().parent
DATA_FILE = Path(os.environ.get("TASK_MONSTER_DATA_FILE", ROOT / "local_data" / "tasks.json"))
st.set_page_config(page_title="Task Monster · Quest Adventure", page_icon="⚔️", layout="centered", initial_sidebar_state="collapsed")
icon_css = "\n".join(
    f'.st-key-nav_{page} button::before{{background-image:url("data:image/svg+xml;base64,{base64.b64encode(navigation_svg(page).encode()).decode()}");}}'
    for page in ("home", "create", "gallery")
)
icon_css += "\n" + "\n".join(
    f'{selector}::before{{background-image:url("data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}");}}'
    for selector, svg in [
        ('[class*="st-key-remove_draft_"] button', remove_svg()),
    ]
)
font_css = "@font-face{font-family:GameFont;src:url(data:font/ttf;base64," + base64.b64encode((ROOT / "assets/fonts/LilitaOne-Regular.ttf").read_bytes()).decode() + ") format('truetype');font-weight:100 900;font-display:swap;}"
st.markdown(f"<style>{font_css}{(ROOT / 'assets' / 'game.css').read_text()}{icon_css}</style>", unsafe_allow_html=True)

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
    if page == "battle" and st.session_state.page in ("home", "create", "gallery"):
        st.session_state.battle_origin = "home" if st.session_state.page == "create" else st.session_state.page
    st.session_state.pending_victory = None
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
    if is_defeated(task):
        return
    was_done = task["steps"][index]["done"]
    toggle_step(task, index)
    sequence = st.session_state.get("reward_sequence", 0) + 1
    st.session_state.reward_sequence = sequence
    st.session_state.effect = {
        "kind": "victory" if is_defeated(task) else ("undo" if was_done else "attack"), "task_id": task_id,
        "step_index": index, "sequence": sequence,
    }
    if is_defeated(task):
        st.session_state.pending_victory = task_id
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
effect = st.session_state.effect if isinstance(st.session_state.effect, dict) else None
with st.container(key="wallet_hud"):
    markup(f'<div class="topbar"><div class="brand">TASK MONSTER<small>SMALL STEPS. BIG WINS.</small></div><div class="hud-tools"><div class="gem-count" aria-label="Gem wallet" aria-live="polite"><span class="gem">{gem_svg()}</span><strong>{gem_balance(tasks)}</strong></div></div></div>')
if st.session_state.storage_error:
    st.warning(st.session_state.storage_error + " Session mode is active. The original save will not be overwritten.")

page = st.session_state.page

if page == "home":
    markup('<div class="page-heading"><h1>Quest board</h1><span>QUEST BOARD</span></div>')
    with st.container(key="hero_card"):
        markup(f'<div class="hero"><span class="hero-label">YOUR NEXT ADVENTURE</span><h2>Big quest?<br>Small steps.</h2><p>Break it down. Finish a step.<br>Land your next hit.</p><div class="hero-party"><span class="party-golem">{monster_svg("Work", "hero-golem")}</span><span class="party-ghost">{monster_svg("Creative", "hero-ghost")}</span><span class="party-slime">{monster_svg("Other", "hero-slime")}</span><span class="party-owl">{monster_svg("Study", "hero-owl")}</span><span class="party-plant">{monster_svg("Life", "hero-plant")}</span><span class="party-dragon">{monster_svg("Fitness", "hero")}</span></div></div>')
        if st.button("Summon a new quest", type="primary", use_container_width=True):
            navigate("create")
            st.rerun()
    markup(f'<div class="stats"><div class="stat"><strong>{len(active):02d}</strong><small>Active quests</small></div><div class="stat"><strong>{len(defeated):02d}</strong><small>Monsters defeated</small></div><div class="stat"><strong>{finished_steps:02d}</strong><small>Steps completed</small></div></div>')
    with st.container(key="active_quests_panel"):
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
    with st.container(key="create_steps_panel"):
        markup('<div class="section-line"><h2>Quest steps</h2><small>At least 2 · max. 24</small></div>')
        with st.form("add_step_form", clear_on_submit=True):
            with st.container(key="step_editor"):
                field, action = st.columns([3, 1], vertical_alignment="bottom")
                with field:
                    draft_title = st.text_input("Add a small step", placeholder="e.g. Read one page", max_chars=120)
                with action:
                    add = st.form_submit_button("Add step", use_container_width=True)
        if add:
            if not draft_title.strip():
                st.warning("A step cannot be empty. Add one small action you can take.")
            elif len(st.session_state.draft) >= 24:
                st.warning("A quest can have up to 24 steps. Try splitting it into two quests.")
            else:
                st.session_state.draft.append(draft_title.strip())
                st.rerun()
        step_count = len(st.session_state.draft)
        if step_count < 2:
            st.caption(f"Add {2-step_count} more step{'s' if step_count == 0 else ''} to unlock summoning.")
        else:
            if st.button("Summon monster", key="summon_button", type="primary", use_container_width=True):
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

            markup(f'<div class="summon-ready">{step_count} steps · Level {step_count} · {step_count * 100} HP</div>')

        for i, step in enumerate(st.session_state.draft):
            with st.container(key=f"step_draft_{i}"):
                text, remove = st.columns([5, 1], vertical_alignment="center")
                with text:
                    markup(f'<div class="step-line"><span class="step-number">{i+1:02d}</span><div class="step-copy">{esc(step)}</div></div>')
                with remove:
                    st.button("Remove step", key=f"remove_draft_{i}", help="Remove this step", on_click=drop_draft, args=(i,))

elif page in ("battle", "review"):
    task = next((t for t in tasks if t["id"] == st.session_state.selected), None)
    if task is None:
        navigate("home")
        st.rerun()
    reviewing = page == "review" or is_defeated(task)
    st.button("Back", key="back_to_quests", help="Return to the previous screen", on_click=navigate, args=("gallery" if page == "review" else st.session_state.get("battle_origin", "home"),))
    name = CATEGORIES[task["category"]][0]
    hp, maximum = health(task)
    victory = is_defeated(task)
    hit = effect["kind"] if effect else None
    markup(f'<div class="battle-title"><h1>{esc(task["title"])}</h1><span class="tag">Lv. {len(task["steps"]):02d}</span></div><div class="subcopy">{task["category"]} realm · {name}</div>')
    if not reviewing:
        markup(f'<div class="battle-hp"><div class="hp-label"><span>MONSTER HP</span><span>{hp} / {maximum}</span></div><div class="hp-track"><div class="hp-fill" style="width:{hp/maximum*100}%"></div></div></div>')
    if st.session_state.notice:
        markup(f'<div class="notice">{gem_svg()}<span>{esc(st.session_state.notice)}</span></div>')
        st.session_state.notice = None
    if reviewing:
        try:
            completed = datetime.fromisoformat(task.get("completed_at") or "").astimezone(ZoneInfo("Asia/Hong_Kong")).strftime("%d %b %Y · %H:%M HKT")
        except (ValueError, TypeError):
            completed = "Time unavailable for this older quest"
        markup(f'<div class="completion-date"><small>QUEST COMPLETED</small><strong>{esc(completed)}</strong></div>')
    floating = '<div class="damage">−100 HP<small>+10 gems</small></div>' if hit in ("attack", "victory") else ('<div class="damage">＋100 HP</div>' if hit == "undo" else '')
    markup(f'<div class="arena {"victory" if victory else ""} {"hurt" if hit in ("attack", "victory") else ""}">{floating}<div class="arena-monster">{monster_svg(task["category"],task["title"],1-hp/maximum,victory)}</div><div class="arena-note">{"QUEST COMPLETE · MONSTER COLLECTED" if victory else "Finish a real-world step, then strike below"}</div></div>')
    with st.container(key="battle_steps_panel"):
        markup(f'<div class="section-line"><h2>Your steps · {completed_count(task)}/{len(task["steps"])}</h2><small>{"A quest worth remembering" if reviewing else "Each step deals 100 damage"}</small></div>')
        for i, step in (enumerate(task["steps"]) if reviewing else ordered_steps(task)):
            with st.container(key=f"step_{task['id']}_{i}"):
                if reviewing:
                    markup(f'<div class="step-line done"><span class="step-number">{gem_svg()}</span><div class="step-copy">{esc(step["title"])}<small>Completed</small></div></div>')
                elif step["done"]:
                    text, undo = st.columns([4, 1], vertical_alignment="center")
                    with text:
                        markup(f'<div class="step-line done"><span class="step-number">{gem_svg()}</span><div class="step-copy">{esc(step["title"])}<small>Complete · 10 gems earned</small></div></div>')
                    with undo:
                        st.button("Undo", key=f"attack_{task['id']}_{i}", help="Undo this step and return its 10 gems", on_click=attack, args=(task["id"], i))
                else:
                    markup(f'<div class="step-line"><span class="step-number">{i+1:02d}</span><div class="step-copy">{esc(step["title"])}<small>−100 HP · +10 gems</small></div></div>')
                    st.button("Complete & strike!", key=f"attack_{task['id']}_{i}", type="primary", on_click=attack, args=(task["id"], i), use_container_width=True)
    if not reviewing:
        with st.expander("Quest options"):
            st.caption("Abandoning removes this quest and its progress. Other quests are kept.")
            confirmed = st.checkbox("I confirm I want to abandon this quest", key=f"confirm_{task['id']}")
            st.button("Abandon quest", key="abandon_button", disabled=not confirmed, on_click=abandon, args=(task["id"],))

elif page == "gallery":
    markup('<div class="page-heading"><h1>Collection</h1><span>MONSTER COLLECTION</span></div><div class="subcopy">Revisit the quests behind your victories.</div>')
    if not defeated:
        markup('<div class="empty-state"><div class="empty-icon">♜</div><h3>Your first trophy is out there</h3><p>Complete every step of a quest<br>to collect its monster card here.</p></div>')
        st.button("Back to quests", on_click=navigate, args=("home",), type="primary")
    with st.container(key="collection_grid"):
        for row in range(0, len(defeated), 3):
            columns = st.columns(3)
            for column, task in zip(columns, list(reversed(defeated))[row:row+3]):
                with column:
                    with st.container(key=f"trophy_card_{task['id']}"):
                        name, _, color, shade = CATEGORIES[task["category"]]
                        level = len(task["steps"])
                        stars = "".join(star_svg(i < min(level, 5)) for i in range(5))
                        markup(f'<div class="trophy" style="--trophy-color:{color};--trophy-shade:{shade}"><div class="trophy-header"><strong>{name}</strong></div><div class="trophy-art">{monster_svg(task["category"],task["title"],trophy=True)}</div><div class="trophy-stars" aria-label="Level {level}" title="Level {level}">{stars}</div><div class="task-title" title="{esc(task["title"])}">{esc(task["title"])}</div></div>')
                        st.button("View quest", key=f"trophy_{task['id']}", help="View this quest and its completed steps", on_click=navigate, args=("review", task["id"]), use_container_width=True)

markup('<div class="save-note">LOCAL SAVE · YOUR ADVENTURE, YOUR PACE</div>')
markup('<div class="nav-clearance" aria-hidden="true"></div>' if page not in ("battle", "review") else '<div class="page-end" aria-hidden="true"></div>')
if page in ("home", "create", "gallery"):
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

# Consume each reward once. This script animates presentation only; Python owns the balance.
if effect and effect["kind"] in ("attack", "victory"):
    event = {**effect, "gem": gem_svg()}
    with st.container(key="reward_animation"):
        reward_script = (ROOT / "assets" / "rewards.js").read_text()
        st.iframe("<script>const reward = " + json.dumps(event) + ";" + reward_script + "</script>", height=1)
st.session_state.effect = None

# The audio engine lives on the parent page so Streamlit reruns do not restart music.
with st.container(key="audio_engine"):
    sound_event = {"id": f"{effect['task_id']}:{effect['sequence']}", "kind": effect["kind"]} if effect else None
    audio_payload = "(() => {const soundEvent = " + json.dumps(sound_event) + ";" + (ROOT / "assets/audio.js").read_text() + "})();"
    # Execute in the main page realm, so handlers survive disposal of this iframe.
    st.iframe("<script>const node=window.parent.document.createElement('script');node.textContent=" + json.dumps(audio_payload) + ";window.parent.document.body.appendChild(node);node.remove();</script>", height=1)


def dismiss_victory():
    st.session_state.pending_victory = None
    navigate("home")


@st.dialog("Monster defeated!", on_dismiss=dismiss_victory)
def victory_dialog(task):
    markup(f'<div class="celebration-art">{monster_svg(task["category"], task["title"], trophy=True)}</div><div class="celebration-copy"><h2>You did it!</h2><p>You defeated {CATEGORIES[task["category"]][0]} by finishing<br>{esc(task["title"])}.</p><small>Your monster is waiting in Collection.</small></div>')
    if st.button("Back to quests", key="finish_celebration", type="primary", use_container_width=True):
        dismiss_victory()
        st.rerun()


pending = st.session_state.get("pending_victory")
if pending:
    completed_task = next((t for t in tasks if t["id"] == pending and is_defeated(t)), None)
    if completed_task:
        victory_dialog(completed_task)
