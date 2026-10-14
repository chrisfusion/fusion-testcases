# template-python-app-streamlit — technical notes

API/kubectl view of [README.md](README.md).

## 1. Build the app

```bash
kubectl port-forward -n fusion service/fusion-forge 18080:8080 --address 127.0.0.1
BASE=http://localhost:18080

curl -s -X POST $BASE/api/v1/appbuilds \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://<your-git-host>/<org>/<repo>.git","repo_ref":"main","project_dir":"v3-beta/template-python-app-streamlit"}'
```

GitOps variant: a `GitWatcher` with `buildType: app` and
`projectDir: v3-beta/template-python-app-streamlit`. Then move the tag `stable` to the
built version (see `testcases_v2/README.md`). The build log lists `copying assets → site-packages`
and `copying wordviz → site-packages`; there is no root-asset line.

## 2. Deploy and open

```bash
# save the manifests from "Reference manifests" below as app.yaml
kubectl apply --dry-run=server -f app.yaml
kubectl apply -f app.yaml
kubectl annotate weavetrigger streamlit-wordcount-trigger fusion-platform.io/fire=true --overwrite -n fusion
kubectl get pods -n fusion -w                       # wait for the app pod to be Ready
kubectl port-forward svc/<service-name> 8501:8501 -n fusion
# open http://localhost:8501
```

The service name is the chain-owned name of the Deploy step: `kubectl get svc -n fusion | grep streamlit-wordcount`.

## Internals

- fusion-runner (`streamlit` type) runs `python -m streamlit run <mountPath>/$ENTRYPOINT` with `STREAMLIT_SERVER_HEADLESS=true`, `STREAMLIT_SERVER_ADDRESS=0.0.0.0` and `STREAMLIT_SERVER_PORT` from `runner.port`.
- `ingress.path` in `metadata.yaml` (optional) reaches the runner as `WEAVE_INGRESS_PATH` and becomes `STREAMLIT_SERVER_BASE_URL_PATH`. Unset or `/` serves at the root.
- The **hostname** is not in `metadata.yaml`: it comes from the ingress rule `name` on the service template plus the cluster-wide `ingress.hostSuffix`. A template with an ingress is invalid until `hostSuffix` is configured.
- A Deploy step is polled for new versions of the `stable` tag and rolled; unhealthy deployments are rolled back after `unhealthyDuration`.
- Reference: `testcases_v2/app-builds/streamlit-showcase/` and the showroom chain `codesource-streamlit.yaml` in fusion-weave.

## Reference manifests

What the settings in the README stand for as Kubernetes manifests (for kubectl users; Spectra users set the
same fields in the GUI). Not part of the app build.

```yaml
apiVersion: weave.fusion-platform.io/v1alpha1
kind: WeaveServiceTemplate
metadata:
  name: streamlit-wordcount
  namespace: fusion
spec:
  image: fusion-runner-python312:local
  replicas: 1
  ports:
    - name: http
      port: 8501
      targetPort: 8501      # must match runner.port in metadata.yaml
      protocol: TCP
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
  revisionHistoryLimit: 2
  codeSource:
    artifactName: app.template-python-app-streamlit
    tag: stable
  # Optional: expose under <name>.<ingress.hostSuffix>, e.g. wordcount.fusion.local.
  # ingress:
  #   rules:
  #     - name: wordcount
  #       path: /
  #       pathType: Prefix
  #       servicePort: http
---
apiVersion: weave.fusion-platform.io/v1alpha1
kind: WeaveChain
metadata:
  name: streamlit-wordcount
  namespace: fusion
spec:
  failurePolicy: StopAll
  concurrencyPolicy: Wait
  steps:
    - name: app
      stepKind: Deploy
      serviceTemplateRef:
        name: streamlit-wordcount
      runOnSuccess: true
---
apiVersion: weave.fusion-platform.io/v1alpha1
kind: WeaveTrigger
metadata:
  name: streamlit-wordcount-trigger
  namespace: fusion
spec:
  chainRef:
    name: streamlit-wordcount
  type: OnDemand
```

## Local run

```bash
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
PYTHONPATH=. .venv/bin/python -m streamlit run main.py
```
