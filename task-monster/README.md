# Task Monster — App Directory

See the [main product README](../README.md) for the introduction, screenshots, design decisions and usage guide.

## Run from this directory

```bash
uv sync --locked
uv run --locked streamlit run app.py
```

Open the local URL printed by Streamlit, normally http://localhost:8501. Press Ctrl+C to stop. Python 3.13 is selected by `.python-version`; dependencies are documented in `pyproject.toml` and `uv.lock`.

Personal progress is stored in the Git-ignored `local_data/tasks.json` file.
