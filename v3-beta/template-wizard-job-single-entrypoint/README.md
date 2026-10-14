# template-wizard-job-single-entrypoint

The simplest repository for Spectra's **"Git Python job" wizard**: **one `main.py`**, a root
asset, and a short-lived token that the job reads **from a file**. The job prints a
word-frequency report on a 5 KB excerpt of Franz Kafka's *Die Verwandlung* and a few facts about
the token it received.

## What the wizard does with the repository

You enter a repository and a job name; the wizard then does, in this order:

1. creates a **GitWatcher** for the repository (build on every push);
2. waits for fusion-forge to **build** the app into a venv pack in fusion-index;
3. **tags** that version (`stable`);
4. creates a **job template** pointing at the artifact;
5. creates a **chain** with that template, including the optional external-auth identity;
6. creates **one trigger per entrypoint** you listed. Each trigger sets `ENTRYPOINT` for its runs.

Triggers are `OnDemand` (fire them yourself) or `Cron` (a schedule). Rolling the wizard run back
removes everything it created.

## The wizard form for this example

| Field | Value |
|---|---|
| Job name | `wizard-single` (lowercase letters, digits, hyphens) |
| Repository URL / branch | your git URL, `main` |
| Project directory | `v3-beta/template-wizard-job-single-entrypoint` (empty if the repo root is this directory) |
| Entrypoints | one entry: `main.py`, type `OnDemand` |
| External auth: mode / name | `serviceAccount` / an allowlisted ServiceAccount, e.g. `ext-auth-demo-sa` (leave both empty for no token) |

Mode and name are set together or not at all. The name must be on the cluster's allowlist; the
wizard offers only those names.

## Other wizards: the batch wizards

The same repository also works with the two **batch** wizards, because it has exactly one fixed entrypoint
(`runner.args.ENTRYPOINT: main.py`). They differ in how the job is started:

| Wizard | Creates | Starts | Form fields (besides repository and job name) |
|---|---|---|---|
| Git Python job (above) | one trigger per listed entrypoint | when you fire it, or on its cron | entrypoints, optional external auth |
| **Git batch job** (`batch-git-job`) | one trigger | **once immediately**, then on demand or by cron | trigger type `OnDemand` / `Cron`, schedule, optional external auth (chain level and per trigger) |
| **Git batch cron job** (`batchcron-git-job`) | one *BatchCron* trigger with a list of jobs | by the cron expression of each list entry | jobs list, optional external auth (chain level only) |

The batch wizards have no entrypoint field: the entrypoint is whatever `metadata.yaml` says, here `main.py`.
That is why a repository with several entrypoints needs the Git Python job wizard instead (see
[`../template-wizard-job-multi-entrypoint`](../template-wizard-job-multi-entrypoint/README.md)).
Token injection by file works the same in all three. Each BatchCron run also gets one `JOB_*` env var per field
of its list entry (`JOB_ID`, `JOB_NAME`, `JOB_TOPIC`, ...); this example does not print them.

## Token injection by file

With external auth set, the operator mints a **fresh, short-lived token for every job pod** and mounts
it as a file; the long-lived credential behind it never reaches your code.

- The path is in the env var **`WEAVE_EXTERNAL_AUTH_TOKEN_FILE`** (`/var/run/secrets/fusion-platform.io/external-auth/token`). `WEAVE_EXTERNAL_AUTH_MODE` and `WEAVE_EXTERNAL_AUTH_NAME` say which identity it is.
- `jobkit/token.py` reads **only the file**. The same token is normally also offered as env var `WEAVE_EXTERNAL_AUTH_TOKEN`, but the file is the variant that always exists, is not inherited by child processes and does not leak into crash dumps.
- The job prints the token's length, `iss`, `sub`, `aud` and time left — never the token.
- Without external auth in the form the job still runs and says `token: none injected`.
- Details and both variants side by side: [`../template-python-app-external-auth`](../template-python-app-external-auth/README.md).

## Root assets

`metadata.yaml` has `rootAssets: true`: the forge bundles **every non-`.py` file in the repository root** into
the package `_root_assets` inside the venv. That is `kafka_excerpt.txt` — and, because the rule has no include
list, also `README.md` and `README_technical.md`. This is expected and harmless. `jobkit/excerpt.py` finds
the file relative to the package. (Alternative without the side effect: an `assets/` package,
see [`../template-python-app-assets-dir`](../template-python-app-assets-dir/README.md).)

## Rules

- `main.py`, `metadata.yaml` and `requirements.txt` are required in the project directory.
- The entrypoint you list in the form must be a file the build uploaded: here `main.py`.
- `runner.args.ENTRYPOINT: main.py` in `metadata.yaml` and the wizard's `main.py` say the same thing, so they do not conflict. For several entrypoints see [`../template-wizard-job-multi-entrypoint`](../template-wizard-job-multi-entrypoint/README.md), where the metadata must **not** set one.
- Code in sub-directories needs an `__init__.py`.
- Bump `version` in `metadata.yaml` to publish a change; an existing version is not rebuilt.

## Contents

| File | Purpose |
|---|---|
| `metadata.yaml` | Build settings: `rootAssets: true`, runner `python`, `ENTRYPOINT: main.py` |
| `requirements.txt` | Pinned dependencies (`tabulate`, `humanize`), rules as in [`../template-python-venv`](../template-python-venv/README.md) |
| `main.py` | Thin entrypoint |
| `jobkit/` | `excerpt.py` (root asset), `token.py` (token by file), `report.py` (the work) |
| `kafka_excerpt.txt` | The input: the first ~4.8 KB of *Die Verwandlung*, a root asset |
| `README_technical.md` | The same wizard run via kubectl, and how to check the result |

## Source of the text

Excerpt from *Die Verwandlung* by Franz Kafka, Project Gutenberg eBook #22367
(<https://www.gutenberg.org/ebooks/22367>), public domain.

## How to use it as a template

1. Copy this directory, e.g. `cp -r template-wizard-job-single-entrypoint my-job`.
2. Set your own `name`, `version`, `maintainer` in `metadata.yaml`.
3. Replace `jobkit/` and the excerpt with your own code and data.
4. Push, then run the wizard with your repository and `main.py` as the entrypoint.
