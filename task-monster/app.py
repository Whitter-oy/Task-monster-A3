import streamlit as st


st.set_page_config(page_title="任务怪兽 Task Monster", page_icon="👾")

# session_state keeps data when a widget causes Streamlit to rerun the script.
if "steps" not in st.session_state:
    st.session_state.steps = []
    st.session_state.task_name = ""
    st.session_state.started = False
    st.session_state.next_id = 0


def add_step(title):
    """Give each step a stable ID so deleting a step does not mix up buttons."""
    st.session_state.steps.append(
        {"id": st.session_state.next_id, "title": title, "done": False}
    )
    st.session_state.next_id += 1


def toggle_step(step_id):
    for step in st.session_state.steps:
        if step["id"] == step_id:
            step["done"] = not step["done"]
            break


def remove_step(step_id):
    st.session_state.steps = [
        step for step in st.session_state.steps if step["id"] != step_id
    ]


def reset_challenge():
    st.session_state.steps = []
    st.session_state.task_name = ""
    st.session_state.started = False
    st.session_state.next_id = 0
    st.session_state.pop("task_input", None)
    st.session_state.pop("confirm_reset", None)


st.title("👾 任务怪兽 Task Monster")
st.write("把一个大任务拆成小步骤。每完成一步，就离驯服怪兽更近一点。")
st.caption("第一阶段原型 · 进度仅保留在当前会话，刷新或关闭后可能丢失。")

if not st.session_state.started:
    st.header("1. 准备挑战")
    task_name = st.text_input(
        "你想完成什么？", placeholder="例如：完成 A3 的互动原型", key="task_input"
    )

    with st.form("add_step_form", clear_on_submit=True):
        step_title = st.text_input(
            "添加一个具体的小步骤", placeholder="例如：画出主界面草图"
        )
        submitted = st.form_submit_button("添加步骤")

    if submitted:
        if step_title.strip():
            add_step(step_title.strip())
            st.success("步骤已添加。你可以继续添加，或开始挑战。")
        else:
            st.warning("步骤不能为空，请写下一件可以执行的小事。")

    st.subheader("你的步骤")
    if not st.session_state.steps:
        st.info("先添加至少一个步骤。建议拆成 3–5 步，每一步都容易开始。")

    for index, step in enumerate(st.session_state.steps, start=1):
        label, action = st.columns([4, 1])
        label.write(f"{index}. {step['title']}")
        action.button(
            "删除", key=f"delete_{step['id']}",
            on_click=remove_step, args=(step["id"],),
        )

    if st.button("开始挑战", type="primary"):
        if not task_name.strip():
            st.warning("请先填写任务名称。")
        elif not st.session_state.steps:
            st.warning("请先添加至少一个步骤。")
        else:
            st.session_state.task_name = task_name.strip()
            st.session_state.started = True
            st.rerun()

else:
    st.header(st.session_state.task_name)
    steps = st.session_state.steps
    completed = sum(1 for step in steps if step["done"])
    progress = completed / len(steps)
    monster_hp = round(100 * (1 - progress))

    if completed == len(steps):
        st.subheader("😊 怪兽已被驯服！")
        st.success("挑战完成！下面保留了你完成的步骤。误点了也可以撤销。")
    elif completed == 0:
        st.subheader("👾 怪兽精神十足")
        st.info("从一个小步骤开始。完成现实中的步骤后，再点击对应按钮。")
    else:
        st.subheader("😵 怪兽开始疲惫了")
        st.info(f"已经完成 {completed} 步，继续按自己的节奏前进。")

    st.metric("怪兽血量", f"{monster_hp} / 100")
    st.progress(progress, text=f"任务进度：已完成 {completed}/{len(steps)} 步")
    st.subheader("2. 完成你的小步骤")

    for step in steps:
        label, action = st.columns([4, 1])
        label.write(f"{'✅' if step['done'] else '⬜'} {step['title']}")
        action.button(
            "撤销" if step["done"] else "完成",
            key=f"toggle_{step['id']}",
            on_click=toggle_step, args=(step["id"],),
        )

    st.divider()
    confirmed = st.checkbox("我确认清空当前挑战，重新开始", key="confirm_reset")
    st.button("重新开始", disabled=not confirmed, on_click=reset_challenge)
