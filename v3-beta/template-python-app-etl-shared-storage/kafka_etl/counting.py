"""Step 2 logic: clean text -> word count file; and reading that file again."""
import csv
import re
from collections import Counter

# A word = a run of letters; the class includes the German umlauts and ß.
WORD = re.compile(r"[a-zäöüß]+")


def count_words(text: str) -> Counter:
    return Counter(WORD.findall(text.lower()))


def write_wordcount(counts: Counter, path: str) -> None:
    """One line per word, most frequent first: `word,count`."""
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["word", "count"])
        writer.writerows(counts.most_common())


def read_wordcount(path: str) -> list[tuple[str, int]]:
    with open(path, encoding="utf-8", newline="") as f:
        rows = csv.reader(f)
        next(rows)  # header
        return [(word, int(count)) for word, count in rows]
