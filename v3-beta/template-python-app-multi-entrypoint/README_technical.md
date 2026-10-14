# template-python-app-multi-entrypoint — technical notes

API/kubectl view of [README.md](README.md).

## 1. Build the app

```bash
kubectl port-forward -n fusion service/fusion-forge 18080:8080 --address 127.0.0.1
BASE=http://localhost:18080

curl -s -X POST $BASE/api/v1/appbuilds \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://<your-git-host>/<org>/<repo>.git","repo_ref":"main","project_dir":"v3-beta/template-python-app-multi-entrypoint"}'
```

GitOps variant: a `GitWatcher` with `buildType: app` and
`projectDir: v3-beta/template-python-app-multi-entrypoint`. Then move the tag `stable`
to the built version (see `testcases_v2/README.md`).

The response has `"fileUploadMode":"auto"` (legacy single-`main.py` builds show `"legacy"`).
The builder log lists the uploaded loose files: `count.py`, `top.py`, `longest.py`.

## 2. Apply and fire

```bash
# save the manifests from "Reference manifests" below as chain.yaml
kubectl apply --dry-run=server -f chain.yaml
kubectl apply -f chain.yaml
kubectl annotate weavetrigger multi-entrypoint-trigger fusion-platform.io/fire=true --overwrite -n fusion
kubectl get fr -n fusion -w
kubectl logs -n fusion -l fusion-platform.io/chain=multi-entrypoint,fusion-platform.io/step=top
```

Expected log lines: `count: 43 words, 35 distinct, 231 Bytes` · a table of the top 3 words ·
`longest words: application, repository, rootassets`.

## Internals

- `metadata.yaml` `files` is tri-state: absent = legacy (`main.py` required, only file uploaded), `[]` = auto-discover top-level `*.py`, list = exactly those. Names are validated: no absolute paths, no `..`.
- fusion-runner (`python` type) runs `python <codeSource mountPath>/$ENTRYPOINT` with the venv's interpreter; without `ENTRYPOINT` it fails with "ENTRYPOINT env var is not set". Packages in the venv are importable; sibling scripts are not.
- Container env order: template `env` → step `envOverrides` → code-source variables including `runner.args`; the last duplicate wins.
- Reference: `testcases_v2/app-builds/etl-pipeline/` (five scripts, chained) and its `EXPLANATION.md`.

## Reference manifests

What the settings in the README stand for as Kubernetes manifests (for kubectl users; Spectra users set the
same fields in the GUI). Not part of the app build.

```yaml
# One job template shared by all steps; each step picks its script via ENTRYPOINT.
apiVersion: weave.fusion-platform.io/v1alpha1
kind: WeaveJobTemplate
metadata:
  name: multi-entrypoint
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
    artifactName: app.template-python-app-multi-entrypoint
    tag: stable
---
apiVersion: weave.fusion-platform.io/v1alpha1
kind: WeaveChain
metadata:
  name: multi-entrypoint
  namespace: fusion
spec:
  failurePolicy: StopAll
  concurrencyPolicy: Wait
  # No dependsOn -> the three steps run in parallel.
  steps:
    - name: count
      jobTemplateRef:
        name: multi-entrypoint
      envOverrides:
        - name: ENTRYPOINT
          value: count.py
    - name: top
      jobTemplateRef:
        name: multi-entrypoint
      envOverrides:
        - name: ENTRYPOINT
          value: top.py
        - name: TOP_N          # extra, script-specific setting of this step
          value: "3"
    - name: longest
      jobTemplateRef:
        name: multi-entrypoint
      envOverrides:
        - name: ENTRYPOINT
          value: longest.py
---
apiVersion: weave.fusion-platform.io/v1alpha1
kind: WeaveTrigger
metadata:
  name: multi-entrypoint-trigger
  namespace: fusion
spec:
  chainRef:
    name: multi-entrypoint
  type: OnDemand
```

## Local run

```bash
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
PYTHONPATH=. .venv/bin/python count.py
TOP_N=3 PYTHONPATH=. .venv/bin/python top.py
```
