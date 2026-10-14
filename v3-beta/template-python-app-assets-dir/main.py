"""Entrypoint (metadata.yaml: runner.args.ENTRYPOINT = main.py).

Kept deliberately thin: it only wires the pieces together. The logic lives in
the `wordstats` package; the input file lives in the `assets` package. fusion-forge
copies both into the venv automatically because they are top-level directories
containing an `__init__.py`.
"""
import os

# `assets` is a normal package from this repository (see assets/__init__.py),
# unlike `_root_assets` in template-python-app-root-asset, which the forge generates.
# Your IDE can resolve this import.
import assets

from wordstats import stats


def main() -> None:
    # Locate the asset next to the package's __init__.py.
    words_path = os.path.join(os.path.dirname(assets.__file__), "words.txt")
    with open(words_path, encoding="utf-8") as f:
        text = f.read()

    # Everything printed goes to the job log.
    print(stats.render_report(text))


if __name__ == "__main__":
    main()
