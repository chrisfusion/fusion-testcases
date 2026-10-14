"""Process 2 of 3 (ENTRYPOINT=count.py): read the clean text from shared storage, count the words.

Input:  /weave-shared/clean.txt     (written by extract.py)
Output: /weave-shared/wordcount.csv (every word with its count) - read by the dashboard.
"""
from kafka_etl import counting, paths


def main() -> None:
    with open(paths.CLEAN_FILE, encoding="utf-8") as f:
        text = f.read()

    counts = counting.count_words(text)
    counting.write_wordcount(counts, paths.WORDCOUNT_FILE)

    print(f"count: {sum(counts.values())} words, {len(counts)} distinct, written to {paths.WORDCOUNT_FILE}")
    print("top 5:", counts.most_common(5))


if __name__ == "__main__":
    main()
