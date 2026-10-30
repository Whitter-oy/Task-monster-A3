import html
import os
from pathlib import Path

import streamlit as st

from art import monster_svg
from game import CATEGORIES, category_for, completed_count, create_task, health, is_defeated, load_tasks, save_tasks, toggle_step

ROOT = Path(__file__).resolve().parent
DATA_FILE = Path(os.environ.get("TASK_MONSTER_DATA_FILE", ROOT / "local_data" / "tasks.json"))
st.set_page_config(page_title="Task Monster · 任务冒险", page_icon="⚔️", layout="centered", initial_sidebar_state="collapsed")
st.markdown(f"<style>{(ROOT / 'assets' / 'game.css').read_text()}</style>", unsafe_allow_html=True)

if "tasks" not in st.session_state:
    tasks, error = load_tasks(DATA_FILE)
    st.session_state.update(tasks=tasks, page="home", selected=None, draft=[], storage_error=error, notice=None, effect=None)


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
        st.session_state.storage_error = "无法写入本机存档。当前会话仍可使用，请检查文件夹写入权限。"


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
active = [t for t in tasks if not is_defeated(t)]
defeated = [t for t in tasks if is_defeated(t)]
finished_steps = sum(completed_count(t) for t in tasks)
markup(f'<div class="topbar"><div class="brand">TASK MONSTER<small>把待办，变成一场冒险</small></div><div class="gem-count"><span class="gem">◆</span> {finished_steps * 10} <span style="font-size:9px;color:#a89aba">XP</span></div></div>')
if st.session_state.storage_error:
    st.warning(st.session_state.storage_error + " 本次先使用会话模式，不覆盖原存档。")
if st.session_state.notice:
    st.success(st.session_state.notice)
    st.session_state.notice = None

page = st.session_state.page

if page == "home":
    markup('<div class="page-heading"><h1>冒险大厅</h1><span>QUEST BOARD</span></div><div class="subcopy">每一件小事，都是值得挑战的怪兽。</div>')
    markup(f'<div class="hero"><span class="hero-label">YOUR NEXT ADVENTURE</span><h2>大任务？<br>一招一招来。</h2><p>拆成小步骤，完成就出击。<br>今天也为自己赢下一场。</p><div class="hero-art">{monster_svg("其他", "hero")}</div></div>')
    if st.button("＋  召唤新的任务怪兽", type="primary", use_container_width=True):
        navigate("create")
        st.rerun()
    markup(f'<div class="stats"><div class="stat"><strong>{len(active):02d}</strong><small>正在挑战</small></div><div class="stat"><strong>{len(defeated):02d}</strong><small>已击败怪兽</small></div><div class="stat"><strong>{finished_steps:02d}</strong><small>完成的小步骤</small></div></div>')
    markup(f'<div class="section-line"><h2>⚔  进行中的挑战</h2><small>{len(active)} 个任务</small></div>')
    if not active:
        markup('<div class="empty-state"><div class="empty-icon">✧</div><h3>你的下一场冒险，等你命名</h3><p>创建一个真实任务，写下几个小步骤。<br>你的第一只专属怪兽就会出现。</p></div>')
    for task in active:
        name, _, color, shade = CATEGORIES[task["category"]]
        hp, maximum = health(task)
        ratio = hp / maximum
        with st.container(key=f"quest_{task['id']}"):
            markup(f'<div class="quest-banner" style="--accent:{color};--shade:{shade}"><span class="tag">{esc(task["category"])} / {name}</span><span class="level">Lv. {len(task["steps"]):02d}</span><h3>{esc(task["title"])}</h3><div class="monster-mini">{monster_svg(task["category"],task["title"],1-ratio)}</div><div class="hp-line"><div class="hp-track"><div class="hp-fill" style="width:{ratio*100}%"></div></div><div class="hp-label"><span>HP {hp} / {maximum}</span><span>{completed_count(task)}/{len(task["steps"])} 步</span></div></div></div>')
            st.button("进入战斗  →", key=f"enter_{task['id']}", on_click=navigate, args=("battle", task["id"]), use_container_width=True)

elif page == "create":
    markup('<div class="page-heading"><h1>召唤任务怪兽</h1><span>NEW QUEST</span></div><div class="subcopy">给任务一个名字，再把它拆成可以开始的小事。</div>')
    title = st.text_input("任务名称", key="new_title", placeholder="例如：完成 A3 作品", max_chars=60)
    category = st.selectbox("任务类型", ["自动识别"] + list(CATEGORIES), key="new_category")
    chosen = category_for(title.strip()) if category == "自动识别" else category
    name, _, color, shade = CATEGORIES[chosen]
    level = len(st.session_state.draft)
    markup(f'<div class="quest-banner" style="--accent:{color};--shade:{shade}"><span class="tag">怪兽预览 · {chosen}</span><span class="level">Lv. {level:02d}</span><h3>{name}</h3><div class="species">每个步骤 = 1 级 · 100 HP<br>步骤越多，挑战等级越高</div><div class="monster-mini">{monster_svg(chosen,title)}</div></div>')
    markup('<div class="section-line"><h2>挑战步骤</h2><small>建议 3–5 步 · 最多 24 步</small></div>')
    with st.form("add_step_form", clear_on_submit=True):
        draft_title = st.text_input("添加一个小步骤", placeholder="例如：画出三个页面的草图", max_chars=120)
        add = st.form_submit_button("＋ 添加步骤", use_container_width=True)
    if add:
        if not draft_title.strip():
            st.warning("步骤不能为空，先写下一件可以执行的小事。")
        elif len(st.session_state.draft) >= 24:
            st.warning("一个任务最多 24 步，试着拆成两个任务吧。")
        else:
            st.session_state.draft.append(draft_title.strip())
            st.rerun()
    for i, step in enumerate(st.session_state.draft):
        with st.container(key=f"step_draft_{i}"):
            markup(f'<div class="step-line"><span class="step-number">{i+1:02d}</span><div class="step-copy">{esc(step)}</div></div>')
            st.button("移除步骤", key=f"remove_draft_{i}", on_click=drop_draft, args=(i,))
    if st.button("⚔  召唤怪兽，开始挑战", type="primary", use_container_width=True):
        try:
            task = create_task(title, st.session_state.draft, category)
        except ValueError as error:
            st.warning(str(error))
        else:
            tasks.append(task)
            persist()
            st.session_state.draft = []
            st.session_state.notice = f"{task['title']} 的任务怪兽已出现！"
            navigate("battle", task["id"])
            st.rerun()

