# weaveapp-gitops

A git repository layout for **WeaveApps applied by Flux**: commit a file, the app runs; delete the file, the app
and everything it created are gone. One `WeaveApp` per file, nothing else: no templates, chains, triggers or runs.

## What is in here

| File | App | Shows |
|---|---|---|
| [`apps/image-site.yaml`](apps/image-site.yaml) | `image-site` | A plain image (`nginx:1.27`) as a service with a hostname. No build. |
| [`apps/image-job.yaml`](apps/image-job.yaml) | `image-job` | A plain image (`busybox`) as a job: one scheduled entrypoint, one on-demand. |
| [`apps/python-job-single.yaml`](apps/python-job-single.yaml) | `python-job-single` | Python job from a forge build ([`template-wizard-job-single-entrypoint`](../template-wizard-job-single-entrypoint/)), with a short-lived token. |
| [`apps/python-job-multi.yaml`](apps/python-job-multi.yaml) | `python-job-multi` | Three entrypoints from one build ([`template-wizard-job-multi-entrypoint`](../template-wizard-job-multi-entrypoint/)). |
| [`apps/streamlit.yaml`](apps/streamlit.yaml) | `streamlit` | Streamlit from a forge build ([`template-wizard-service-streamlit`](../template-wizard-service-streamlit/)), plain. |
| [`streamlit-nginx/`](streamlit-nginx/streamlit-nginx.yaml) | `streamlit-nginx` | The same Streamlit tuned for **ingress-nginx**: login, forwarded headers, timeouts, upload limit, sticky sessions. |
| [`streamlit-traefik/`](streamlit-traefik/streamlit-traefik.yaml) | `streamlit-traefik` | The same tuning for **Traefik**. |
| [`platform/`](platform/) | — | What the **platform team** sets up once; not applied from this repo. |

Use **one** of the two tuned Streamlit folders per cluster — the one matching the cluster's ingress controller. The
top-level [`kustomization.yaml`](kustomization.yaml) applies `apps/` plus `streamlit-nginx/`.

## Rules

- **Only WeaveApps.** Flux applies this repo as the account `fusion-weave-gitops`, which may create WeaveApps and
  nothing else. Anything else in the repo makes the whole sync fail.
- **Hostnames are a label, not a domain.** `ingressName: site` becomes `site.<cluster domain>`. You cannot pick a
  full domain.
- **Images need a fixed tag** (`nginx:1.27`, not `nginx` or `nginx:latest`) and must be on the cluster's allowed list.
  With a forge build (`codeSource`) the `image` is the runner image.
- **Schedules have six fields, seconds first:** `"0 0 2 * * *"` is 02:00:00 every day.
- **Run a job now:** set the annotation `fusion-platform.io/fire=<entrypoint>` on the app (in Spectra: *Run*).

## Tuning the Ingress (nginx and Traefik)

An app's Ingress gets its settings from three layers; a later one wins on the same key, nothing set earlier is removed:

1. the cluster-wide ingress settings (e.g. certificate issuer) — platform team,
2. settings for the app's runner type, e.g. every **Streamlit** app — platform team (`platform/helm-values-*.yaml`),
3. the app's own `service.ingressAnnotations` — you, in this repo.

**nginx** reads everything from annotations, so the app file is complete. **Traefik** reads only a few annotations
(entrypoint, TLS, which middlewares); login, headers and limits are *Middlewares* that the annotation points to.
The platform team creates those once (`platform/helm-values-traefik.yaml`) and every app can use them.

| What | ingress-nginx (in the app) | Traefik (in the app → Middleware from the platform) |
|---|---|---|
| Login via Keycloak (oauth2-proxy) | `auth-url`, `auth-signin` | `router.middlewares: fusion-oauth2-forward-auth@kubernetescrd` → `forwardAuth` |
| Who is logged in, as headers to the app | `auth-response-headers` | same middleware, `authResponseHeaders` |
| `X-Forwarded-For/-Host/-Proto/-Port` | sent by default; trusting a load balancer in front is a controller setting | sent by default; `fusion-forwarded-https` pins proto/port; trusting a load balancer is a Traefik setting |
| `X-Forwarded-Prefix` (app under a path) | `x-forwarded-prefix` | `headers.customRequestHeaders` middleware |
| Long websocket sessions (Streamlit) | `proxy-read-timeout`, `proxy-send-timeout` | nothing needed per route |
| Upload size | `proxy-body-size` | `fusion-upload-limit` → `buffering.maxRequestBodyBytes` |
| HTTPS only | `ssl-redirect` | `router.entrypoints: websecure`, `router.tls` |
| Sticky sessions (more than one pod) | `affinity: cookie` | **not possible** from a WeaveApp (a Service annotation in Traefik) → keep `replicas: 1` |

Technical details, commands and the full setup: [README_technical.md](README_technical.md).
