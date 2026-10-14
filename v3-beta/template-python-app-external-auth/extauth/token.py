"""Reading the token that fusion injects via `externalAuthRef`.

What `externalAuthRef` does
---------------------------
You name an identity on the chain (`mode: serviceAccount` or `mode: oidc`, plus a
`name` the operator has allowlisted). For every job pod of a Job-kind step the
operator then mints a SHORT-LIVED token and hands it over. The long-lived
credential behind it (ServiceAccount rights, Keycloak client secret) never enters
your container - your code only ever sees the token.

How the token arrives (two ways, same value)
--------------------------------------------
1. FILE  (always, preferred)   path in the env var WEAVE_EXTERNAL_AUTH_TOKEN_FILE,
                               which is /var/run/secrets/fusion-platform.io/external-auth/token
2. ENV   (second option)       WEAVE_EXTERNAL_AUTH_TOKEN - only while the chain's
                               `unsafeEnvironmentInjector` is true (the default)

Always set next to it (not secret):
   WEAVE_EXTERNAL_AUTH_MODE   serviceAccount | oidc
   WEAVE_EXTERNAL_AUTH_NAME   the allowlisted name from the chain

Why file first?
---------------
An env var is inherited by child processes and shows up in crash dumps and debug
output; a file is read exactly where needed. The file is also the only variant that
exists when `unsafeEnvironmentInjector: false`. The env variant is the fallback for
legacy code that can only read the environment.

Lifetime
--------
The token is short-lived (Helm `externalAuth.defaultTokenTTL`, default 5m, for
serviceAccount mode; the Keycloak client's access token lifespan for oidc mode)
and is minted fresh for every job-creation attempt, so a retry gets a new one.
Read it when you need it and do not cache it beyond the job.
"""
import base64
import json
import os

TOKEN_FILE_VAR = "WEAVE_EXTERNAL_AUTH_TOKEN_FILE"
TOKEN_ENV_VAR = "WEAVE_EXTERNAL_AUTH_TOKEN"
MODE_VAR = "WEAVE_EXTERNAL_AUTH_MODE"
NAME_VAR = "WEAVE_EXTERNAL_AUTH_NAME"


def read_token_from_file() -> str | None:
    """Way 1 (preferred): the mounted token file. None when externalAuthRef is not set."""
    path = os.environ.get(TOKEN_FILE_VAR)
    if not path or not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


def read_token_from_env() -> str | None:
    """Way 2 (second option): the env var. None when the env injector is switched off."""
    return os.environ.get(TOKEN_ENV_VAR) or None


def read_token() -> tuple[str, str] | None:
    """The pattern for application code: file first, env as fallback.

    Returns (token, source) with source "file" or "env", or None if neither exists.
    """
    token = read_token_from_file()
    if token:
        return token, "file"
    token = read_token_from_env()
    if token:
        return token, "env"
    return None


def auth_header(token: str) -> dict[str, str]:
    """How you would present the token to the service it was minted for.
    This template does not call any service - it only shows the header."""
    return {"Authorization": f"Bearer {token}"}


def claims(token: str) -> dict:
    """Decode the (public) payload of a JWT WITHOUT verifying it, only to show
    who the token is for. Both modes produce JWTs. Never trust unverified claims
    for security decisions - the receiving service verifies the signature."""
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)  # restore base64 padding
        return json.loads(base64.urlsafe_b64decode(payload))
    except (IndexError, ValueError):
        return {}
