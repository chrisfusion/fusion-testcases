"""Reading the short-lived token that fusion injects BY FILE.

In the wizard form you set `externalAuthMode` (serviceAccount | oidc) and
`externalAuthName` (an identity the operator has allowlisted). The chain then carries
`externalAuthRef`, and for every job pod the operator mints a fresh short-lived token
and mounts it as a FILE. The long-lived credential behind it never reaches this code.

  WEAVE_EXTERNAL_AUTH_TOKEN_FILE   path of the token file
                                   (/var/run/secrets/fusion-platform.io/external-auth/token)
  WEAVE_EXTERNAL_AUTH_MODE / _NAME  which identity it was minted for (not secret)

The same token is also offered as the env var WEAVE_EXTERNAL_AUTH_TOKEN (unless the
env injector is switched off). This job deliberately uses only the file: it is the
variant that always exists, is not inherited by child processes and does not show up
in crash dumps. See ../template-python-app-external-auth for both variants side by side.
"""
import base64
import json
import os

TOKEN_FILE_VAR = "WEAVE_EXTERNAL_AUTH_TOKEN_FILE"


def read_token() -> str | None:
    """The token, or None when the wizard run configured no external auth."""
    path = os.environ.get(TOKEN_FILE_VAR)
    if not path or not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


def claims(token: str) -> dict:
    """Public JWT payload, decoded WITHOUT verification, only to show who the token is for.
    The service that receives the token verifies the signature - never trust these yourself."""
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload))
    except (IndexError, ValueError):
        return {}
