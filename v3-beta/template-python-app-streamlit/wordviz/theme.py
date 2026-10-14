"""Everything that comes from the `assets` package: picture, icons, css, input text.

The assets are ordinary files inside an ordinary package (see assets/__init__.py).
fusion-forge copies the whole directory into the venv, so they are found relative
to the package - never relative to the working directory, which differs at runtime.
"""
import base64
import os

import assets
import streamlit as st

ASSETS_DIR = os.path.dirname(assets.__file__)


def path(*parts: str) -> str:
    """Absolute path of a file in the assets package, e.g. path("icons", "words.svg")."""
    return os.path.join(ASSETS_DIR, *parts)


def read_text(*parts: str) -> str:
    with open(path(*parts), encoding="utf-8") as f:
        return f.read()


def apply_css() -> None:
    """Inject assets/style.css into the page."""
    st.markdown(f"<style>{read_text('style.css')}</style>", unsafe_allow_html=True)


def icon_data_uri(name: str) -> str:
    """An SVG icon as data: URI, so it can be used in an <img> tag of our own HTML
    (streamlit does not serve arbitrary files from the venv)."""
    encoded = base64.b64encode(read_text("icons", f"{name}.svg").encode()).decode()
    return f"data:image/svg+xml;base64,{encoded}"


def metric_card(icon: str, value: str, label: str) -> str:
    """HTML of one metric card; styled by .metric-card in assets/style.css."""
    return (
        '<div class="metric-card">'
        f'<img src="{icon_data_uri(icon)}" alt="">'
        f'<div><div class="value">{value}</div><div class="label">{label}</div></div>'
        "</div>"
    )
