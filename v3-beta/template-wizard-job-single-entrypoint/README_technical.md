# template-wizard-job-single-entrypoint — technical notes

The wizard flow of [README.md](README.md) as kubectl. The wizard definition is `python-git-job`
(`fusion-wizard`, chart `definitions/python-git-job.yaml`).

## Check the definition and start a wizard run

```bash
kubectl get wizarddefinitions -n fusion                 # python-git-job must exist
kubectl apply --dry-run=server -f wizardrun.yaml        # save the manifest below first
kubectl create -f wizardrun.yaml
kubectl get wizardruns -n fusion -w                     # phase until Ready
```

```yaml
apiVersion: wizard.fusion-platform.io/v1alpha1
kind: WizardRun
metadata:
  name: wizard-single
  namespace: fusion
spec:
  definitionRef:
    name: python-git-job
  parameters:
    jobName: wizard-single
    repoUrl: https://<your-git-host>/<org>/<repo>.git
    repoRef: main
    projectDir: v3-beta/template-wizard-job-single-entrypoint
    entrypoints:                    # objectList: key = file, type = OnDemand | Cron
      - key: main.py
        type: OnDemand
        schedule: ""                # Cron only; weave uses 6 fields, seconds first (0 */5 * * * *)
    externalAuthMode: serviceAccount          # optional, together with the name
    externalAuthName: ext-auth-demo-sa        # must be on the operator's allowlist
```

## Fire and read the result

```bash
kubectl get weavetriggers -n fusion | grep wizard-single     # one trigger: wizard-single-main
kubectl annotate weavetrigger wizard-single-main fusion-platform.io/fire=true --overwrite -n fusion
kubectl get fr -n fusion -w
kubectl logs -n fusion -l fusion-platform.io/chain=wizard-single
```

Expected: `excerpt: 730 words, 403 distinct, 4.8 kB`, a top-5 table (`er`, `die`, `und`, `der`, `zu`),
and with external auth: `token: read from file WEAVE_EXTERNAL_AUTH_TOKEN_FILE, N chars, masked` plus
`sub system:serviceaccount:fusion:ext-auth-demo-sa`.

## Roll back

Set `spec.desiredState: RolledBack` on the `WizardRun` (or delete it via the wizard API) — the wizard
removes what it created, ref-counted through its ledger. A rolled-back run is terminal; create a new one.

## Notes

- Every resource the wizard creates carries the labels `fusion-platform.io/managed-by: wizard` and `wizard.fusion-platform.io/run: <run>`.
- The wizard step `waitBuild` matches the build by repository URL **and** project directory.
- Run it only against a repository/directory that nothing else uses: rolling back deletes the artifact the run created.
- `rootAssets` builds log `copied 3 root asset file(s) into package _root_assets`.
