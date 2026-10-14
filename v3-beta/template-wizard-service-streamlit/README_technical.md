# template-wizard-service-streamlit — technical notes

The wizard flow of [README.md](README.md) as kubectl. The wizard definition is `python-git-service`
(`fusion-wizard`, chart `definitions/python-git-service.yaml`).

## Start a wizard run

```bash
kubectl get wizarddefinitions -n fusion                 # python-git-service must exist
kubectl apply --dry-run=server -f wizardrun.yaml        # save the manifest below first
kubectl create -f wizardrun.yaml
kubectl get wizardruns -n fusion -w                     # phase until Ready
```

```yaml
apiVersion: wizard.fusion-platform.io/v1alpha1
kind: WizardRun
metadata:
  name: wizard-words
  namespace: fusion
spec:
  definitionRef:
    name: python-git-service
  parameters:
    serviceName: wizard-words
    repoUrl: https://<your-git-host>/<org>/<repo>.git
    repoRef: main
    projectDir: v3-beta/template-wizard-service-streamlit
    port: 8501                      # must equal runner.port in metadata.yaml
    ingressName: ""                 # optional hostname label, e.g. words -> words.<hostSuffix>
```

## Open the app

```bash
kubectl get pods,svc -n fusion | grep wizard-words        # wait for the pod to be Ready
kubectl port-forward -n fusion svc/wizard-words-run 8501:8501    # then open http://localhost:8501
```

The Deployment and Service are named `<serviceName>-run` (the wizard's chain has one deploy step called `run`).
The trigger is fired by the wizard itself (`fireOnCreate`); nothing to annotate. With an `ingressName` the app is
also reachable at `https://<ingressName>.<ingress.hostSuffix>` (needs DNS/hosts entry and, on a TLS-enabled
cluster, a certificate).

## Roll back

Set `spec.desiredState: RolledBack` on the `WizardRun`; the wizard removes what it created (trigger, chain, service
template, watcher), ref-counted through its ledger, and the Deployment goes with the chain. A rolled-back run is
terminal; create a new one.

## Notes

- Every resource the wizard creates carries the labels `fusion-platform.io/managed-by: wizard` and `wizard.fusion-platform.io/run: <run>`.
- The wizard step `waitBuild` matches the build by repository URL **and** project directory.
- The service template's ports come from the form (`port`); the artifact's `runner.port` is only exported as `WEAVE_PORT` for chain-owned deploy steps, which makes the runner start Streamlit on it. Different values break the service.
- fusion-runner (`streamlit` type) runs `python -m streamlit run <mountPath>/$ENTRYPOINT` headless on `0.0.0.0`.
- `rootAssets` builds log `copied 3 root asset file(s) into package _root_assets` (the excerpt and the two READMEs).

## Local run

```bash
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
# the root asset package only exists after a forge build; simulate it:
SP=$(.venv/bin/python -c 'import site;print(site.getsitepackages()[0])')
mkdir $SP/_root_assets && touch $SP/_root_assets/__init__.py && cp kafka_excerpt.txt $SP/_root_assets/
PYTHONPATH=. .venv/bin/python -m streamlit run main.py
```
