# Assignment 3 — Task Monster

一个面向学生的游戏化任务清单：把大任务拆成小步骤，完成一步就降低怪兽血量，全部完成后驯服怪兽。

## 运行第一阶段原型

需要安装 uv。在仓库根目录运行：

```bash
cd task-monster
uv sync --locked
uv run streamlit run app.py
```

打开终端显示的本地网址，通常是 http://localhost:8501。按 Ctrl+C 停止服务。

## 项目文件

- [使用方法、限制和来源](task-monster/README.md)
- [开发过程与 AI 使用记录](task-monster/PROCESS.md)
- [Python 源代码](task-monster/app.py)
- [依赖声明](task-monster/pyproject.toml) 和 [锁定版本](task-monster/uv.lock)

## 当前状态

第一阶段核心互动已完成：创建任务、添加或删除步骤、完成或撤销、更新血量、通关、确认重置。
进度仅保留在当前会话，尚未实现磁盘保存。
真实用户试用和截图仍待完成；当前版本不是最终提交版。

## 开发记录

从当前原型开始保留真实 Git 提交。后续每次完成并验证一个有意义的修改后提交，在 GitHub 连接可用时推送。
过程文档记录重要设计决定、验证结果与真实用户试用，不回填虚构的开发阶段或观察。
