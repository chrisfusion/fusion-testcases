# template-python-app-external-auth

How a job gets a **short-lived access token** from fusion without ever seeing the
long-lived credential behind it. This is the focused version of way 7 from
[`template-python-app-inject-variables`](../template-python-app-inject-variables/README.md).

The app is a small report job: it finds the injected token, tells you whether it
came from the file or the env var, decodes who it is for and when it expires, and
shows the `Authorization` header it would send. The token itself is never printed —
only its length. Built like the other app templates (generic app build via the GitOps forge).

## What `externalAuthRef` does

On the chain you name an identity:

```yaml
externalAuthRef:
  mode: serviceAccount     # or: oidc
  name: ext-auth-demo-sa   # must be on the operator's allowlist
```

For every job pod of a Job-kind step the operator then **mints a fresh token** and hands it over:

| Mode | Token is | Behind it (never in your container) |
|---|---|---|
| `serviceAccount` | Kubernetes ServiceAccount token (JWT, audience `fusion` by default) | rights of the named ServiceAccount |
| `oidc` | Keycloak access token (JWT) | client id/secret of the named Secret |

A retry of a failed job gets a new token. Deploy-kind steps are not supported.

## Two ways to receive it

| | How | When it exists |
|---|---|---|
| **File** (preferred) | path in `$WEAVE_EXTERNAL_AUTH_TOKEN_FILE` (`/var/run/secrets/fusion-platform.io/external-auth/token`) | always |
| **Env var** (second option) | `$WEAVE_EXTERNAL_AUTH_TOKEN` | only while the chain's `unsafeEnvironmentInjector` is `true` (default) |

Also set, not secret: `WEAVE_EXTERNAL_AUTH_MODE` and `WEAVE_EXTERNAL_AUTH_NAME`.

**Why file first?** An env var is inherited by child processes and appears in crash
dumps and debug output. A file is read exactly where it is needed — and it is the only
variant left once you set `unsafeEnvironmentInjector: false`. Keep the env var only for
legacy code that cannot read files. `extauth/token.py` implements the pattern
(`read_token()`: file first, env as fallback) and `main.py` shows both side by side.

## Settings in Spectra

The app alone gets no token. The chain (or job) that runs it needs:

| Setting | Value in this example |
|---|---|
| External auth → mode | `serviceAccount` (or `oidc`) |
| External auth → name | an allowlisted identity, here `ext-auth-demo-sa` |
| Environment injector (`unsafeEnvironmentInjector`) | on = token as file **and** env var; off = file only |
| Step type | Job (Deploy steps are not supported) |
| Code source | artifact `app.template-python-app-external-auth`, tag `stable` |

kubectl users find the same settings as manifests in [README_technical.md](README_technical.md#reference-manifests).

## Prerequisites (done by the maintainer, once per cluster)

The chain is only valid if the identity is allowlisted and exists:

- **serviceAccount:** the name is listed in Helm `externalAuth.serviceAccounts` and the ServiceAccount exists in the namespace.
- **oidc:** the name is a Secret listed in Helm `externalAuth.oidcSecrets`, with the keys `clientId`, `clientSecret`, `tokenURL`.
- The operator never creates or manages these. A GUI can list the allowed names from `GET /api/v1/external-auth/options`.

## Lifetime

`serviceAccount` tokens live as long as the job's `activeDeadlineSeconds` (if set on the
template), otherwise Helm `externalAuth.defaultTokenTTL` (default 5 minutes). Kubernetes
enforces a minimum of 10 minutes, so shorter values are raised to that. For `oidc` the
Keycloak client's own access-token lifespan applies. Read the token when you need it;
do not store it beyond the job.

## Contents

| File | Purpose |
|---|---|
| `metadata.yaml` | App build settings (name, version, runner) |
| `requirements.txt` | Pinned dependencies (`tabulate`, `humanize`), rules as in [`../template-python-venv`](../template-python-venv/README.md) |
| `main.py` | Thin entrypoint: reports file vs. env, claims and expiry |
| `extauth/token.py` | Reading and describing the token; the explanation in docstrings |
| `README_technical.md` | Build, apply and test commands |

Everything in this directory is used by the build. For the build itself see
[`../template-python-app-no-assets`](../template-python-app-no-assets/README.md).

## How to use it as a template

1. Copy this directory, e.g. `cp -r template-python-app-external-auth my-app`.
2. Set your own `name`, `version`, `maintainer` in `metadata.yaml`.
3. When you create the chain (Spectra), set the settings listed under "Settings in Spectra" below.
4. In your code call `read_token()` and send `auth_header(token)` to the service the token was minted for. That service verifies the signature; do not trust the decoded claims yourself.

For the commands see [README_technical.md](README_technical.md).
