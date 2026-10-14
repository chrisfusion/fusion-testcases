"""All the ways fusion injects variables, secrets and tokens into a job container.

Each function below covers ONE mechanism and returns rows of
(way, name, where, value). The settings that switch each way on are described in README.md.

Overview
--------
Environment variables (visible to every process, also to child processes and
often to crash dumps -> use for NON-secret configuration):

  1. metadata.yaml  runner.args            plain env vars, baked into the artifact
  2. WeaveJobTemplate  spec.env            static env vars; also valueFrom a Secret/ConfigMap key
  3. WeaveChain step   envOverrides        per-step env vars; also valueFrom a Secret/ConfigMap key
  4. codeSource        WEAVE_*             automatic: artifact name, tag, version, ...
  5. BatchCron         JOB_*               automatic: only when started by a BatchCron trigger

Secrets and tokens, as FILE and/or as ENV (prefer the file, see "Env vs. file"):

  6. WeaveChain authSecretRef              a whole Secret: one FILE per key in
                                           WEAVE_AUTH_SECRET_DIR (always) and one ENV var
                                           per key (only while unsafeEnvironmentInjector
                                           is true, the default)
  7. WeaveChain externalAuthRef            a short-lived token minted by the operator:
                                           FILE named in WEAVE_EXTERNAL_AUTH_TOKEN_FILE
                                           (always) and ENV WEAVE_EXTERNAL_AUTH_TOKEN
                                           (only while unsafeEnvironmentInjector is true)
  8. WeaveJobTemplate volumes              any Secret or ConfigMap mounted as files at a
                                           path of your choice

Env vs. file
------------
The file mounts are always there. The env variants are the "unsafe environment
injector": set `unsafeEnvironmentInjector: false` on the chain (or its trigger/run
override) to switch them off, and then only the file variants exist. Code that
reads files works in both setups, so write it file-first and fall back to env.

Precedence when a name appears twice
------------------------------------
Container env is built in this order: template `env`, step `envOverrides`, then
codeSource variables including `runner.args`. With duplicates the LAST one wins
at runtime. Hence a `runner.args` key can never be overridden per step.
"""
import os

Row = tuple[str, str, str, str]

AUTH_SECRET_DIR_VAR = "WEAVE_AUTH_SECRET_DIR"
EXTERNAL_TOKEN_FILE_VAR = "WEAVE_EXTERNAL_AUTH_TOKEN_FILE"
EXTERNAL_TOKEN_ENV_VAR = "WEAVE_EXTERNAL_AUTH_TOKEN"

# Where the job template mounts the Secret of way 8 (WeaveJobTemplate.spec.volumes).
CUSTOM_MOUNT_DIR = "/etc/app-secrets"

NOT_SET = "<not set>"


def mask(value: str) -> str:
    """Never print secret values, not even into a job log. Length is enough to
    prove that the injection worked."""
    return f"<{len(value)} chars, masked>"


def _env_row(way: str, name: str, secret: bool = False) -> Row:
    """Read one env var; mask it when it is a secret."""
    value = os.environ.get(name)
    if value is None:
        return (way, name, "env", NOT_SET)
    return (way, name, "env", mask(value) if secret else value)


def _file_rows(way: str, directory: str) -> list[Row]:
    """One row per file in a directory (a mounted Secret/ConfigMap has one file per key)."""
    if not os.path.isdir(directory):
        return [(way, directory, "dir", NOT_SET)]
    rows = []
    for name in sorted(os.listdir(directory)):
        path = os.path.join(directory, name)
        # Secret volumes contain hidden ..data symlinks; only look at real keys.
        if name.startswith(".") or not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as f:
            rows.append((way, path, "file", mask(f.read().strip())))
    return rows


def from_runner_args() -> list[Row]:
    """Way 1 - metadata.yaml `runner.args`. Plain env var, not secret."""
    return [_env_row("1 runner.args", "GREETING")]


