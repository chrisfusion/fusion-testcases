"""Entrypoint 1 of 3 - the wizard runs it as `ENTRYPOINT=count.py`.

There is no main.py: every top-level script is an entrypoint of the same artifact.
In the wizard form each one is an entry of the `entrypoints` list and gets its own
trigger. Stays thin - the logic is in the shared `jobkit` package.
"""
import humanize

from jobkit import text


def main() -> None:
    content = text.load_excerpt()
    words = text.split_words(content)
    print(f"count: {len(words)} words, {len(set(words))} distinct, {humanize.naturalsize(len(content.encode()))}")


if __name__ == "__main__":
    main()
