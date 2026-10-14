# template-wizard-job-multi-entrypoint

The second repository for Spectra's **"Git Python job" wizard**: **three entrypoints and no
`main.py`**, with the input as a root asset. Each entrypoint becomes its own trigger.

| Entrypoint | Does |
|---|---|
| `count.py` | number of words, distinct words and size of the excerpt |
| `top.py` | the five most frequent words |
| `longest.py` | the three longest words |

The input is a 5 KB excerpt of Franz Kafka's *Die Verwandlung* (`kafka_excerpt.txt`).

## What the wizard does with the repository

1. creates a **GitWatcher** (build on every push);
2. waits for the **build** into a venv pack in fusion-index;
3. **tags** it (`stable`);
4. creates one **job template** and one **chain** for the whole artifact;
5. creates **one trigger per entry** of the entrypoints list. Each trigger sets `ENTRYPOINT` to its file name, so the same artifact runs a different script per trigger.

Every entry has its own type: `OnDemand` or `Cron` with a schedule — mixing them is fine.

## The wizard form for this example

| Field | Value |
|---|---|
| Job name | `wizard-multi` |
| Repository URL / branch | your git URL, `main` |
| Project directory | `v3-beta/template-wizard-job-multi-entrypoint` |
| Entrypoints | `count.py` OnDemand, `top.py` OnDemand, `longest.py` OnDemand (or Cron with a schedule) |
| External auth | not used here (see [`../template-wizard-job-single-entrypoint`](../template-wizard-job-single-entrypoint/README.md)) |

## Rules for several entrypoints

- **No `main.py`** is needed, but every script you list must be a **top-level** `.py` file.
- **`metadata.yaml` needs `files: []`** (auto-discover every top-level `*.py`). Without it the forge expects exactly one `main.py`. To pick files by hand: `files: [count.py, top.py]`.
- **Never set `runner.args.ENTRYPOINT`** in `metadata.yaml`. It is applied after the trigger's setting and wins, so every trigger would run the same script. `runner.type: python` alone is safe.
- **Scripts cannot import each other.** Only packages (with `__init__.py`) are installed into the venv. Shared code lives in `jobkit/`.
- The wizard sets nothing but `ENTRYPOINT` per trigger; any other setting must come from the job template or defaults (`TOP_N` here defaults to 5).

## Root assets

`rootAssets: true` bundles **every non-`.py` file of the repository root** into the package `_root_assets`:
`kafka_excerpt.txt` and — there is no include list — the READMEs too. Expected and harmless. Root `.py` files
are not assets; they stay the entrypoints. `jobkit/text.py` finds the excerpt relative to the package.

## Contents

| File | Purpose |
|---|---|
| `metadata.yaml` | `files: []`, `rootAssets: true`, runner `python`, **no** fixed entrypoint |
| `requirements.txt` | Pinned dependencies (`tabulate`, `humanize`), rules as in [`../template-python-venv`](../template-python-venv/README.md) |
| `count.py`, `top.py`, `longest.py` | The three entrypoints, thin scripts |
| `jobkit/` | Shared code (`text.py`) |
| `kafka_excerpt.txt` | The input, a root asset |
| `README_technical.md` | The same wizard run via kubectl |

## Source of the text

Excerpt from *Die Verwandlung* by Franz Kafka, Project Gutenberg eBook #22367
(<https://www.gutenberg.org/ebooks/22367>), public domain.

## How to use it as a template

1. Copy this directory, e.g. `cp -r template-wizard-job-multi-entrypoint my-jobs`.
2. Set your own `name`, `version`, `maintainer` in `metadata.yaml`.
3. Replace the scripts and `jobkit/`; keep `__init__.py` in each package and `files: []`.
4. Push, then run the wizard and list your scripts as entrypoints.
