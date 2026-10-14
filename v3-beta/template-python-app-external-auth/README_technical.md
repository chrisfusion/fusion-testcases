# template-python-app-external-auth — technical notes

API/kubectl view of [README.md](README.md).

## 1. Build the app

Same flow as [`template-python-app-no-assets`](../template-python-app-no-assets/README_technical.md);
only the project directory differs.

```bash
kubectl port-forward -n fusion service/fusion-forge 18080:8080 --address 127.0.0.1
BASE=http://localhost:18080

curl -s -X POST $BASE/api/v1/appbuilds \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://<your-git-host>/<org>/<repo>.git","repo_ref":"main","project_dir":"v3-beta/template-python-app-external-auth"}'
```

GitOps variant: a `GitWatcher` with `buildType: app` and
`projectDir: v3-beta/template-python-app-external-auth`. Then move the tag `stable`
to the built version (see `testcases_v2/README.md`).

## 2. Check the allowlist

```bash
# deploy-time allowlists as the operator sees them
kubectl get deploy -n fusion fusion-weave-operator \
  -o jsonpath='{.spec.template.spec.containers[0].env}' | tr ',' '\n' | grep -A1 EXTERNAL_AUTH
kubectl get sa -n fusion ext-auth-demo-sa
```

Helm values: `externalAuth.serviceAccounts`, `externalAuth.oidcSecrets`,
`externalAuth.defaultTokenTTL`, `externalAuth.saAudience`.

## 3. Apply and fire

```bash
# save the manifests from "Reference manifests" below as chain.yaml
kubectl apply --dry-run=server -f chain.yaml
kubectl apply -f chain.yaml
kubectl annotate weavetrigger external-auth-trigger fusion-platform.io/fire=true --overwrite -n fusion
kubectl get fr -n fusion -w
kubectl logs -n fusion -l fusion-platform.io/chain=external-auth,fusion-platform.io/step=show-token
```

Expected with the defaults: token present as file **and** env var, `file and env hold the
same token: True`, `token used by the app: from file`, `sub` =
`system:serviceaccount:fusion:ext-auth-demo-sa`, `aud` = `fusion`.

## 4. File-only mode

Set `unsafeEnvironmentInjector: false` in the chain (GUI or manifest), re-apply and fire again. The
`WEAVE_EXTERNAL_AUTH_TOKEN` row then shows `<not set>`, the file row is unchanged and the
app still works because it reads the file first. Per trigger / run:
`unsafeEnvironmentInjectorOverride`; `externalAuthRefOverride` swaps the identity.

## Reference manifests

What the GUI settings below stand for as Kubernetes manifests (for kubectl users; Spectra users set the
same fields in the GUI, see [README.md](README.md)). Not part of the app build.

```yaml
# SPDX-License-Identifier: GPL-3.0-or-later
# Manifests that hand a short-lived external-auth token to the app. Plain
# kubectl-applyable; NOT part of the app build.
#
# Prerequisites (maintainer, once per cluster - the operator never creates these):
#   * Helm values of fusion-weave: externalAuth.serviceAccounts: [ext-auth-demo-sa]
#       (mode oidc instead: externalAuth.oidcSecrets: [<secret>] with keys
#        clientId, clientSecret, tokenURL in the operator's namespace)
#   * the ServiceAccount itself:  kubectl create serviceaccount ext-auth-demo-sa -n fusion
#   * the app published as app.template-python-app-external-auth, tag `stable`
#
# Apply, fire, read the log:
#   kubectl apply -f chain.yaml
#   kubectl annotate weavetrigger external-auth-trigger fusion-platform.io/fire=true --overwrite -n fusion
#   kubectl get fr -n fusion -w
---
apiVersion: weave.fusion-platform.io/v1alpha1
kind: WeaveJobTemplate
metadata:
  name: external-auth
  namespace: fusion
spec:
  image: fusion-runner-python312:local
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 300m
      memory: 256Mi
  # Short-lived token: if set, the token lifetime follows this deadline (but
  # never below the Kubernetes minimum of 10 minutes for serviceAccount mode).
  # Without it Helm externalAuth.defaultTokenTTL applies.
  activeDeadlineSeconds: 600
  codeSource:
    artifactName: app.template-python-app-external-auth
    tag: stable
---
apiVersion: weave.fusion-platform.io/v1alpha1
kind: WeaveChain
metadata:
  name: external-auth
  namespace: fusion
spec:
  failurePolicy: StopAll
  concurrencyPolicy: Wait
  # The one setting this example is about. Job-kind steps only.
  #   mode: serviceAccount -> Kubernetes ServiceAccount token (TokenRequest API)
  #   mode: oidc           -> Keycloak access token (client_credentials grant)
  # `name` must be on the operator's allowlist for that mode, else the chain is invalid.
  externalAuthRef:
    mode: serviceAccount
    name: ext-auth-demo-sa
  # true (default): the token arrives as FILE *and* as env var WEAVE_EXTERNAL_AUTH_TOKEN.
  # false:          FILE only - the env var disappears, the app must read the file.
  # Try both and compare the report. Per trigger / per run: unsafeEnvironmentInjectorOverride.
  unsafeEnvironmentInjector: true
  steps:
    - name: show-token
      jobTemplateRef:
        name: external-auth
---
apiVersion: weave.fusion-platform.io/v1alpha1
kind: WeaveTrigger
metadata:
  name: external-auth-trigger
  namespace: fusion
spec:
  chainRef:
    name: external-auth
  type: OnDemand
```

## Internals

- The operator stores the minted token in a per-job Secret (`<jobName>-ext-auth`), mounted read-only at `/var/run/secrets/fusion-platform.io/external-auth/` (key `token`). The env var is a `secretKeyRef` to that key.
- `serviceAccount` mode: TokenRequest API with audience `externalAuth.saAudience`; the TTL is derived from `activeDeadlineSeconds` or `defaultTokenTTL`, clamped to Kubernetes' 10-minute floor.
- `oidc` mode: Keycloak `client_credentials` grant using the allowlisted Secret.
- Sources (fusion-flux): `api/v1alpha1/weavechain_types.go` (`WeaveExternalAuthRef`), `internal/jobbuilder/builder.go` (mount and env), `CHANGELOG.md` (feature notes).

## Local run

```bash
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python main.py    # prints "no token injected"
```
Set `WEAVE_EXTERNAL_AUTH_TOKEN_FILE` / `WEAVE_EXTERNAL_AUTH_TOKEN` to a JWT to simulate the injection.