def from_template_env() -> list[Row]:
    """Way 2 - WeaveJobTemplate `spec.env`. LOG_LEVEL is a static value, DB_HOST comes
    from a ConfigMap key and DB_PASSWORD from a Secret key (valueFrom). The code
    cannot tell the difference - to the process they are all plain env vars."""
    way = "2 template env"
    return [
        _env_row(way, "LOG_LEVEL"),
        _env_row(way, "DB_HOST"),
        _env_row(way, "DB_PASSWORD", secret=True),
    ]


def from_step_env_overrides() -> list[Row]:
    """Way 3 - WeaveChain step `envOverrides`. Same shape as `spec.env`, but per
    step: one template can be reused by several steps with different values."""
    return [_env_row("3 step envOverrides", "STEP_NOTE")]


def from_code_source() -> list[Row]:
    """Way 4 - set automatically for every step with a codeSource (our artifact)."""
    way = "4 codeSource"
    return [_env_row(way, n) for n in ("WEAVE_ARTIFACT", "WEAVE_TAG", "WEAVE_VERSION")]


def from_batch_cron() -> list[Row]:
    """Way 5 - set automatically when the run was started by a BatchCron trigger."""
    way = "5 BatchCron"
    return [_env_row(way, n) for n in ("JOB_ID", "JOB_NAME", "JOB_SCHEDULE")]


def from_auth_secret() -> list[Row]:
    """Way 6 - chain `authSecretRef`: the same Secret, twice.

    FILE: WEAVE_AUTH_SECRET_DIR points to a directory with one file per Secret key.
          Always present. Preferred: the value is not inherited by child
          processes and not listed in `kubectl describe`/crash dumps.
    ENV:  every Secret key is also an env var, but only while
          unsafeEnvironmentInjector is true (default).
    """
    way = "6 authSecretRef"
    rows = [_env_row(way, "API_KEY", secret=True)]
    secret_dir = os.environ.get(AUTH_SECRET_DIR_VAR)
    if secret_dir is None:
        return rows + [(way, AUTH_SECRET_DIR_VAR, "env", NOT_SET)]
    return rows + _file_rows(way, secret_dir)


def read_api_key() -> str | None:
    """The recommended pattern for application code: file first, env as fallback."""
    secret_dir = os.environ.get(AUTH_SECRET_DIR_VAR)
    if secret_dir:
        path = os.path.join(secret_dir, "API_KEY")
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                return f.read().strip()
    return os.environ.get("API_KEY")


def from_external_auth() -> list[Row]:
    """Way 7 - chain `externalAuthRef`: a short-lived token minted by the operator.

    Only for Job-kind steps. The credential behind it (ServiceAccount rights or a
    Keycloak client secret) never reaches the container, only the token does.
    FILE: path in WEAVE_EXTERNAL_AUTH_TOKEN_FILE, always present when configured.
    ENV:  WEAVE_EXTERNAL_AUTH_TOKEN, only while unsafeEnvironmentInjector is true.
    Also set: WEAVE_EXTERNAL_AUTH_MODE (serviceAccount|oidc), WEAVE_EXTERNAL_AUTH_NAME.
    """
    way = "7 externalAuthRef"
    rows = [_env_row(way, "WEAVE_EXTERNAL_AUTH_MODE"), _env_row(way, EXTERNAL_TOKEN_ENV_VAR, secret=True)]
    token_file = os.environ.get(EXTERNAL_TOKEN_FILE_VAR)
    if token_file is None:
        return rows + [(way, EXTERNAL_TOKEN_FILE_VAR, "env", NOT_SET)]
    with open(token_file, encoding="utf-8") as f:
        return rows + [(way, token_file, "file", mask(f.read().strip()))]


def from_mounted_volume() -> list[Row]:
    """Way 8 - WeaveJobTemplate `volumes`: any Secret or ConfigMap as files at a
    path you choose (here /etc/app-secrets). Use it for certificates, key files
    and config files that a library expects at a fixed path."""
    return _file_rows("8 template volumes", CUSTOM_MOUNT_DIR)


ALL_WAYS = (
    from_runner_args,
    from_template_env,
    from_step_env_overrides,
    from_code_source,
    from_batch_cron,
    from_auth_secret,
    from_external_auth,
    from_mounted_volume,
)
