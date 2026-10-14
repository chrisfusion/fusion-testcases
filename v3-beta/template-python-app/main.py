"""Entrypoint (metadata.yaml: runner.args.ENTRYPOINT = main.py).

Kept deliberately thin: it only wires the pieces together. The logic lives in
the `wordstats` package, which fusion-forge copies into the venv automatically
because it is a top-level directory containing an `__init__.py`.
"""
import os

# Synthetic package created by fusion-forge because of `rootAssets: true`.
# It contains every non-.py file from the repository root (here: words.txt).
# It only exists inside the built venv, so your IDE may flag this import.
import _root_assets

from wordstats import stats


def main() -> None:
    # Locate the asset next to the synthetic package's __init__.py.
    words_path = os.path.join(os.path.dirname(_root_assets.__file__), "words.txt")
    with open(words_path, encoding="utf-8") as f:
        text = f.read()

    # Everything printed goes to the job log.
    print(stats.render_report(text))


if __name__ == "__main__":
    main()