elif page == "battle":
    task = next((t for t in tasks if t["id"] == st.session_state.selected), None)
    if task is None:
        navigate("home")
        st.rerun()
    st.button("‹  返回任务大厅", on_click=navigate, args=("home",))
    name = CATEGORIES[task["category"]][0]
    hp, maximum = health(task)
    victory = is_defeated(task)
    effect = st.session_state.effect
    markup(f'<div class="battle-title"><h1>{esc(task["title"])}</h1><span class="tag">Lv. {len(task["steps"]):02d}</span></div><div class="subcopy">{task["category"]}领域 · {name}</div>')
    markup(f'<div class="battle-hp"><div class="hp-label"><span>MONSTER HP</span><span>{hp} / {maximum}</span></div><div class="hp-track"><div class="hp-fill" style="width:{hp/maximum*100}%"></div></div></div>')
    floating = '<div class="damage">−100 HP</div>' if effect == "attack" else ('<div class="damage">＋100 HP</div>' if effect == "undo" else '')
    markup(f'<div class="arena {"victory" if victory else ""} {"hurt" if effect == "attack" else ""}">{floating}<div class="arena-monster">{monster_svg(task["category"],task["title"],1-hp/maximum,victory)}</div><div class="arena-note">{"QUEST COMPLETE · 怪兽已收录" if victory else "完成现实中的步骤，再点击下方出击"}</div></div>')
    if victory:
        markup('<div class="victory-banner"><strong>✦ 挑战胜利 ✦</strong><small>你做到了！这只怪兽已加入战利品图鉴。</small></div>')
        st.button("▣  查看战利品图鉴", type="primary", on_click=navigate, args=("gallery",))
    markup(f'<div class="section-line"><h2>你的行动 · {completed_count(task)}/{len(task["steps"])}</h2><small>每一步造成 100 点伤害</small></div>')
    for i, step in enumerate(task["steps"]):
        with st.container(key=f"step_{task['id']}_{i}"):
            markup(f'<div class="step-line {"done" if step["done"] else ""}"><span class="step-number">{"✓" if step["done"] else f"{i+1:02d}"}</span><div class="step-copy">{esc(step["title"])}<small>{"已完成 · 可撤销误操作" if step["done"] else "完成后出击 · −100 HP"}</small></div></div>')
            st.button("撤销完成" if step["done"] else "⚔  完成这一步，出击！", key=f"attack_{task['id']}_{i}", type="secondary" if step["done"] else "primary", on_click=attack, args=(task["id"], i), use_container_width=True)
    with st.expander("任务管理"):
        st.caption("放弃会移除这个任务和它的进度，其他任务不受影响。")
        confirmed = st.checkbox("确认放弃这个任务", key=f"confirm_{task['id']}")
        st.button("放弃并移除", disabled=not confirmed, on_click=abandon, args=(task["id"],))

elif page == "gallery":
    markup('<div class="page-heading"><h1>战利品图鉴</h1><span>MONSTER COLLECTION</span></div><div class="subcopy">它们曾经看起来很难。现在，都是你的战绩。</div>')
    markup(f'<div class="collection-intro"><span class="medal">✹</span><div><strong>{len(defeated):02d} 只怪兽已击败</strong><small>每一张卡牌，都是你完成的一个真实任务。</small></div></div>')
    if not defeated:
        markup('<div class="empty-state"><div class="empty-icon">♜</div><h3>第一份战利品，还在前方</h3><p>完成一个任务的所有步骤，<br>就能在这里收藏它的怪兽卡牌。</p></div>')
        st.button("⚔  回到任务大厅", on_click=navigate, args=("home",), type="primary")
    for row in range(0, len(defeated), 2):
        columns = st.columns(2)
        for column, task in zip(columns, list(reversed(defeated))[row:row+2]):
            with column:
                name = CATEGORIES[task["category"]][0]
                markup(f'<div class="trophy"><span class="tag">Lv. {len(task["steps"]):02d} · {task["category"]}</span>{monster_svg(task["category"],task["title"],trophy=True)}<strong>{name}</strong><div class="task-title">{esc(task["title"])}</div><div class="stars">✦ ✦ ✦</div><div class="trophy-foot">DEFEATED · {len(task["steps"])} 步全部完成</div></div>')
                st.button("查看战绩", key=f"trophy_{task['id']}", on_click=navigate, args=("battle", task["id"]))

markup('<div class="save-note">LOCAL SAVE · 进度保存在本机 · 按自己的节奏冒险</div>')
with st.container(key="bottom_nav"):
    for column, (label, target) in zip(st.columns(3), [("⚔  任务大厅", "home"), ("＋  召唤怪兽", "create"), ("▣  战利品", "gallery")]):
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
