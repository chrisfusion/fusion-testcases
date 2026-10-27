# weaveapp-gitops — technical notes

## Prerequisites

| What | Where | Needed by |
|---|---|---|
| fusion-weave with `WeaveApp.spec.service.ingressAnnotations` (CRD + operator) | fusion-flux `[Unreleased]` | `streamlit-nginx`, `streamlit-traefik` |
| Artifacts `app.template-wizard-*`, tag `stable` | built by the wizard GitWatchers (see the `template-wizard-*` READMEs) | `python-job-*`, `streamlit*` |
| Runner image `fusion-runner-python312:local` on `ALLOWED_IMAGE_PREFIXES` | operator env | `python-job-*`, `streamlit*` |
| `ext-auth-demo-sa` on `EXTERNAL_AUTH_SERVICE_ACCOUNTS` | operator env | `python-job-single` |
| `ingress.hostSuffix` set (here `fusion.local`) | fusion-weave Helm values | every app with an ingress |
| oauth2-proxy + Keycloak client | [`platform/oauth2-proxy-values.yaml`](platform/oauth2-proxy-values.yaml) | `streamlit-nginx`, `streamlit-traefik` |
| Traefik Middlewares | [`platform/helm-values-traefik.yaml`](platform/helm-values-traefik.yaml) (rendered by the fusion-weave chart) | `streamlit-traefik` |

## Apply without Flux

```bash
kubectl kustomize v3-beta/weaveapp-gitops                    # what Flux would apply
kubectl apply -k v3-beta/weaveapp-gitops --dry-run=server
kubectl apply -k v3-beta/weaveapp-gitops
kubectl get fa -n fusion -w                                   # phase: Pending -> Ready
```

An app in phase `Invalid` says why: `kubectl get fa <name> -n fusion -o jsonpath='{.status.validationMessage}'`.
`strict decoding error: unknown field "spec.service.ingressAnnotations"` means the cluster still has an older
WeaveApp CRD: `kubectl apply -f config/crd/bases/weave.fusion-platform.io_weaveapps.yaml` (fusion-flux).

## Apply with Flux

[`platform/flux.yaml`](platform/flux.yaml): a `GitRepository` and a Flux `Kustomization` in the release namespace
`fusion`, `serviceAccountName: fusion-weave-gitops`, `prune: true`. Check what the account may do:

```bash
kubectl auth can-i create weaveapps -n fusion --as system:serviceaccount:fusion:fusion-weave-gitops   # yes
kubectl auth can-i create deployments -n fusion --as system:serviceaccount:fusion:fusion-weave-gitops # no
```

## Jobs

```bash
kubectl annotate fa image-job fusion-platform.io/fire=adhoc --overwrite -n fusion     # run now
kubectl get fa image-job -n fusion -o jsonpath='{range .status.executions[*]}{.entrypoint} {.phase} {.jobName}{"\n"}{end}'
kubectl logs -n fusion job/<jobName>
```

Via the API: `PATCH /api/v1/apps/image-job` with `{"metadata":{"annotations":{"fusion-platform.io/fire":"adhoc"}}}`;
logs: `GET /monitor/v1/apps/image-job/logs?entrypoint=adhoc`.

## Names of the created objects

| App type | Objects |
|---|---|
| service | Deployment, Service and Ingress `<app>-app` (e.g. `streamlit-nginx-app`) |
| job | one Job per execution, labels `fusion-platform.io/app=<app>`, `fusion-platform.io/entrypoint=<ep>` |

```bash
kubectl get ingress streamlit-nginx-app -n fusion -o jsonpath='{.metadata.annotations}' | jq
```

## How the ingress annotations combine

Order (later wins per key, never removes):

1. fusion-weave Helm `ingress.annotations` (env `INGRESS_ANNOTATIONS`),
2. `ingress.runnerAnnotations[<metadata.yaml runner.type>]` (env `INGRESS_RUNNER_ANNOTATIONS`) — only for apps with
   `codeSource`, since the runner type comes from the artifact's `metadata.yaml`,
3. the app's `spec.service.ingressAnnotations`.

