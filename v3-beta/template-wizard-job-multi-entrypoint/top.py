"""Entrypoint 2 of 3 - the wizard runs it as `ENTRYPOINT=top.py`.

The wizard only sets ENTRYPOINT per trigger, so there is no per-entrypoint setting
beyond the file name; TOP_N is optional and defaults to 5.
"""
import os
from collections import Counter

from tabulate import tabulate

from jobkit import text


def main() -> None:
    top_n = int(os.environ.get("TOP_N", "5"))
    counts = Counter(text.split_words(text.load_excerpt())).most_common(top_n)
    print(f"top {top_n} words")
    print(tabulate(counts, headers=["word", "count"], tablefmt="simple"))


if __name__ == "__main__":
    main()
