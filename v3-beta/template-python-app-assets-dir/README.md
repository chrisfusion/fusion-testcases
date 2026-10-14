# template-python-app-assets-dir

Same application as [`template-python-app-root-asset`](../template-python-app-root-asset/README.md) —
same `main.py` flow, same `wordstats/` code, same `words.txt` input, same
dependencies — but the input file is shipped as an **assets directory** instead
of a root asset.

## The difference to `template-python-app-root-asset`

| | `template-python-app-root-asset` | `template-python-app-assets-dir` (this one) |
|---|---|---|
| Where `words.txt` lives | repository root | `assets/words.txt` |
| `metadata.yaml` | `rootAssets: true` | `rootAssets: false` (also the default) |
| Package holding the file | `_root_assets`, **generated** by the forge (`import _root_assets`) | `assets`, **your own** package with an `__init__.py` (`import assets`) |
| What gets bundled | **every** non-`.py` root file, including the READMEs | only the contents of the directories you made packages |
| IDE / local run | `_root_assets` does not exist locally, import is flagged and needs simulating | `assets` is a normal package, runs and resolves locally |
| Package name | fixed by the operator (default `_root_assets`) | you choose it |

**Which one to use?** Prefer the assets directory: it is explicit, testable locally,
and ships nothing by accident. Use `rootAssets: true` only when files must sit in the
repo root, or you want to see the feature.

No data files at all? See [`../template-python-app-no-assets`](../template-python-app-no-assets/README.md).

## Contents

| File | Purpose |
|---|---|
| `metadata.yaml` | Name, version, Python version, how to start the app; `rootAssets: false` |
| `requirements.txt` | Pinned dependencies (`tabulate`, `humanize`), rules as in [`../template-python-venv`](../template-python-venv/README.md) |
| `main.py` | Thin entrypoint; reads the asset via the `assets` package |
| `wordstats/` | The application code as a small package |
| `assets/` | Package (`__init__.py`) holding the input file `words.txt` |
| `README_technical.md` | API/curl/GitWatcher details |

## What the forge does with it

1. Reads `metadata.yaml`, builds a Python 3.12 venv from `requirements.txt`.
2. Copies every top-level directory that is a Python package — here `wordstats/` and `assets/` — into the venv.
3. Uploads the venv pack, `main.py` and `metadata.yaml` to fusion-index as `app.template-python-app-assets-dir`, version `0.1.0`.

Root files like the READMEs are **not** bundled.

## Layout rules

- `main.py`, `metadata.yaml` and `requirements.txt` are required in the repo root (or configured sub-directory).
- Every directory you want shipped must contain an `__init__.py`; otherwise it is not importable.
- Locate data files relative to the package: `os.path.join(os.path.dirname(assets.__file__), "words.txt")`.
- Bump `version` in `metadata.yaml` to publish a change; an existing version is not rebuilt.

## How to use it as a template

1. Copy this directory, e.g. `cp -r template-python-app-assets-dir my-app`.
2. Set your own `name`, `version`, `maintainer` in `metadata.yaml`.
3. Replace `wordstats/` and the files in `assets/`; keep `__init__.py` in each package.
4. Pin your dependencies, push, and let the forge build it from Spectra.

For the API view see [README_technical.md](README_technical.md).
