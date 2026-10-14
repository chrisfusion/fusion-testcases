"""The bundled sample text: a root asset."""
import os

# Synthetic package created by fusion-forge because of `rootAssets: true`. It holds
# every non-.py file of the repository root (here: kafka_excerpt.txt). It only
# exists inside the built venv, so an IDE may flag this import.
import _root_assets


def load() -> str:
    path = os.path.join(os.path.dirname(_root_assets.__file__), "kafka_excerpt.txt")
    with open(path, encoding="utf-8") as f:
        return f.read()
