# template-python-app-root-asset

A single, generic Python application built by the fusion-forge **GitOps builder**:
you point the forge at a git repository (or a sub-directory of one), and it builds
the code and its dependencies into a venv pack and uploads it to fusion-index as
`app.<name>`.

The example is a tiny one-shot program: it reads a text file and prints the most
frequent words as a table. The logic is nothing special — the point is the layout.

## Contents

| File | Purpose |
|---|---|
| `metadata.yaml` | Tells the forge name, version, Python version, how to start the app, and to ship the text file |
| `requirements.txt` | Pinned dependencies (`tabulate`, `humanize`) — same rules as in [`../template-python-venv`](../template-python-venv/README.md) |
| `main.py` | Entrypoint; thin, only wires things together |
| `wordstats/` | The application code as a small package (`__init__.py` + `stats.py`) |
| `words.txt` | Input file, shipped as an **asset** |
| `README_technical.md` | API/curl/GitWatcher details |

## What the forge does with it

1. Reads `metadata.yaml` (name, version, builder image, runner).
2. Builds a Python 3.12 venv from `requirements.txt`.
3. Copies every top-level directory that is a Python package (here `wordstats/`) into the venv.
4. Because of `rootAssets: true`, bundles the non-`.py` files from the repo root (here `words.txt`) into a package called `_root_assets`.
5. Uploads the venv pack, `main.py` and `metadata.yaml` to fusion-index as `app.template-python-app-root-asset`, version `0.1.0`.

## Layout rules

- **`main.py`, `metadata.yaml` and `requirements.txt` are required** in the repository root (or the configured sub-directory).
- **Code in sub-directories** must be an importable package, i.e. contain an `__init__.py`. Anything else is not importable at runtime.
- **Assets in the root** (any non-`.py` file) are only shipped with `rootAssets: true`. Read them via the `_root_assets` package, as `main.py` shows. `requirements.txt`, `metadata.yaml` and dotfiles are never treated as assets.
- **Every non-`.py` root file is bundled**, not only your data files. In this template the forge reports `copied 3 root asset file(s)`: `words.txt` plus `README.md` and `README_technical.md`. This is expected and harmless; the READMEs just travel along inside `_root_assets`. Keep only files you are happy to ship in the repo root, or use a sub-directory package for the rest.
- **Assets in a sub-directory** need no flag: put them in a package directory (with `__init__.py`) and locate them relative to the package's `__file__`.
- **Versions:** the same version is not rebuilt. Bump `version` in `metadata.yaml` to publish a change.
- **No port, no ingress:** `runner.type: python` runs the entrypoint once. For a web app use a web runner type (see the Streamlit examples).

## How to use it as a template

1. Copy this directory, e.g. `cp -r template-python-app-root-asset my-app`.
2. In `metadata.yaml` set your own `name`, `version`, `maintainer`.
3. Replace `wordstats/` with your own package(s) and edit `main.py`; keep `__init__.py` in every package.
4. Replace `words.txt` with your own asset files, or remove them together with `rootAssets: true`.
5. Pin your dependencies in `requirements.txt`.
6. Push to git and let the forge build it from the repository (and sub-directory) in Spectra.
   With a GitWatcher the build runs automatically on every push.

No data files at all? See [`../template-python-app-no-assets`](../template-python-app-no-assets/README.md). Prefer to ship data files without the root-asset side effects? See [`../template-python-app-assets-dir`](../template-python-app-assets-dir/README.md), the same app with an `assets/` package.

For the API view see [README_technical.md](README_technical.md).
