# monorepo-widget

Unrelated top-level repo content on purpose — the buildable package lives under
`services/widget-lib/`, not at the repo root. Exercises `projectDir` on both
`GitWatcher.spec.projectDir` and `CIBuild.spec.gitSource.projectDir` (fusion-forge),
which shifts the root used for `pyproject.toml` lookup, wheel build, and (for
app-builds) structure validation / entrypoint resolution.

Point a GitWatcher or a manual gitbuild request at this repo with:

```yaml
projectDir: testcases_v2/git-builds/monorepo-widget/services/widget-lib
```
