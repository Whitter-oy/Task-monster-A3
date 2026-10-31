# Task Monster — App Directory

The full project overview, interaction guide, consistent screenshot gallery, limitations and credits are in the **[repository README](../README.md)**. The starting idea, classmate trial, design changes and AI-tool decisions are in **[PROCESS.md at the repository root](../PROCESS.md)**.

## Run from this directory

```bash
uv sync --locked
uv run --locked streamlit run app.py
```

Open the local URL printed by Streamlit, normally http://localhost:8501. Press Ctrl+C to stop. Python 3.13 is selected by `.python-version`; `pyproject.toml` and `uv.lock` document dependencies.

## Optional local verification

```bash
uv run --locked python -m unittest discover -s tests -v
```

With Node.js installed, `node --test tests/audio.test.cjs` runs the optional sound checks. There is no GitHub automatic-check workflow.

Personal progress is stored in `local_data/tasks.json`, which is ignored by Git. This is a single-user local prototype, not a shared hosted service. See the [main README](../README.md#mistakes-interruption-and-limitations) for error recovery and limitations.
