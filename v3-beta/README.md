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
| [`template-python-app-inject-variables/`](template-python-app-inject-variables/) | The eight ways fusion injects env vars, secrets and tokens (file or env) into a job; Spectra settings plus reference manifests. |
| [`template-python-app-external-auth/`](template-python-app-external-auth/) | Only `externalAuthRef`: a short-lived operator-minted token, read from file (preferred) or env var (second option). |
| [`template-python-app-multi-entrypoint/`](template-python-app-multi-entrypoint/) | Three entrypoints from one build, no `main.py` (`files: []`); each chain step picks its script via `ENTRYPOINT`. Shared code and an assets package. |
| [`template-python-app-streamlit/`](template-python-app-streamlit/) | A Streamlit web app (Deploy step): the word-count example as charts, with banner picture, favicon, SVG icons and CSS from an `assets/` package. |
| [`template-python-app-etl-shared-storage/`](template-python-app-etl-shared-storage/) | One build, three processes: extract → count (jobs) → Streamlit dashboard, linked by the chain's shared storage. Data: Kafka's *Die Verwandlung* (shipped as asset, no internet needed). |

More templates (app builds, git builds, chains, triggers) will be added step by step.
