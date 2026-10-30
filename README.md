# Task Monster — 把待办变成一场冒险

给觉得大任务难以开始的学生使用的游戏化任务工具。创建任务并拆成小步骤，每完成一步就攻击怪兽，全部完成后将怪兽收入战利品图鉴。

## 手机游戏界面

深色冒险大厅、原创怪兽、任务卡牌与底部导航，桌面浏览器也保持约 460px 的手机页面宽度。

<img src="task-monster/assets/screenshots/home.jpg" width="220" alt="任务大厅" /> <img src="task-monster/assets/screenshots/battle.jpg" width="220" alt="怪兽战斗" /> <img src="task-monster/assets/screenshots/gallery.jpg" width="220" alt="战利品图鉴" />

截图来自独立演示存档，任务与完成情况仅用于展示，不代表实际用户试用。

## 运行

需要 Python 3.13 和 uv。在仓库根目录打开终端：

```bash
cd task-monster
uv sync --locked
uv run streamlit run app.py
```

打开终端显示的本地网址，通常是 http://localhost:8501。按 Ctrl+C 停止服务。若已启动旧版，先停止再运行上述最后一行，然后刷新浏览器。

## 主互动

1. 在“召唤怪兽”中输入任务名称，选择类型或让程序按关键词自动识别。
2. 逐一添加并确认步骤。一个步骤对应一级、100 HP；创建前可以移除步骤。
3. 大厅可同时显示多个进行中的任务，点击对应的“进入战斗”。
4. 完成现实中的步骤后点击“出击”：扣除 100 HP、更新进度，并显示受伤反馈。误操作可以撤销。
5. 所有步骤完成后收录到图鉴；查看战绩时仍可撤销，撤销后会移回进行中列表。

## 代码与过程

- [详细使用方法与限制](task-monster/README.md)
- [开发过程、AI 使用和试用待办](task-monster/PROCESS.md)
- [界面](task-monster/app.py)、[任务与存档逻辑](task-monster/game.py)、[原创怪兽绘制](task-monster/art.py)
- [依赖声明](task-monster/pyproject.toml) 与 [锁定版本](task-monster/uv.lock)

## 存档与限制

任务自动保存至本机 `task-monster/local_data/tasks.json`，已加入 Git 忽略规则，不上传真实任务。刷新后可继续使用。
这是单人本地原型，没有账号或云同步；同一个服务上的不同浏览器共享本机存档，请避免同时编辑。不要直接作为多人在线服务部署。
自动识别使用本地关键词与确定性规则，无 AI API。六种怪兽具有按任务名称变化的装饰，同类任务可能拥有相似外形。
每步伤害相同，不判断真实任务是否完成；XP 由已完成步骤计算，撤销也会回退。

## 本地验证（可选）

在 task-monster 目录运行：

```bash
uv run --locked python -m unittest discover -s tests -v
```

没有 GitHub 自动检查工作流。程序测试不代替真实用户试用或老师评分。

## Credits 与提交进度

Python 和 Streamlit 概念参考 SD5913 课堂。怪兽由原创 SVG 代码绘制，系统字体和符号用于界面；用户提供的手机游戏截图仅作为风格参考，未复制其中角色或素材。使用 Codex 辅助编程与设计，决定与修改记录见 PROCESS。
真实用户试用仍待进行。Git 历史保留每次实际修改；截图、程序验证不算用户试用。
