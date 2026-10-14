"""The actual application logic, using the packages from requirements.txt."""
from collections import Counter

import humanize
from tabulate import tabulate


def render_report(text: str, top: int = 5) -> str:
    """Return a table of the most frequent words plus the text size."""
    words = [w.strip(".,:;!?").lower() for w in text.split()]
    counts = Counter(w for w in words if w).most_common(top)

    table = tabulate(counts, headers=["word", "count"], tablefmt="simple")
    size = humanize.naturalsize(len(text.encode("utf-8")))
    return f"{len(words)} words, {size}\n\n{table}"
