"""Entrypoint 3 of 3 - the wizard runs it as `ENTRYPOINT=longest.py`."""
from jobkit import text


def main() -> None:
    distinct = sorted(set(text.split_words(text.load_excerpt())), key=lambda w: (-len(w), w))
    print("longest words: " + ", ".join(distinct[:3]))


if __name__ == "__main__":
    main()