The operator only ever adds or updates annotations on an existing Ingress: a key deleted from the app stays on the
Ingress until the Ingress is recreated (e.g. delete the Ingress, the operator rebuilds it on the next reconcile).

A value is replaced as a whole: `traefik.ingress.kubernetes.io/router.middlewares` set by an app replaces the
runner-type value instead of appending to it — list every middleware the app needs (see `streamlit-traefik.yaml`).

## Writable folders

`spec.writablePaths[]` (`mountPath`, optional `sizeLimit`, optional `medium: Memory`) becomes one emptyDir per
path, mounted into the app container and the `code-loader` init container. Layers, in order:

1. operator `WRITABLE_PATHS` (Helm `codeSource.writablePaths`) — only for `codeSource` apps,
2. `RUNNER_WRITABLE_PATHS` (Helm `codeSource.runnerWritablePaths[<metadata.yaml runner.type>]`) — only for
   `codeSource` apps,
3. the app's `spec.writablePaths` — any app, with or without `codeSource`.

A path already mounted from an emptyDir only takes `sizeLimit`/`medium` from a later entry; nothing is
duplicated or removed. Relative paths, `/`, duplicates and paths used by `spec.volumes` or the code mount
(`/weave-code`) make the app `Invalid`.

```bash
kubectl get deploy streamlit-app -n fusion -o json | jq -c '[.spec.template.spec.volumes[] | {name, emptyDir}]'
kubectl exec -n fusion deploy/streamlit-app -c service -- touch /x    # Read-only file system
```

The fusion runner image runs as uid 1000 with `HOME=/home/runner` (not `/home/nonroot`, which the default
`WRITABLE_PATHS` lists).

## Traefik Middlewares

The fusion-weave chart renders `ingress.traefik.middlewares.<name>` as `Middleware/<name>` in the release namespace,
spec copied verbatim — only when the cluster has the `traefik.io/v1alpha1` Middleware CRD. Check the rendering:

```bash
helm template fusion-weave ../fusion-flux/deployment/fusion-weave -n fusion \
  -f v3-beta/weaveapp-gitops/platform/helm-values-traefik.yaml \
  --api-versions traefik.io/v1alpha1/Middleware -s templates/traefik-middlewares.yaml
```

(Plain `helm template` sees no cluster CRDs and renders nothing; `--api-versions` or
`ingress.traefik.skipCapabilityCheck=true` forces it.) A route whose middleware does not exist is not served by
Traefik at all — create the Middlewares before applying `streamlit-traefik/`.

## Login flow (oauth2-proxy)

- **nginx:** every request → `auth-url` (`/oauth2/auth`: 202 logged in / 401 not) → on 401 the browser goes to
  `auth-signin` (`https://auth.fusion.local/oauth2/start?rd=…`) → Keycloak → `/oauth2/callback` → back to the app.
- **Traefik:** `forwardAuth` on oauth2-proxy's `/` with `--upstream=static://202 --reverse-proxy`: logged in → 202,
  not logged in → oauth2-proxy itself redirects to Keycloak. `/oauth2/auth` would only answer 401 and the browser
  would show an error, which is why the address differs from nginx's.
- One cookie for `.fusion.local`, so one login covers every protected app.
- `X-Auth-Request-User/-Email/-Groups` reach the app (`--set-xauthrequest`); in Streamlit:
  `st.context.headers["X-Auth-Request-Email"]`.

## Notes

- `streamlit-nginx` runs 2 replicas with cookie affinity; `streamlit-traefik` runs 1, because Traefik's sticky
  sessions are a *Service* annotation and a WeaveApp can only annotate its Ingress.
- `image-site` runs the stock `nginx` image as root on port 80. On a cluster with `WORKLOAD_SECURITY_DEFAULTS`
  enforcing `runAsNonRoot` use an unprivileged image (e.g. `nginxinc/nginx-unprivileged:1.27`, port 8080).
- `python-job-multi` sets `ENTRYPOINT` per entrypoint; its artifact's `metadata.yaml` must not set
  `runner.args.ENTRYPOINT`, which would override all three.
- The apps use `namespace: fusion` explicitly; the Flux Kustomization also sets `targetNamespace: fusion`.
