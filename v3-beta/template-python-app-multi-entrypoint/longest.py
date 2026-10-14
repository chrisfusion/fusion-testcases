"""Entrypoint 3 of 3 - selected with ENTRYPOINT=longest.py."""
from wordstats import text


def main() -> None:
    distinct = sorted(set(text.split_words(text.load_text())), key=lambda w: (-len(w), w))
    print("longest words: " + ", ".join(distinct[:3]))


if __name__ == "__main__":
    main()
