# v3-beta

Commented, copy-and-adapt examples for using fusion (forge, weave, index).
Successor to `../testcases_v2/`, organized as **templates** rather than test fixtures.

## Conventions

- Every example lives in its own directory named `template-<example>`
  (e.g. `template-python-job`).
- Every template has **two layers of explanation**:
  1. a `README.md` in the template directory (what it shows and the rules, written for Spectra GUI users),
     plus a `README_technical.md` with the curl/API commands and internals,
  2. in-code comments in every file (why each line is there).
- Templates are meant to be copied and modified — keep them minimal.

## Templates

| Template | Demonstrates |
|---|---|
| [`template-python-venv/`](template-python-venv/) | Simplest build: only a pinned `requirements.txt`. The forge builds a Python 3.12 venv from it and uploads it to fusion-index as `venv.<name>`. Explains the forge's requirements rules. |

More templates (app builds, git builds, chains, triggers) will be added step by step.
