# template-python-venv — technical notes

API-level version of the flow described in [README.md](README.md). Spectra users
normally do not need this.

## Prerequisite

Port-forward the forge (keep running in a separate terminal):

```bash
kubectl port-forward -n fusion service/fusion-forge 18080:8080 --address 127.0.0.1
curl http://localhost:18080/q/health/ready
```

## Validate without building

```bash
curl -X POST http://localhost:18080/api/v1/venvs/validate \
  -F name=my-venv -F version=1.0.0 -F requirements=@requirements.txt
```

Runs the same line-by-line checks as a real submit (see the rules in the README)
and reports violations with line number and reason. Nothing is built.

## Submit a build

```bash
curl -X POST http://localhost:18080/api/v1/venvs \
  -F name=my-venv -F version=1.0.0 -F requirements=@requirements.txt
```

Multipart form fields: `name`, `version`, `requirements` (the file).
The result is the artifact `venv.my-venv` at version `1.0.0` in fusion-index.

## Status and logs

```bash
curl http://localhost:18080/api/v1/venvs                # list builds
curl http://localhost:18080/api/v1/venvs/<id>           # status (lazily syncs the CR)
curl http://localhost:18080/api/v1/venvs/<id>/logs      # builder pod logs
```

## Where the validation rules live

In fusion-forge: `internal/validation/validator.go` (always-on rules) and
`internal/validation/forge-rules.yaml` (operator-configurable: `require-exact-pinning`,
`banned-packages`, `max-packages`). The full curl set (error cases, filtering) is in
`fusion-forge/EXAMPLES.md`.
