"""Entrypoint 2 of 3 - selected with ENTRYPOINT=top.py.

Besides ENTRYPOINT a step can set further env vars of its own: TOP_N changes how
many words are listed. The same script can therefore serve several steps with
different settings.
"""
import os
from collections import Counter

from tabulate import tabulate

from wordstats import text


def main() -> None:
    top_n = int(os.environ.get("TOP_N", "5"))
    counts = Counter(text.split_words(text.load_text())).most_common(top_n)
    print(f"top {top_n} words")
    print(tabulate(counts, headers=["word", "count"], tablefmt="simple"))


if __name__ == "__main__":
    main()
