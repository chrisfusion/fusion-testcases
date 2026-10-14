# template-python-app-etl-shared-storage — technical notes

API/kubectl view of [README.md](README.md).

## 1. Build the app

```bash
kubectl port-forward -n fusion service/fusion-forge 18080:8080 --address 127.0.0.1
BASE=http://localhost:18080

curl -s -X POST $BASE/api/v1/appbuilds \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://<your-git-host>/<org>/<repo>.git","repo_ref":"main","project_dir":"v3-beta/template-python-app-etl-shared-storage"}'
```

GitOps variant: a `GitWatcher` with `buildType: app` and
`projectDir: v3-beta/template-python-app-etl-shared-storage`. Then move the tag `stable` to the
built version (see `testcases_v2/README.md`). The build log shows
`auto-discovered 3 python file(s): [count.py dashboard.py extract.py]` and copies `assets` and `kafka_etl`.

## 2. Create the chain and start a run

```bash
# save the manifests from "Reference manifests" below as etl.yaml
kubectl apply --dry-run=server -f etl.yaml
kubectl apply -f etl.yaml                          # templates + chain
kubectl create -f etl-run.yaml                     # the WeaveRun (last manifest), see note
kubectl get fr -n fusion -w
kubectl logs -n fusion -l fusion-platform.io/step=extract
kubectl logs -n fusion -l fusion-platform.io/step=count
kubectl port-forward -n fusion svc/etl-kafka-dashboard 8501:8501      # then open http://localhost:8501
```

Use `kubectl create` for the run, not `apply`: server-side apply can silently prune a
newly added CRD field such as `stepOverrides` shortly after a CRD update.
The run-owned Deployment and Service are named `<runName>-<stepName>`, here `etl-kafka-dashboard`.

Expected logs: `extract: 141034 chars raw -> 120497 chars clean ...`, then
`count: 19148 words, 3738 distinct ...` and `top 5: [('die', 626), ('und', 624), ...]`.

## Internals

- `sharedStorage` provisions a PVC `<runName>-shared` (ReadWriteMany) per run, owned by the WeaveRun. Mounted at `/weave-shared` in job pods (`jobbuilder`) and in run-owned deploy steps (`deploybuilder.ApplySharedStorage`); not in chain-owned deploy steps. On minikube RWX needs a suitable class such as `csi-hostpath-sc`.
- The run stays `Running` while the dashboard Deployment exists; deleting the run tears down the Deployment, Service, Ingress and PVC (finalizer `weave.fusion-platform.io/deploy-cleanup`).
- Env order of the run-owned dashboard: service template `env` first, then the code-source variables (`WEAVE_ARTIFACT`, ...). Step `envOverrides` do **not** apply to run-owned deploy steps — put `WEAVE_RUNNER_TYPE`/`ENTRYPOINT` into the service template.
- `WEAVE_RUNNER_TYPE` is only injected from the artifact's metadata when `runner.type` is set; this artifact omits it, so the per-step value stands.
- The run-owned path takes ports from the template unless the metadata sets `runner.port`; this artifact sets none, so the template's `8501` is used.

## Reference manifests

What the settings in the README stand for as Kubernetes manifests (for kubectl users; Spectra users set the
same fields in the GUI). Not part of the app build.

```yaml
apiVersion: weave.fusion-platform.io/v1alpha1
kind: WeaveJobTemplate
metadata:
  name: etl-job
  namespace: fusion
spec:
  image: fusion-runner-python312:local
  env:
    - name: WEAVE_RUNNER_TYPE      # the artifact sets no runner type, each template says it
      value: python
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
  codeSource:
    artifactName: app.template-python-app-etl-shared-storage
    tag: stable
---
apiVersion: weave.fusion-platform.io/v1alpha1
kind: WeaveServiceTemplate
metadata:
  name: etl-dashboard
  namespace: fusion
spec:
  image: fusion-runner-python312:local
  replicas: 1
  ports:
    - name: http
      port: 8501
      targetPort: 8501
      protocol: TCP
  env:
    - name: WEAVE_RUNNER_TYPE
      value: streamlit
    - name: ENTRYPOINT             # step envOverrides do not reach run-owned deploy steps
      value: dashboard.py
    - name: WEAVE_PORT
      value: "8501"
  resources:
    requests:
      cpu: 200m
      memory: 500Mi
    limits:
      cpu: 500m
      memory: 1Gi
  readinessProbe:
    httpGet:
      path: /_stcore/health
      port: 8501
    initialDelaySeconds: 10
    periodSeconds: 10
    failureThreshold: 6
  serviceType: ClusterIP
  unhealthyDuration: "5m"
---
apiVersion: weave.fusion-platform.io/v1alpha1
kind: WeaveChain
metadata:
  name: etl-kafka
  namespace: fusion
spec:
  failurePolicy: StopAll
  concurrencyPolicy: Wait
  sharedStorage:                    # one ReadWriteMany volume per run, mounted at /weave-shared
    size: 100Mi
    storageClassName: csi-hostpath-sc
  steps:
    - name: extract
      jobTemplateRef:
        name: etl-job
      envOverrides:
        - name: ENTRYPOINT
          value: extract.py
    - name: count
      dependsOn: [extract]
      jobTemplateRef:
        name: etl-job
      envOverrides:
        - name: ENTRYPOINT
          value: count.py
    - name: dashboard
      stepKind: Deploy
      dependsOn: [count]
      serviceTemplateRef:
        name: etl-dashboard
```

The run (save as `etl-run.yaml`, create with `kubectl create`):

```yaml
apiVersion: weave.fusion-platform.io/v1alpha1
kind: WeaveRun
metadata:
  name: etl-kafka
  namespace: fusion
spec:
  chainRef:
    name: etl-kafka
  stepOverrides:                    # makes the dashboard run-owned -> it gets /weave-shared
    - stepName: dashboard
      artifactName: app.template-python-app-etl-shared-storage
      tag: stable
      # ingressName: kafka          # optional: https://kafka.<ingress.hostSuffix>
```

## Local run

```bash
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
export SHARED_DIR=$(mktemp -d)
PYTHONPATH=. .venv/bin/python extract.py
PYTHONPATH=. .venv/bin/python count.py
PYTHONPATH=. .venv/bin/python -m streamlit run dashboard.py
```
