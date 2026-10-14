"""Entrypoint 1 of 3 - selected with ENTRYPOINT=count.py.

There is no main.py: each top-level script is a separate entrypoint of the same
artifact. The job picks one through the ENTRYPOINT environment variable (set per
chain step, see README.md); fusion-runner then executes exactly this file.

Stays thin on purpose - the logic is in the shared `wordstats` package.
"""
import humanize

from wordstats import text


def main() -> None:
    content = text.load_text()
    words = text.split_words(content)
    size = humanize.naturalsize(len(content.encode("utf-8")))
    print(f"count: {len(words)} words, {len(set(words))} distinct, {size}")


if __name__ == "__main__":
    main()
