"""Shared logic used by all three entrypoints."""
import os

# `assets` is a normal package of this repository (assets/__init__.py); the forge
# copies it into the venv like any other directory, so the data file travels with it.
import assets


def load_text() -> str:
    """Read the input text shipped in the assets package."""
    path = os.path.join(os.path.dirname(assets.__file__), "words.txt")
    with open(path, encoding="utf-8") as f:
        return f.read()


def split_words(text: str) -> list[str]:
    """Lower-cased words without surrounding punctuation."""
    words = [w.strip(".,:;!?").lower() for w in text.split()]
    return [w for w in words if w]
