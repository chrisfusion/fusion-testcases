# testcases_v2

Successor to the top-level `streamlit-demo*` / `simple_streamlit_template` fixtures.
Same two build shapes fusion-forge understands, kept side by side, organized by shape
instead of by demo name. The old top-level directories are untouched — treat them as
frozen/legacy.

Each example here is consumed by fusion-forge (`../fusion-forge`) and, where noted,
deployed by a preseeded example chain in fusion-weave's Helm "showroom"
(`fusion-flux/deployment/fusion-weave/templates/showroom/`, `showroom.codeSourceApps.*`).

## app-builds/

Shape expected by `POST /api/v1/appbuilds` and `GitWatcher.spec.buildType: app`:
repo root (or `projectDir`) must contain `metadata.yaml`, `requirements.txt`, `main.py`.
Any other top-level directory is copied as-is into the venv's `site-packages` — must be
an importable package (needs `__init__.py`).

| Example | Demonstrates | Consumed by |
|---|---|---|
| `streamlit-showcase/` | Standard web app build: `runner.type: streamlit`, a port, an ingress `pathPrefix`. Long-running service → deployed as a `Deploy`-kind step. | `showroom.codeSourceApps.streamlitShowcase` (`codesource-streamlit.yaml`) — artifact `app.streamlit-showcase` |
| `batch-report-generator/` | Non-web app build: no `runner.port`, no `ingress` block — a one-shot script that reads `/weave-input/input.json` if present, writes a JSON report, and prints the result as the last stdout line (`producesOutput` capture rule). Meant for a `Job`-kind step, not `Deploy`. | `showroom.codeSourceApps.batchReport` (`codesource-batch.yaml`) — artifact `app.batch-report-generator` |
| `batch-metadata-reader/` | Non-web app build, same shape as `batch-report-generator/`. Reads and prints two metadata sources reaching the container: its own fusion-index artifact metadata (`WEAVE_*` env vars, from `codeSource`) and, when the run was created by a `BatchCron` trigger, that job's scheduling metadata (`JOB_*` env vars). The combined "codeSource step fired by a BatchCron schedule" scenario. | `showroom.codeSourceApps.batchMetadata` (`codesource-batchcron.yaml`) — artifact `app.batch-metadata-reader` |

## venv-builds/

Shape expected by `POST /api/v1/venvs`: just a `requirements.txt` — no `metadata.yaml`,
no `pyproject.toml`. Produces a `venv.{name}` artifact in fusion-index with no
metadata.yaml, so `codeSource` never injects `runner.args`-derived env vars for it.
This is the fit for a flat repo of interchangeable scripts sharing one
`requirements.txt`, run as separate steps of the same `WeaveChain`, each
selecting its own script via a per-step `ENTRYPOINT` env override rather than
via a fixed `runner.args.ENTRYPOINT` baked into metadata (which would collide
with — and silently win over — any per-step override, see `chain.yaml` for why).

| Example | Demonstrates | Consumed by |
|---|---|---|
| `etl-pipeline/` | 5 flat scripts (`extract.py`, `transform_customers.py`, `transform_orders.py`, `merge.py`, `load.py`) sharing one `requirements.txt`, reused by one `WeaveJobTemplate` across a 5-step chain (`extract` → parallel `transform_customers`/`transform_orders` → `merge` → `load`), each step picking its script via `envOverrides: [{name: ENTRYPOINT, value: ...}]`. Scripts only read `WEAVE_*` env vars — no real ETL logic. | Not wired into the Helm showroom; `chain.yaml` next to the scripts is a plain kubectl-applyable manifest (`WeaveJobTemplate` + `WeaveChain` + `WeaveTrigger`), publish steps documented as comments at the top. |

## git-builds/

Shape expected by `POST /api/v1/gitbuilds` and `GitWatcher.spec.buildType: git`:
a `pyproject.toml` with `[project]` name/version at the repo root (or `projectDir`),
built with `pip wheel` (no `--no-deps`, so `[build-system]` deps are fetched).

| Example | Demonstrates |
|---|---|
| `metrics-lib/` | Plain importable library package (`src/metrics_lib/`), no console entry point — the base pip-installable-library shape. |
| `onepackage-cli/` | Self-contained entry point via `[project.scripts]` — installs a runnable CLI command, not just an import target. |
| `monorepo-widget/` | `GitWatcher.spec.projectDir` / `CIBuild.spec.gitSource.projectDir`: the buildable package (`services/widget-lib/`) is nested under unrelated top-level repo content, exercising the monorepo-subdirectory path. |

## Publishing these to fusion-index

There's no code-changed automation for this — build and publish out-of-band, either:

- **Manual, one-off**: `POST /api/v1/venvs` (multipart) for venv-builds,
  `POST /api/v1/gitbuilds` (JSON) for git-builds, or `POST /api/v1/appbuilds` (JSON)
  for app-builds, against your fusion-forge deployment. venv-builds additionally need
  each flat script uploaded as an extra file via `POST /api/v1/artifacts/{id}/versions/{version}/files`
  against fusion-index directly — see `venv-builds/etl-pipeline/chain.yaml`.
- **Automatic, on every push**: apply a `GitWatcher` CR — see
  `../fusion-forge/config/samples/gitwatcher_private_repo.yaml` (git-build,
  `tokenSecretRef` private-repo auth demo, watches `metrics-lib/`) and
  `../fusion-forge/config/samples/gitwatcher_app_autobuild.yaml` (app-build,
  watches `streamlit-showcase/`). Both set `projectDir` to the relevant subfolder
  of this repo.

`showroom.codeSourceApps.*` in fusion-weave assumes `app.streamlit-showcase`,
`app.batch-report-generator`, and `app.batch-metadata-reader` already exist in
fusion-index under tag `stable` — publish them first, then enable that Helm flag.
