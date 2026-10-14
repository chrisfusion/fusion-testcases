"""The word-count logic, free of any streamlit code (easy to test on its own)."""
from collections import Counter

import pandas as pd

# A tiny stopword list so the chart shows more than "the" and "is".
STOPWORDS = {"the", "is", "a", "an", "in", "of", "and", "to", "it", "by", "are", "be", "with"}


def split_words(text: str) -> list[str]:
    """Lower-cased words without surrounding punctuation."""
    words = [w.strip(".,:;!?\"'()").lower() for w in text.split()]
    return [w for w in words if w]


def top_words(words: list[str], top_n: int, drop_stopwords: bool) -> pd.DataFrame:
    """Most frequent words as a DataFrame (index: word, column: count), ready for a chart."""
    if drop_stopwords:
        words = [w for w in words if w not in STOPWORDS]
    counts = Counter(words).most_common(top_n)
    return pd.DataFrame(counts, columns=["word", "count"]).set_index("word")


def length_distribution(words: list[str]) -> pd.DataFrame:
    """How many words have 1, 2, 3, ... letters."""
    counts = Counter(len(w) for w in words)
    return pd.DataFrame(sorted(counts.items()), columns=["letters", "words"]).set_index("letters")
