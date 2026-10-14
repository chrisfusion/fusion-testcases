# template-python-app-multi-entrypoint

One build, **several entrypoints, no `main.py`**. The artifact contains three small
scripts (`count.py`, `top.py`, `longest.py`) that share one package and one input
file; each chain step decides which script it runs. Same word-statistics idea as the
other app templates, now split into three jobs.

## How it differs from the single-entrypoint templates

| | `template-python-app-*` (others) | `template-python-app-multi-entrypoint` (this one) |
|---|---|---|
| Entrypoint | one fixed `main.py`, set in `metadata.yaml` (`runner.args.ENTRYPOINT`) | none fixed; every top-level `*.py` is one, chosen **per step** |
| `metadata.yaml` | no `files` key | `files: []` (auto-discover top-level scripts) |
| `runner.args.ENTRYPOINT` | set | **must not be set** (see below) |
| Shared code | optional | in a package (`wordstats/`), because scripts cannot import each other |
| Jobs per build | one | as many as you have scripts, all from one artifact |

## How it works

1. **Build:** with `files: []` the forge uploads every top-level `*.py` file (`count.py`, `top.py`, `longest.py`) as a loose file on the artifact version, next to the venv pack. Directories that are packages (`wordstats/`, `assets/`) go into the venv.
2. **Run:** every step uses the *same* artifact and sets the environment variable `ENTRYPOINT` to a script name. fusion-runner starts exactly that file inside the venv.
3. **Per-step settings:** a step can set more variables next to `ENTRYPOINT`. Here `top.py` reads `TOP_N` (default 5), so the same script can serve several steps with different values.

## Rules

- **No `main.py` needed**, but every script you want to run must be a *top-level* `.py` file. Scripts in sub-directories are not uploaded as entrypoints.
- **Scripts cannot import each other.** Only packages (directories with `__init__.py`) are installed into the venv. Put shared code into a package, like `wordstats/`.
- **Never set `runner.args.ENTRYPOINT` in `metadata.yaml`.** Everything under `runner.args` is applied after the step's own settings and wins, so one fixed `ENTRYPOINT` would silently override the choice of every step. `runner.type` alone is safe.
- **Choose files by hand if you prefer:** `files: [count.py, top.py]` uploads exactly those and fails fast if one is missing.
- **Assets** work as in [`template-python-app-assets-dir`](../template-python-app-assets-dir/README.md): `words.txt` lives in the `assets/` package. (`rootAssets` would also work, but would bundle the READMEs too.)
- Bump `version` in `metadata.yaml` to publish a change; an existing version is not rebuilt.

## Settings in Spectra

The build only provides the scripts; the chain decides what runs. For each step:

| Step | Job template | Environment overrides |
|---|---|---|
| `count` | one template with code source `app.template-python-app-multi-entrypoint`, tag `stable` | `ENTRYPOINT=count.py` |
| `top` | the same template | `ENTRYPOINT=top.py`, `TOP_N=3` |
| `longest` | the same template | `ENTRYPOINT=longest.py` |

The three steps have no dependencies, so they run in parallel. Add `dependsOn` to
order them. kubectl users find these settings as manifests in
[README_technical.md](README_technical.md#reference-manifests).

## Contents

| File | Purpose |
|---|---|
| `metadata.yaml` | App build settings: `files: []`, runner type, **no** fixed entrypoint |
| `requirements.txt` | Pinned dependencies (`tabulate`, `humanize`), rules as in [`../template-python-venv`](../template-python-venv/README.md) |
| `count.py`, `top.py`, `longest.py` | The three entrypoints, thin scripts |
| `wordstats/` | Shared code (`text.py`) used by all scripts |
| `assets/` | Package holding the input file `words.txt` |
| `README_technical.md` | Build, apply and test commands, reference manifests |

## How to use it as a template

1. Copy this directory, e.g. `cp -r template-python-app-multi-entrypoint my-app`.
2. Set your own `name`, `version`, `maintainer` in `metadata.yaml`.
3. Replace the three scripts with your own top-level scripts; keep shared code in a package with `__init__.py`.
4. Pin your dependencies, push, build through Spectra, then create one step per script with its `ENTRYPOINT`.
