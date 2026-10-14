"""Shared logic of the three entrypoints."""
import os

# Synthetic package created by fusion-forge because of `rootAssets: true`. It holds
# every non-.py file of the repository root (here: kafka_excerpt.txt). It only
# exists inside the built venv, so an IDE may flag this import.
import _root_assets


def load_excerpt() -> str:
    path = os.path.join(os.path.dirname(_root_assets.__file__), "kafka_excerpt.txt")
    with open(path, encoding="utf-8") as f:
        return f.read()


def split_words(text: str) -> list[str]:
    """Lower-cased words without surrounding punctuation."""
    words = [w.strip(".,:;!?\"'()»«-").lower() for w in text.split()]
    return [w for w in words if w]
