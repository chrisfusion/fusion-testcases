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
| [`template-python-app-root-asset/`](template-python-app-root-asset/) | Single generic Python app via the GitOps app build: `metadata.yaml`, pinned `requirements.txt`, a thin `main.py`, code in a sub-package, and a root text file shipped as an asset (`rootAssets`). |
| [`template-python-app-assets-dir/`](template-python-app-assets-dir/) | Same app as `template-python-app-root-asset`, but the input file lives in an own `assets/` package and `rootAssets` is false. Explains the difference and when to prefer which. |
| [`template-python-app-no-assets/`](template-python-app-no-assets/) | Same app with no data files at all: the input text is hardcoded in `main.py`. Includes a comparison of all three app templates. |

More templates (app builds, git builds, chains, triggers) will be added step by step.
