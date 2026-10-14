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

## The batch wizards

Same repository, other definitions. Both were run on minikube with this directory.

**`batch-git-job`** — one trigger, fired once right after creation (`fireOnCreate`):

```yaml
apiVersion: wizard.fusion-platform.io/v1alpha1
kind: WizardRun
metadata:
  name: bg-single
  namespace: fusion
spec:
  definitionRef:
    name: batch-git-job
  parameters:
    jobName: bg-single
    repoUrl: https://<your-git-host>/<org>/<repo>.git
    repoRef: main
    projectDir: v3-beta/template-wizard-job-single-entrypoint
    triggerType: OnDemand           # or Cron, together with `schedule` (6 fields, seconds first)
    externalAuthMode: serviceAccount
    externalAuthName: ext-auth-demo-sa
```

The run `bg-single-<id>` appears without any manual fire and succeeds; its log shows the report and the token facts.

With `triggerType: Cron` and `schedule: "0 * * * * *"` (every minute; **6 fields, seconds first**) it was tested too: one run
started immediately on creation and further runs followed on each cron match, all with the same report and token. A Cron
trigger keeps firing until the wizard run is rolled back.

**`batchcron-git-job`** — one BatchCron trigger with a list of jobs (5-field cron, no seconds):

```yaml
apiVersion: wizard.fusion-platform.io/v1alpha1
kind: WizardRun
metadata:
  name: bc-single
  namespace: fusion
spec:
  definitionRef:
    name: batchcron-git-job
  parameters:
    jobName: bc-single
    repoUrl: https://<your-git-host>/<org>/<repo>.git
    repoRef: main
    projectDir: v3-beta/template-wizard-job-single-entrypoint
    jobs: '[{"job":{"id":"every-minute","name":"Every minute","schedule":"* * * * *","topic":"demo","maintainer":"some.maintainer@example.local","metadata":{"region":"eu-west"}}}]'
    externalAuthMode: serviceAccount          # chain level only for this wizard
    externalAuthName: ext-auth-demo-sa
```

Runs are named `bc-single-<job id>-<suffix>` and appear on every cron match. **Roll this one back when you are
done** (below), otherwise it keeps firing. Rolling it back removed its trigger, chain, watcher and finished runs
and left the shared artifact and the other wizard runs untouched.

## Roll back

Set `spec.desiredState: RolledBack` on the `WizardRun` (or delete it via the wizard API) — the wizard
removes what it created, ref-counted through its ledger. A rolled-back run is terminal; create a new one.

## Notes

- Every resource the wizard creates carries the labels `fusion-platform.io/managed-by: wizard` and `wizard.fusion-platform.io/run: <run>`.
- The wizard step `waitBuild` matches the build by repository URL **and** project directory.
- Run it only against a repository/directory that nothing else uses: rolling back deletes the artifact the run created.
- `rootAssets` builds log `copied 3 root asset file(s) into package _root_assets`.
