# template-python-app-inject-variables

How to get **configuration, secrets and tokens into your code** when it runs in
fusion. The app is a small report job: it checks every injection mechanism and
prints which values arrived, with secret values masked (only their length is shown).
It is built like the other app templates — generic app build via the GitOps forge —
the new part is `injection/sources.py` (the explanation, in code) and the settings
that switch each mechanism on (see "Settings in Spectra").

## The eight ways

**Environment variables** — for non-secret configuration:

| # | Where it is configured | What arrives in the code |
|---|---|---|
| 1 | `metadata.yaml` → `runner.args` | plain env var (here `GREETING`), baked into the artifact |
| 2 | job template → `env` | static env var, or taken from a Secret/ConfigMap key (`valueFrom`) |
| 3 | chain step → `envOverrides` | same as 2, but per step; one template can serve many steps |
| 4 | automatic with `codeSource` | `WEAVE_ARTIFACT`, `WEAVE_TAG`, `WEAVE_VERSION`, … |
| 5 | automatic from a BatchCron trigger | `JOB_ID`, `JOB_NAME`, `JOB_SCHEDULE`, … |

**Secrets and tokens** — as a file, as an env var, or both:

| # | Where it is configured | File | Env var |
|---|---|---|---|
| 6 | chain → `authSecretRef` (a whole Secret) | one file per key in the directory `$WEAVE_AUTH_SECRET_DIR` — **always** | one env var per key — only while the env injector is on |
| 7 | chain → `externalAuthRef` (short-lived token minted by the operator, Job steps only) | path in `$WEAVE_EXTERNAL_AUTH_TOKEN_FILE` — **always** | `WEAVE_EXTERNAL_AUTH_TOKEN` — only while the env injector is on |
| 8 | job template → `volumes` (any Secret/ConfigMap) | files at a mount path you choose (here `/etc/app-secrets`) | – |

Way 7 also sets `WEAVE_EXTERNAL_AUTH_MODE` and `WEAVE_EXTERNAL_AUTH_NAME`. With
`externalAuthRef` the long-lived credential behind the token (ServiceAccount rights
or Keycloak client secret) never reaches your container, only the token.

## Settings in Spectra

The app alone gets nothing injected; the job template and chain that run it do:

| Way | Setting |
|---|---|
| 1 | `runner.args` in `metadata.yaml` (this directory) |
| 2 | job template → environment variables (static, or from a Secret/ConfigMap key) |
| 3 | chain step → environment overrides |
| 4, 5 | nothing to set: automatic with a code source / a BatchCron trigger |
| 6 | chain → auth secret (name of an existing Secret) |
| 7 | chain → external auth (mode + allowlisted name), see [`../template-python-app-external-auth`](../template-python-app-external-auth/README.md) |
| 8 | job template → volumes (Secret or ConfigMap + mount path; here `/etc/app-secrets`) |
| 6, 7 | chain → environment injector (`unsafeEnvironmentInjector`): on = file and env, off = file only |

kubectl users find all of it as manifests in [README_technical.md](README_technical.md#reference-manifests).

## File or env var?

- **Prefer files for secrets.** An env var is inherited by every child process, shows up in crash dumps and debug output, and is easy to log by accident. A file is read exactly where it is needed.
- **The file mounts are always on.** The env variants of ways 6 and 7 belong to the *environment injector* (`unsafeEnvironmentInjector`, default **on**). Set it to `false` on the chain (a trigger or a run can override it) and only the files remain.
- **So write code file-first, env as fallback** — it then works in both setups. `read_api_key()` in `injection/sources.py` shows the pattern.
- **Never print secrets.** This template only prints their length.

## Which value wins?

If the same name is set in several places, the container gets all of them and the **last one wins**. The order is: job template `env` → step `envOverrides` → `runner.args` / `codeSource` variables. So a `runner.args` key (way 1) can never be overridden by a step: only put values there that are meant to be fixed with the artifact.

## Contents

| File | Purpose |
|---|---|
| `metadata.yaml` | App build settings; `runner.args.GREETING` shows way 1 |
| `requirements.txt` | Pinned dependency (`tabulate`), rules as in [`../template-python-venv`](../template-python-venv/README.md) |
| `main.py` | Thin entrypoint: runs all checks and prints the table |
| `injection/sources.py` | One function per way, with the explanation in docstrings |
| `README_technical.md` | Build, apply and test commands |

The forge uses `main.py`, `metadata.yaml`, `requirements.txt` and the `injection/` package. For the build itself see
[`../template-python-app-no-assets`](../template-python-app-no-assets/README.md).

## How to use it as a template

1. Copy this directory, e.g. `cp -r template-python-app-inject-variables my-app`.
2. Set your own `name`, `version`, `maintainer` in `metadata.yaml`.
3. Keep the ways you need (and the matching functions in `sources.py`), delete the rest.
4. Read the values in your own code: env via `os.environ`, secrets via files as shown in `read_api_key()`.
5. Build through Spectra / the GitOps builder, then create the Secrets and apply the chain.

Not every way has to be configured: an unused way simply shows `<not set>` in the report.

For the commands see [README_technical.md](README_technical.md).
