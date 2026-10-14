"""Entrypoint (metadata.yaml: runner.args.ENTRYPOINT = main.py).

Shows every way fusion can inject environment variables, secrets and tokens
into a job container, and prints which of them arrived. Values of secrets are
masked in the output - only their length is shown.

The explanation of each mechanism is in `injection/sources.py` (read its module
docstring first); the settings that switch them on are described in README.md.
A way that is not configured shows up as "<not set>" - that is not an error.
"""
from tabulate import tabulate

from injection import sources


def main() -> None:
    rows = []
    for way in sources.ALL_WAYS:
        rows.extend(way())

    # Everything printed goes to the job log.
    print(tabulate(rows, headers=["way", "name", "kind", "value"], tablefmt="simple"))

    # The recommended pattern for secrets in application code: file first,
    # env as fallback. Only the outcome is printed, never the key itself.
    api_key = sources.read_api_key()
    print(f"\nAPI key available to the app: {'yes' if api_key else 'no'}")


if __name__ == "__main__":
    main()
