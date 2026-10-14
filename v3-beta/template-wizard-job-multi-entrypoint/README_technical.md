# template-wizard-job-multi-entrypoint — technical notes

The wizard flow of [README.md](README.md) as kubectl. The wizard definition is `python-git-job`
(`fusion-wizard`, chart `definitions/python-git-job.yaml`).

## Start a wizard run

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
  name: wizard-multi
  namespace: fusion
spec:
  definitionRef:
    name: python-git-job
  parameters:
    jobName: wizard-multi
    repoUrl: https://<your-git-host>/<org>/<repo>.git
    repoRef: main
    projectDir: v3-beta/template-wizard-job-multi-entrypoint
    entrypoints:                    # one trigger per entry; types may be mixed
      - key: count.py
        type: OnDemand
        schedule: ""
      - key: top.py
        type: OnDemand
        schedule: ""
      - key: longest.py
        type: OnDemand              # or: type: Cron, schedule: "0 */5 * * * *" (6 fields, seconds first)
        schedule: ""
```

## Fire and read the result

```bash
kubectl get weavetriggers -n fusion | grep wizard-multi      # wizard-multi-count, -top, -longest
for t in count top longest; do
  kubectl annotate weavetrigger wizard-multi-$t fusion-platform.io/fire=true --overwrite -n fusion
done
kubectl get fr -n fusion -w
kubectl logs -n fusion -l fusion-platform.io/chain=wizard-multi --tail=20
```

Expected: `count: 730 words, 403 distinct, 4.8 kB`, a top-5 table (`er`, `die`, `und`, `der`, `zu`) and
`longest words: auseinandergepackte, möbelerschütternde, musterkollektion`.

## Roll back

Set `spec.desiredState: RolledBack` on the `WizardRun`; the wizard removes what it created, ref-counted
through its ledger. A rolled-back run is terminal; create a new one.

## Notes

- Trigger names are `<jobName>-<entrypoint stem>`; the trigger sets `ENTRYPOINT` through `parameterOverrides`.
- `metadata.yaml` has `files: []` (builder log: `auto-discovered 3 python file(s)`) and `rootAssets: true` (`copied 3 root asset file(s)`: the excerpt and the two READMEs).
- Run it only against a repository/directory that nothing else uses: rolling back deletes the artifact the run created.
