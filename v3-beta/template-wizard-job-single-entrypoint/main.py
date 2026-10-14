"""Entrypoint (metadata.yaml: runner.args.ENTRYPOINT = main.py; also listed in the wizard form).

Kept deliberately thin: the work is in the `jobkit` package, which fusion-forge copies
into the venv because it is a top-level directory containing an `__init__.py`.
"""
from jobkit import report


def main() -> None:
    # Everything printed goes to the job log.
    report.run()


if __name__ == "__main__":
    main()
