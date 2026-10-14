# template-python-app — technical notes

API-level view of the flow in [README.md](README.md).

## Prerequisite

```bash
kubectl port-forward -n fusion service/fusion-forge 18080:8080 --address 127.0.0.1
BASE=http://localhost:18080
```

## Validate and build (app build)

Only the repository coordinates are sent; name, version and builder image come from
`metadata.yaml`. If this template lives in a sub-directory of a larger repo, set `project_dir`.

```bash
curl -s -X POST $BASE/api/v1/appbuilds/validate \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://<your-git-host>/<org>/<repo>.git","repo_ref":"main","project_dir":"v3-beta/template-python-app"}'

curl -s -X POST $BASE/api/v1/appbuilds \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://<your-git-host>/<org>/<repo>.git","repo_ref":"main","project_dir":"v3-beta/template-python-app"}'
```

Status and logs: `GET /api/v1/appbuilds/<id>` and `GET /api/v1/appbuilds/<id>/logs`.

## GitOps: build on every push (GitWatcher)

```yaml
apiVersion: build.fusion-platform.io/v1alpha1
kind: GitWatcher
metadata:
  name: template-python-app-watcher
  namespace: fusion
spec:
  repoURL: https://<your-git-host>/<org>/<repo>.git
  repoRef: main
  buildType: app
  enabled: true
  projectDir: v3-beta/template-python-app
  # private repo: Secret with an access token
  # tokenSecretRef: { name: <secret>, key: token }
```

For `buildType: app`, `metadataSource`/`name`/`version` are ignored — `metadata.yaml` is authoritative.
Remember to bump `version` in `metadata.yaml`; an unchanged version is not rebuilt.

## Root assets internals

- `rootAssets: true` makes the builder copy regular, non-`.py` root files (skipping `requirements.txt`, `metadata.yaml`, dotfiles, symlinks, directories) into `site-packages/<pkg>/` together with an empty `__init__.py`.
- `<pkg>` defaults to `_root_assets`; it is an operator setting (Helm `operator.config.builderRootAssetsPackage`), not a `metadata.yaml` value.
- The build fails if a project directory or dependency already uses that package name — do not name your own package `_root_assets`.
- Root `.py` files are not assets; they are handled by the `files` key (not used here, `main.py` is the legacy single-file mode).

## Local smoke test

The `_root_assets` package only exists after a forge build. To test locally, simulate it:

```bash
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
SP=$(.venv/bin/python -c 'import site;print(site.getsitepackages()[0])')
mkdir $SP/_root_assets && touch $SP/_root_assets/__init__.py && cp words.txt $SP/_root_assets/
cp -r wordstats $SP/
.venv/bin/python main.py
```

## Source references (fusion-forge)

`EXAMPLES.md` §3 (app builds, assets), `internal/gitutil/metadata.go` (metadata.yaml keys),
`builder/main.go` (`copyRootAssets`).
