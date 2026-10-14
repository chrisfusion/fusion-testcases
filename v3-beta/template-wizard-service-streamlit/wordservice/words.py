"""The word counting, free of any streamlit code."""
from collections import Counter

import pandas as pd


def split_words(text: str) -> list[str]:
    """Lower-cased words without surrounding punctuation."""
    words = [w.strip(".,:;!?\"'()»«-").lower() for w in text.split()]
    return [w for w in words if w]


def count(text: str) -> pd.DataFrame:
    """Every word with its count, most frequent first (columns: word, count)."""
    counts = Counter(split_words(text))
    return pd.DataFrame(counts.most_common(), columns=["word", "count"])
