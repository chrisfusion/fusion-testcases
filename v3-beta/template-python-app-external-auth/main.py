"""Entrypoint (metadata.yaml: runner.args.ENTRYPOINT = main.py).

Shows the token fusion injects through the chain's `externalAuthRef`: where it
arrived (file and/or env), who it is for, and when it expires. The token itself is
never printed - only its length. The explanation of the mechanism is in
`extauth/token.py`; the chain settings that switch it on are described in README.md.
"""
import os
import time

import humanize
from tabulate import tabulate

from extauth import token as ext


def main() -> None:
    from_file = ext.read_token_from_file()
    from_env = ext.read_token_from_env()

    rows = [
        ["mode", ext.MODE_VAR, "env", _env(ext.MODE_VAR)],
        ["name", ext.NAME_VAR, "env", _env(ext.NAME_VAR)],
        ["token (file, preferred)", ext.TOKEN_FILE_VAR, "file", _masked(from_file)],
        ["token (env, second option)", ext.TOKEN_ENV_VAR, "env", _masked(from_env)],
    ]
    print(tabulate(rows, headers=["what", "name", "kind", "value"], tablefmt="simple"))

    if from_file and from_env:
        print(f"\nfile and env hold the same token: {from_file == from_env}")

    # What application code should do: file first, env as fallback.
    found = ext.read_token()
    if found is None:
        print("\nno token injected - is externalAuthRef set on the chain?")
        return
    token, source = found
    print(f"\ntoken used by the app: from {source}")

    claims = ext.claims(token)
    if claims:
        info = [[k, claims[k]] for k in ("iss", "sub", "aud") if k in claims]
        if "exp" in claims:
            left = humanize.naturaldelta(claims["exp"] - time.time())
            info.append(["expires in", left])
        print(tabulate(info, tablefmt="simple"))

    # To call a service the token was minted for, send ext.auth_header(token).
    print(f"\nrequest header would be: Authorization: Bearer <{len(token)} chars, masked>")


def _env(name: str) -> str:
    return os.environ.get(name, "<not set>")


def _masked(value: str | None) -> str:
    return "<not set>" if value is None else f"<{len(value)} chars, masked>"


if __name__ == "__main__":
    main()
