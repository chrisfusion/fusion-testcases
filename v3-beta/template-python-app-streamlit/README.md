# template-python-app-streamlit

A **Streamlit web app** built by the fusion-forge GitOps builder: the word-count example
of the other templates as an interactive page, with a banner picture, custom icons, a
CSS file and charts. Where the other app templates run once and exit (Job step), this
one is a long-running web service (Deploy step).

## What the app shows

- A banner picture and page icon from the assets.
- Three metric cards (words, distinct words, text size) with our own SVG icons, styled by `style.css`.
- Tabs with a bar chart of the most frequent words, the distribution of word lengths and the text itself.
- A sidebar to choose the text (the bundled sample or your own), the number of words in the chart, and whether common words are hidden.

## Assets: picture, icons, CSS, text

Everything the page needs lives in the `assets/` **package** (a directory with an `__init__.py`).
The forge copies the whole directory into the venv — files, sub-directory `icons/` and all — so no
flag is needed (compare [`template-python-app-assets-dir`](../template-python-app-assets-dir/README.md)).

| File | Used for |
|---|---|
| `assets/banner.png` | the picture at the top (`st.image`) |
| `assets/favicon.png` | the browser tab icon (`st.set_page_config(page_icon=...)`) |
| `assets/icons/*.svg` | the icons in the metric cards (embedded in our own HTML) |
| `assets/style.css` | the card styling, injected with `st.markdown("<style>…")` |
| `assets/words.txt` | the sample text |

Rules of thumb (all shown in `wordviz/theme.py`):

- **Find assets relative to the package** (`os.path.dirname(assets.__file__)`), never relative to the working directory.
- **Streamlit does not serve files from the venv.** Hand pictures to `st.image(path)`, and embed icons as data URIs in your HTML — a plain `<img src="assets/…">` would 404.
- **Icons without files:** Streamlit has built-in Material icons (`:material/bar_chart:`), used here for the tab labels and the info box. Use your own SVGs only when you need a specific look.

## Layout rules

- `main.py`, `metadata.yaml` and `requirements.txt` are required in the repo root (or configured sub-directory).
- `main.py` runs **again on every interaction**, so it only calls into the `wordviz` package (the code, with `__init__.py`).
- `st.set_page_config(...)` must be the first Streamlit call of a run.
- Pin every dependency, `streamlit` included — it is what the runner starts.
- Bump `version` in `metadata.yaml` to publish a change; an existing version is not rebuilt.

## What differs from the batch templates

| | batch templates | this template |
|---|---|---|
| `runner.type` | `python` | `streamlit` |
| `runner.port` | none | `8501`, must match the service's port |
| Step kind | Job (runs once) | **Deploy** (keeps running, restarted on a new version) |
| Reachable via | log output | a Service, optionally an Ingress under its own hostname |
| `ingress.path` | – | optional URL path segment; not set here, the app lives at `/` |

## Settings in Spectra

The build only provides the app; a **Deploy** step runs it:

| Setting | Value in this example |
|---|---|
| Step kind | Deploy |
| Code source | artifact `app.template-python-app-streamlit`, tag `stable` |
| Port | `8501` (same as `runner.port`) |
| Readiness probe | HTTP GET `/_stcore/health` on port 8501 |
| Resources | request 200m CPU / 500Mi, limit 500m CPU / 1Gi (as in `metadata.yaml`) |
| Ingress (optional) | one rule; its **name** becomes the hostname `<name>.<cluster domain>` |

kubectl users find the same settings as manifests in
[README_technical.md](README_technical.md#reference-manifests).

## Contents

| File | Purpose |
|---|---|
| `metadata.yaml` | App build settings: streamlit runner, port, resources |
| `requirements.txt` | Pinned dependencies (`streamlit`, `pandas`), rules as in [`../template-python-venv`](../template-python-venv/README.md) |
| `main.py` | Thin entrypoint |
| `wordviz/` | `theme.py` (loads assets), `data.py` (word counting), `ui.py` (the page) |
| `assets/` | Banner, favicon, SVG icons, CSS, sample text |
| `README_technical.md` | Build, deploy and test commands, reference manifests |

## How to use it as a template

1. Copy this directory, e.g. `cp -r template-python-app-streamlit my-dashboard`.
2. Set your own `name`, `version`, `maintainer` in `metadata.yaml`.
3. Replace `wordviz/` and the files in `assets/`; keep `__init__.py` in each package.
4. Pin your dependencies, push, build through Spectra, then create the Deploy step.
