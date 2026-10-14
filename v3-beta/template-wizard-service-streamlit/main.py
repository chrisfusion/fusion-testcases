"""Entrypoint (metadata.yaml: runner.args.ENTRYPOINT = main.py).

`streamlit run main.py` executes this file again on every user interaction, so it
stays thin: the work is in the `wordservice` package, which fusion-forge copies into
the venv because it is a top-level directory containing an `__init__.py`.
"""
from wordservice import ui

ui.render()
