# template-wizard-service-streamlit

A repository for Spectra's **"Git Python service" wizard**: a small **Streamlit web app** that counts
the words of a text. It starts with a 5 KB excerpt of Franz Kafka's *Die Verwandlung* (a root asset) and lets you
paste your own text. It shows the number of words, the distinct words, the most frequent word, a bar chart of the
top words and a searchable table of all words.

## What the wizard does with the repository

You enter a repository and a service name; the wizard then does, in this order:

1. creates a **GitWatcher** for the repository (build on every push);
2. waits for fusion-forge to **build** the app into a venv pack in fusion-index;
3. **tags** that version (`stable`);
4. creates a **service template** (image, port, optional hostname) pointing at the artifact;
5. creates a **chain** with a deploy step for it;
6. creates a trigger and **fires it once**, so the service starts right away.

The app keeps running as a Deployment with a Service. When you push a new version and the `stable` tag moves,
the running pods are restarted with the new code. Rolling the wizard run back removes everything it created.

## The wizard form for this example

| Field | Value |
|---|---|
| Service name | `wizard-words` (lowercase letters, digits, hyphens) |
| Repository URL / branch | your git URL, `main` |
| Project directory | `v3-beta/template-wizard-service-streamlit` (empty if the repo root is this directory) |
| Port | `8501` (Streamlit's default; **must equal `runner.port` in `metadata.yaml`**) |
| Ingress name | optional DNS label, e.g. `words` → the app is reachable at `words.<cluster domain>`; empty = no hostname |

## How it differs from the job wizards

| | job wizards ([single](../template-wizard-job-single-entrypoint/README.md), [multi](../template-wizard-job-multi-entrypoint/README.md)) | this service wizard |
|---|---|---|
| Result | a job template; triggers start one-shot runs | a service template; a **Deployment** that keeps running |
| `runner.type` | `python` | `streamlit` |
| `runner.port` | none | `8501`, same as the form's port |
| Started | when you fire a trigger | **once automatically**, then it stays up |
| Entrypoints | a list, one trigger each | one: `ENTRYPOINT: main.py` in `metadata.yaml` |
| Token / external auth | optional (Job steps) | not available (a short-lived token would expire under a long-running service) |

## Root assets

`metadata.yaml` has `rootAssets: true`: the forge bundles **every non-`.py` file of the repository root** into the
package `_root_assets` inside the venv. That is `kafka_excerpt.txt` — and, because the rule has no include list, also
`README.md` and `README_technical.md`. Expected and harmless. `wordservice/excerpt.py` finds the file relative to the
package. (Alternative without the side effect: an `assets/` package,
see [`../template-python-app-assets-dir`](../template-python-app-assets-dir/README.md).)

## Rules

- `main.py`, `metadata.yaml` and `requirements.txt` are required in the project directory.
- `main.py` runs **again on every interaction**, so it only calls into the `wordservice` package (needs an `__init__.py`).
- `st.set_page_config(...)` must be the first Streamlit call of a run.
- Pin every dependency, `streamlit` included — it is what the runner starts.
- Bump `version` in `metadata.yaml` to publish a change; an existing version is not rebuilt.
- Keep the form's **port** and `runner.port` identical, otherwise the service forwards to the wrong port.
- `ingressName` is a **hostname**; `ingress.path` in `metadata.yaml` would be a URL **path**. They are independent; this template uses only the hostname.

## Contents

| File | Purpose |
|---|---|
| `metadata.yaml` | Build settings: `rootAssets: true`, runner `streamlit`, port 8501 |
| `requirements.txt` | Pinned dependencies (`streamlit`, `pandas`), rules as in [`../template-python-venv`](../template-python-venv/README.md) |
| `main.py` | Thin entrypoint |
| `wordservice/` | `excerpt.py` (root asset), `words.py` (counting), `ui.py` (the page) |
| `kafka_excerpt.txt` | The sample text, a root asset |
| `README_technical.md` | The same wizard run via kubectl, and how to open the app |

For a richer Streamlit example (banner, icons, CSS, charts) see [`../template-python-app-streamlit`](../template-python-app-streamlit/README.md).

## Source of the text

Excerpt from *Die Verwandlung* by Franz Kafka, Project Gutenberg eBook #22367
(<https://www.gutenberg.org/ebooks/22367>), public domain.

## How to use it as a template

1. Copy this directory, e.g. `cp -r template-wizard-service-streamlit my-service`.
2. Set your own `name`, `version`, `maintainer` in `metadata.yaml`.
3. Replace `wordservice/` and the excerpt with your own code and data.
4. Push, then run the wizard with your repository and the port from `metadata.yaml`.
