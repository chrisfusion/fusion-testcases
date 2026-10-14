# template-python-app-no-assets — technical notes

API-level view of [README.md](README.md). Build flow and API calls are identical to
[`template-python-app-assets-dir`](../template-python-app-assets-dir/README_technical.md);
only the project directory and artifact name differ.

## Prerequisite

```bash
kubectl port-forward -n fusion service/fusion-forge 18080:8080 --address 127.0.0.1
BASE=http://localhost:18080
```

## Validate and build (app build)

```bash
curl -s -X POST $BASE/api/v1/appbuilds/validate \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://<your-git-host>/<org>/<repo>.git","repo_ref":"main","project_dir":"v3-beta/template-python-app-no-assets"}'

curl -s -X POST $BASE/api/v1/appbuilds \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://<your-git-host>/<org>/<repo>.git","repo_ref":"main","project_dir":"v3-beta/template-python-app-no-assets"}'
```

Status and logs: `GET /api/v1/appbuilds/<id>` and `GET /api/v1/appbuilds/<id>/logs`.

## GitOps: build on every push (GitWatcher)

```yaml
apiVersion: build.fusion-platform.io/v1alpha1
kind: GitWatcher
metadata:
  name: template-python-app-no-assets-watcher
  namespace: fusion
spec:
  repoURL: https://<your-git-host>/<org>/<repo>.git
  repoRef: main
  buildType: app
  enabled: true
  projectDir: v3-beta/template-python-app-no-assets
```

## Internals

- `rootAssets` is absent, so the builder skips `copyRootAssets`; the builder log has no `copied N root asset file(s)` line.
- `wordstats/` is copied into `site-packages` by the generic step that copies every project sub-directory.
- Legacy file-upload mode (no `files` key in `metadata.yaml`): `main.py` is required and is the only loose file uploaded next to the venv pack.

## Local run

```bash
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python main.py
```
