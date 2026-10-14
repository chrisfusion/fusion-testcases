# template-python-app-etl-shared-storage

A small **ETL pipeline from one build**: a single venv pack with three entrypoints that
hand their results to each other through fusion's **shared storage**, ending in a Streamlit
dashboard. The data is Franz Kafka's *Die Verwandlung* (Project Gutenberg #22367, public domain).

```
 extract.py ──────────▶ count.py ──────────▶ dashboard.py
 raw ebook → clean.txt   clean.txt → wordcount.csv   wordcount.csv → charts
 (job)                   (job)                       (web app, stays running)
        └──────────── /weave-shared (one volume per run) ────────────┘
```

| Process | Entrypoint | Does | Writes / reads |
|---|---|---|---|
| 1 extract | `extract.py` | reads the raw ebook (an asset), cuts the Gutenberg licence header/footer and the title page, drops chapter numbers and punctuation noise | writes `clean.txt` |
| 2 count | `count.py` | counts every word (umlauts and ß included) | reads `clean.txt`, writes `wordcount.csv` (`word,count`, most frequent first) |
| 3 dashboard | `dashboard.py` | top words, word-length distribution, searchable table of all words | reads `wordcount.csv` |

**No internet at runtime.** The ebook was downloaded once and is committed as
`assets/die_verwandlung.txt`; the pipeline only reads that file. This is what makes the
example work in an environment without internet access.

## One build, three kinds of process

This is a combination of earlier templates:

- **Multi-entrypoint** ([`template-python-app-multi-entrypoint`](../template-python-app-multi-entrypoint/README.md)): `files: []` uploads every top-level script. Shared code lives in a package (`kafka_etl/`), because scripts cannot import each other.
- **Assets package** ([`template-python-app-assets-dir`](../template-python-app-assets-dir/README.md)): the ebook lives in `assets/`.
- **Streamlit** ([`template-python-app-streamlit`](../template-python-app-streamlit/README.md)): the dashboard.

New here is that the pack serves **two runner types**: the first two steps are batch jobs
(`python`), the third is a web app (`streamlit`). Therefore:

- `metadata.yaml` has **no `runner:` block**. Whatever the metadata sets is applied last and wins, so a fixed `runner.type` or `ENTRYPOINT` there would break one of the two kinds.
- Each step sets its own `WEAVE_RUNNER_TYPE` and `ENTRYPOINT`: jobs via the job template and a step override, the dashboard via the service template.

## Shared storage

The chain declares `sharedStorage` (here 100Mi). For every run fusion creates **one volume**
and mounts it at **`/weave-shared`** into the steps of that run, so `extract` can write a file
and `count` finds it there. Things to know:

- **The volume belongs to the run.** It is created with the run and deleted with it. A new run starts with an empty volume.
- **Job steps always get it.** Deploy steps only if they are **run-owned**.
- **Chain-owned Deploy steps do not get it.** Their Deployment outlives the run and its volume. Only a deploy step that the *run* brings along (a `stepOverrides` entry) is mounted, so the dashboard here is run-owned.
- **Consequence:** the pipeline is started by creating a **run** that carries the dashboard override (`artifactName`, `tag`, optionally `ingressName`), not by a plain trigger. The dashboard stays up as long as the run exists; deleting the run removes the dashboard and the volume.
- The storage class must support `ReadWriteMany` (several pods at the same time).

### Volume permissions

A new volume is owned by root, but the runner image runs as an unprivileged user (uid/gid 1000), which
then cannot write: `Permission denied: '/weave-shared/clean.txt'`. Fix it with the pod setting
**`fsGroup: 1000`** (Kubernetes then makes the volume group-writable on mount). Set it on the job template
and the service template as the manifests do, or once for the whole cluster in the operator's workload
security defaults. The storage driver must honour `fsGroup`. Note that a template-level pod security
context replaces the operator-wide default entirely, so repeat any settings you need from it.

## Settings in Spectra

| Where | Setting |
|---|---|
| Chain | shared storage: size `100Mi`, storage class with ReadWriteMany |
| Step `extract` (Job) | code source `app.template-python-app-etl-shared-storage` tag `stable`; environment `WEAVE_RUNNER_TYPE=python`, `ENTRYPOINT=extract.py` |
| Step `count` (Job) | depends on `extract`; same, with `ENTRYPOINT=count.py` |
| Step `dashboard` (Deploy) | depends on `count`; service template with port 8501 and environment `WEAVE_RUNNER_TYPE=streamlit`, `ENTRYPOINT=dashboard.py`, `WEAVE_PORT=8501` |
| Run | deploy override for `dashboard`: artifact `app.template-python-app-etl-shared-storage`, tag `stable` (and an ingress name for a hostname) |

kubectl users find the same settings as manifests in
[README_technical.md](README_technical.md#reference-manifests).

## Contents

| File | Purpose |
|---|---|
| `metadata.yaml` | App build settings: `files: []`, no runner block |
| `requirements.txt` | Pinned dependencies (`streamlit`, `pandas`), rules as in [`../template-python-venv`](../template-python-venv/README.md) |
| `extract.py`, `count.py`, `dashboard.py` | The three entrypoints, thin scripts |
| `kafka_etl/` | Shared code: `paths.py` (where the files are), `cleaning.py`, `counting.py` |
| `assets/` | Package holding the raw ebook `die_verwandlung.txt` |
| `README_technical.md` | Build, run and test commands, reference manifests |

## How to use it as a template

1. Copy this directory, e.g. `cp -r template-python-app-etl-shared-storage my-etl`.
2. Set your own `name`, `version`, `maintainer` in `metadata.yaml`.
3. Replace the ebook in `assets/` and the logic in `kafka_etl/`; keep the file names in `paths.py` as the contract between the steps.
4. Add or rename steps by adding a script and a chain step with its `ENTRYPOINT`.
5. Build through Spectra, then start a run with the dashboard override.

## Source of the text

*Die Verwandlung* by Franz Kafka, Project Gutenberg eBook #22367
(<https://www.gutenberg.org/ebooks/22367>), included unmodified with its Project Gutenberg
licence header. The text is in the public domain.
