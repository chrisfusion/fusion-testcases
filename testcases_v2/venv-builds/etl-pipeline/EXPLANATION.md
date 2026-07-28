# Five scripts, one package

How the `etl-pipeline` chain runs five different jobs from a single build.
Explained twice — once for whoever owns the scripts, once for whoever owns
the Kubernetes plumbing. Both descriptions point at the same run, fired for
real on minikube on 2026-07-28.

```
extract.py ─┬─> transform_customers.py ─┬─> merge.py ─> load.py
            └─> transform_orders.py ────┘
```

One shared package, five entry points. `extract` runs once; the two
transform steps run at the same time; `merge` waits for both; `load` runs
last. Real timestamps from the successful run: `23:38:36 → 23:38:40 /
23:38:40 → 23:38:44 → 23:38:49 UTC`.

## For a data analyst

Say your team keeps five Python scripts in one repository — `extract.py`,
two transform scripts, a merge script, a load script. They all import the
same handful of libraries, so really there's only one `requirements.txt`
for the whole folder.

Normally that leaves you with two bad options: run all five scripts
yourself, in order, on your laptop (slow — and the two transform scripts
don't actually depend on each other, so making them wait is wasted time);
or ask an engineer to package each script as its own separate deployable
thing, just to run five scripts that share one codebase.

**What we did instead:** think of it like zipping the whole scripts folder
once and handing that single zip file to five different runners. Each
runner unpacks the exact same zip, but is told which one script inside to
execute — five people sharing one toolbox, each reaching for a different
tool. In the system's own words: that zip file is an *artifact*, and the
"which script" instruction is its *entry point*.

The scripts themselves don't need to do anything special to cooperate with
each other — in this example they just print which step they are. Nothing
about "run these two at the same time" is hardcoded in Python; it's
declared once, outside the code, as a dependency graph.

And that graph is enforced for real, every time: in the run above, the two
transform steps both started in the same second, automatically, because
nothing told the system they had to wait for each other. You don't
schedule that — you say "merge depends on both transforms," once, and it's
handled the same way on every future run.

**Adding a sixth script:** dropping a new script — say `dedupe.py` — into
the same repository needs no new packaging and no new container image; it
rides along the next time the shared package is rebuilt. Wiring it into
the running order is still a short, explicit edit (a few lines saying what
it depends on) — small enough that it's not a new build, but it is a real
edit someone has to make on purpose, not something that happens
automatically just because the file exists.

Net effect: one build serves five jobs instead of five separate ones, and
the two independent steps finish in parallel instead of back to back.

## For an engineer

One `WeaveJobTemplate` (`etl-pipeline`) carries a single `codeSource`
pointing at `venv.etl-pipeline@stable` in fusion-index. All five
`WeaveChainStep` entries in the `etl-pipeline` `WeaveChain` reference that
one template; the only thing that differs per step is an `ENTRYPOINT` env
override. The DAG shape — including which steps run concurrently — is
declared once via `dependsOn` and resolved by the operator's
`dag.Advance`; nothing about ordering lives in application code.

Build and publish, concretely: `POST /api/v1/venvs` against fusion-forge
created `CIBuild forge-venv-77`, which ran a real build pod and uploaded
the resulting venv archive to fusion-index as artifact `venv.etl-pipeline`
(id `1601`), version `1.0.0` (`versionId 4701`). The five scripts were
uploaded separately, straight to fusion-index, as extra files on that same
version — fusion-forge's git-build entrypoint upload only supports one
file per version, so this shape (multiple raw scripts sharing a venv) is
published out of band. The `stable` tag was then moved to `1.0.0` via a
`PUT` carrying both `version` and `versionId`, which fusion-index requires
together.

### Gotcha 1 · avoided at design time — metadata-driven ENTRYPOINT would have silently won

In `jobbuilder.Build`, `mergeEnv(template.Spec.Env, step.EnvOverrides,
run.Spec.ParameterOverrides)` correctly dedupes by key, step wins over
template. But `codesource.EnvVars(...)` — which is where `runner.args`
from a `metadata.yaml` would inject its own `ENTRYPOINT` — is appended to
the env slice *after* that merge, unmerged. Kubernetes resolves duplicate
env-var names in a pod spec last-value-wins at the container runtime, so a
metadata-supplied `ENTRYPOINT` would beat every step's override, every
time.

Fix: publish this artifact as a plain venv build with no `metadata.yaml`
at all. With `csMeta == nil`, `codesource.EnvVars` never emits a
`runner.args`-derived key, so there's nothing to collide with the per-step
override.

### Gotcha 2 · hit on the first live fire — no metadata meant no runner type either

First run (`etl-pipeline-trigger-5x8jl`) landed `Stopped`: `extract`'s
container exited 1 with `unsupported runner type "" (set via
WEAVE_RUNNER_TYPE)`. `WEAVE_RUNNER_TYPE` is only auto-injected from
`meta.Runner.Type` — and per Gotcha 1, this artifact deliberately carries
no metadata, so it's never set.

Fix: added `WEAVE_RUNNER_TYPE: python` as a static entry on
`WeaveJobTemplateSpec.Env`. It's template-level, not codeSource-derived,
so it flows through the normal `mergeEnv` path with no collision risk.
Re-fired as `etl-pipeline-trigger-9lw4f` — succeeded.

### Measured, not asserted

The concurrency in the diagram above isn't declared as a claim, it's
measured — start times pulled from `kubectl logs` on the successful run:

| Step                | Entry point             | Started (UTC) |
|----------------------|--------------------------|---------------|
| extract              | extract.py               | 23:38:36      |
| transform-customers   | transform_customers.py   | 23:38:40      |
| transform-orders      | transform_orders.py      | 23:38:40      |
| merge                 | merge.py                 | 23:38:44      |
| load                  | load.py                  | 23:38:49      |

Known loose end, not chased down: the container prints `WEAVE_VERSION` as
an empty string even though the code-loader correctly resolved and
downloaded `1.0.0` — some version-string plumbing isn't populated on this
metadata-less codeSource path. Doesn't affect entry-point selection, just
cosmetic.

## Receipts

| | |
|---|---|
| WeaveChain / Template / Trigger | `etl-pipeline` / `etl-pipeline` / `etl-pipeline-trigger` |
| fusion-index artifact | `venv.etl-pipeline` (id 1601) |
| Version | `1.0.0` (versionId 4701) — 6 files, tag: `stable` |
| Build | `forge-venv-77` (CIBuild, requirements) |
| Runs | `etl-pipeline-trigger-5x8jl` → Stopped (fixed) · `etl-pipeline-trigger-9lw4f` → Succeeded |
| Source | `testcases_v2/venv-builds/etl-pipeline/chain.yaml` |

Built and fired on minikube, namespace `fusion`, 2026-07-28.
