# template-python-app-assets-dir — technical notes

API-level view of [README.md](README.md). Differences to
[`template-python-app-root-asset`](../template-python-app-root-asset/README_technical.md) are only the
asset handling and the artifact name.

## Prerequisite

```bash
kubectl port-forward -n fusion service/fusion-forge 18080:8080 --address 127.0.0.1
BASE=http://localhost:18080
```

## Validate and build (app build)

```bash
curl -s -X POST $BASE/api/v1/appbuilds/validate \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://<your-git-host>/<org>/<repo>.git","repo_ref":"main","project_dir":"v3-beta/template-python-app-assets-dir"}'

curl -s -X POST $BASE/api/v1/appbuilds \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://<your-git-host>/<org>/<repo>.git","repo_ref":"main","project_dir":"v3-beta/template-python-app-assets-dir"}'
```

Status and logs: `GET /api/v1/appbuilds/<id>` and `GET /api/v1/appbuilds/<id>/logs`.

## GitOps: build on every push (GitWatcher)

```yaml
apiVersion: build.fusion-platform.io/v1alpha1
kind: GitWatcher
metadata:
  name: template-python-app-assets-dir-watcher
  namespace: fusion
spec:
  repoURL: https://<your-git-host>/<org>/<repo>.git
  repoRef: main
  buildType: app
  enabled: true
  projectDir: v3-beta/template-python-app-assets-dir
```

## Asset internals

- With `rootAssets: false` (or the key absent) the builder skips `copyRootAssets` entirely; the builder log has no `copied N root asset file(s)` line.
- `assets/` is handled by the generic step that copies every project sub-directory into `site-packages` (`cp -r`), exactly like `wordstats/`. No flag involved.
- Do not name your own package `_root_assets`: that name is reserved for the root-asset mechanism (operator setting `builderRootAssetsPackage`) and the build fails on a clash when `rootAssets: true`.

## Local run (no simulation needed)

```bash
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python main.py      # assets/ and wordstats/ resolve from the working directory
```
