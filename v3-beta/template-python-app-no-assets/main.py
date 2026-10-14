"""Entrypoint (metadata.yaml: runner.args.ENTRYPOINT = main.py).

Kept deliberately thin: it only wires the pieces together. The logic lives in
the `wordstats` package, which fusion-forge copies into the venv automatically
because it is a top-level directory containing an `__init__.py`.

Unlike the other templates there is no input file: the text is hardcoded below,
so nothing besides code has to be shipped.
"""
from wordstats import stats

# Hardcoded input, replaces the words.txt asset of the other templates.
LOREM_IPSUM = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod "
    "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim "
    "veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea "
    "commodo consequat. Duis aute irure dolor in reprehenderit in voluptate "
    "velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint "
    "occaecat cupidatat non proident, sunt in culpa qui officia deserunt "
    "mollit anim id est laborum."
)


def main() -> None:
    # Everything printed goes to the job log.
    print(stats.render_report(LOREM_IPSUM))


if __name__ == "__main__":
    main()
