"""Process 1 of 3 (ENTRYPOINT=extract.py): read the raw ebook, clean it, save it to shared storage.

No internet access: the ebook is an asset of the artifact (assets/die_verwandlung.txt).
Output: /weave-shared/clean.txt - read by the next step.
"""
from kafka_etl import cleaning, paths


def main() -> None:
    with open(paths.RAW_FILE, encoding="utf-8") as f:
        raw = f.read()

    cleaned = cleaning.clean(raw)

    with open(paths.CLEAN_FILE, "w", encoding="utf-8") as f:
        f.write(cleaned)

    print(f"extract: {len(raw)} chars raw -> {len(cleaned)} chars clean, written to {paths.CLEAN_FILE}")


if __name__ == "__main__":
    main()
