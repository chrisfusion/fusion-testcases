# template-python-app-inject-variables — technical notes

API/kubectl view of [README.md](README.md).

## 1. Build the app

Same flow as [`template-python-app-no-assets`](../template-python-app-no-assets/README_technical.md);
only the project directory differs.

```bash
kubectl port-forward -n fusion service/fusion-forge 18080:8080 --address 127.0.0.1
BASE=http://localhost:18080

curl -s -X POST $BASE/api/v1/appbuilds \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://<your-git-host>/<org>/<repo>.git","repo_ref":"main","project_dir":"v3-beta/template-python-app-inject-variables"}'
```

GitOps variant: a `GitWatcher` with `buildType: app` and
`projectDir: v3-beta/template-python-app-inject-variables`.

The Kubernetes manifests that use the app are not part of this directory; they are listed under
"Reference manifests" below.

## 2. Tag the artifact

The reference manifests reference `app.template-python-app-inject-variables` with tag `stable`.
Move the tag to the built version (see `testcases_v2/README.md` for the index calls).

## 3. Apply and fire

```bash
# save the manifests from "Reference manifests" below as chain.yaml
kubectl apply --dry-run=server -f chain.yaml     # validate against the CRDs first
kubectl apply -f chain.yaml
kubectl annotate weavetrigger inject-variables-trigger fusion-platform.io/fire=true --overwrite -n fusion
kubectl get fr -n fusion -w
kubectl logs -n fusion -l fusion-platform.io/chain=inject-variables,fusion-platform.io/step=report
```

Expected: ways 1, 2, 3, 4, 6 and 8 show values/lengths; 5 (BatchCron) and 7
(`externalAuthRef`) show `<not set>` unless you use a BatchCron trigger / enable the
commented `externalAuthRef` block.

## 4. Try the file-only mode

Set `unsafeEnvironmentInjector: false` in the chain, re-apply and fire again. The
`API_KEY` row of way 6 then shows `<not set>` as `env` but is still listed as a `file`.
Per trigger / per run this is `unsafeEnvironmentInjectorOverride`.

## Reference manifests

What the settings in [README.md](README.md) stand for as Kubernetes manifests (for kubectl users; Spectra users
set the same fields in the GUI). Not part of the app build.

```yaml
# SPDX-License-Identifier: GPL-3.0-or-later
# Kubernetes manifests that switch on every injection way shown in
# injection/sources.py. Plain kubectl-applyable; NOT part of the app build
# (a separate deployment step, not built by the forge).
#
# Publish the app first (forge app build / GitWatcher, see README_technical.md) so
# that artifact app.template-python-app-inject-variables has the tag `stable`.
#
# Apply, fire, read the log:
#   kubectl apply -f chain.yaml
#   kubectl annotate weavetrigger inject-variables-trigger fusion-platform.io/fire=true --overwrite -n fusion
#   kubectl get fr -n fusion -w
#
# Secret values below are fake placeholders. Never commit real secrets - create
# them with `kubectl create secret` or let your secret manager sync them.
---
# Source for way 2 (valueFrom) and way 8 (mounted files).
apiVersion: v1
kind: ConfigMap
metadata:
  name: inject-variables-config
  namespace: fusion
data:
  db-host: "db.example.local"
---
# Source for way 2 (valueFrom a Secret key).
apiVersion: v1
kind: Secret
metadata:
  name: inject-variables-db
  namespace: fusion
stringData:
  password: "fake-db-password"
---
# Source for way 6 (authSecretRef): every key becomes a FILE in
# WEAVE_AUTH_SECRET_DIR and, while unsafeEnvironmentInjector is true, an ENV var.
apiVersion: v1
kind: Secret
metadata:
  name: inject-variables-auth
  namespace: fusion
stringData:
  API_KEY: "fake-api-key"
  SERVICE_URL: "https://service.example.local"
---
# Source for way 8 (template volumes): one file per key under the mountPath.
apiVersion: v1
kind: Secret
metadata:
  name: inject-variables-files
  namespace: fusion
stringData:
  license.key: "fake-license"
---
apiVersion: weave.fusion-platform.io/v1alpha1
kind: WeaveJobTemplate
metadata:
  name: inject-variables
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
  codeSource:
    artifactName: app.template-python-app-inject-variables
    tag: stable
  # WAY 2: static env, and env taken from a ConfigMap / Secret key.
  env:
    - name: LOG_LEVEL
      value: INFO
    - name: DB_HOST
      valueFrom:
        configMapKeyRef:
          name: inject-variables-config
          key: db-host
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: inject-variables-db
          key: password
  # WAY 8: Secret (or ConfigMap) mounted as files at a path of your choice.
  volumes:
    - name: app-secrets
      mountPath: /etc/app-secrets   # must match CUSTOM_MOUNT_DIR in injection/sources.py
      secretName: inject-variables-files
---
apiVersion: weave.fusion-platform.io/v1alpha1
kind: WeaveChain
metadata:
  name: inject-variables
  namespace: fusion
spec:
  failurePolicy: StopAll
  concurrencyPolicy: Wait
  # WAY 6: whole Secret -> files in WEAVE_AUTH_SECRET_DIR (+ env vars, see below).
  authSecretRef:
    name: inject-variables-auth
  # WAY 7 (optional): operator-minted short-lived token. The name must be on the
  # operator's allowlist (Helm externalAuth.serviceAccounts / externalAuth.oidcSecrets),
  # otherwise the chain is invalid - hence commented out.
  # externalAuthRef:
  #   mode: serviceAccount
  #   name: <allowlisted-serviceaccount>
  # Set to false to REMOVE the env variants of way 6 and 7 and keep only the files.
  # Try it: the report then shows API_KEY as "<not set>" in env but still as a file.
  unsafeEnvironmentInjector: true
  steps:
    - name: report
      jobTemplateRef:
        name: inject-variables
      # WAY 3: per-step env. The same template could serve other steps with other values.
      envOverrides:
        - name: STEP_NOTE
          value: "set by the chain step"
---
# WAY 5 needs a BatchCron trigger (see ../../testcases_v2/app-builds/batch-metadata-reader);
# with this OnDemand trigger the JOB_* rows stay "<not set>".
apiVersion: weave.fusion-platform.io/v1alpha1
kind: WeaveTrigger
metadata:
  name: inject-variables-trigger
  namespace: fusion
spec:
  chainRef:
    name: inject-variables
  type: OnDemand
```

## Source references (fusion-flux)

| Topic | Where |
|---|---|
| Field docs | `api/v1alpha1/weavechain_types.go` (`authSecretRef`, `externalAuthRef`, `unsafeEnvironmentInjector`, `envOverrides`), `weavejobtemplate_types.go` (`env`, `volumes`) |
| Mount paths and env names | `internal/jobbuilder/builder.go` — `/var/run/secrets/fusion-platform.io/auth-secret`, `.../external-auth/token`, `WEAVE_AUTH_SECRET_DIR`, `WEAVE_EXTERNAL_AUTH_*` |
| codeSource variables, `runner.args` | `internal/codesource/codesource.go` |
| External auth allowlist | Helm `externalAuth.serviceAccounts` / `externalAuth.oidcSecrets` |
