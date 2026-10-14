# template-python-venv

The simplest fusion example: **a single `requirements.txt`**.

When you submit it to fusion-forge (via Spectra), the forge builds a Python 3.12
virtual environment from it, packs that venv and uploads it to fusion-index as a
`venv.<name>` artifact. Later steps (jobs, apps) can reference that venv to get
exactly these packages at runtime.

There is no code in this example — only the dependency list. It shows the
`requirements.txt` rules and the result of a build, nothing else.

## Contents

| File | Purpose |
|---|---|
| `requirements.txt` | Three small, pinned packages (`requests`, `python-dateutil`, `tqdm`), commented in-line |
| `README_technical.md` | API/curl commands for the same flow (for developers and ops) |

## Rules for `requirements.txt`

The forge validates the file line by line before it builds anything. A violation
rejects the whole submission and tells you the line and the reason.

**Always enforced**

- One requirement per line: `package==version`.
- A version specifier is mandatory — a bare `requests` is rejected.
- Package names must follow PEP 508 (letters, digits, `-`, `_`, `.`; must start and end with a letter or digit).
- No pip options: `-r other.txt`, `-e .`, `--index-url ...` and any other line starting with `-` are rejected.
- No VCS or URL dependencies: `git+https://...`, `https://...whl` and similar are rejected.
- Blank lines and `# comments` (full-line or trailing) are fine.

**Configurable by the forge operator** (defaults shown)

- **Exact pinning: on.** Only `==` is accepted; `>=`, `~=`, `<` etc. are rejected. If switched off, any version operator is accepted, but a specifier is still required.
- **Banned packages: none.** The operator can block package names (case-insensitive; `-`, `_` and `.` are treated as the same).
- **Maximum packages: 100.** More entries than that are rejected.

**Good practice**

- List direct dependencies only; pip resolves the transitive ones during the build.
- Pin everything, so two builds of the same version contain the same packages.
- Everything must be installable from the package index the forge uses — private or local packages are not supported in this shape.

## How to use it as a template

1. Copy this directory, e.g. `cp -r template-python-venv my-venv`.
2. Replace the three packages in `requirements.txt` with your own, keeping every one pinned.
3. In Spectra, open the venv build form, choose a **name** and **version**, upload your `requirements.txt` and submit.
4. When the build finishes, the artifact `venv.<name>` at that version is available in fusion-index.

The name and version are entered at submit time — they are not read from the file.

For the same flow through the API (validate, submit, status, logs), see
[README_technical.md](README_technical.md).
