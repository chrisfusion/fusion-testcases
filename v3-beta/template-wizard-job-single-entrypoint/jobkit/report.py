"""The job's work: a word-frequency report on the excerpt, plus a look at the injected token."""
import time
from collections import Counter

import humanize
from tabulate import tabulate

from jobkit import excerpt, token


def run() -> None:
    text = excerpt.load()
    words = [w.strip(".,:;!?\"'()»«-").lower() for w in text.split()]
    words = [w for w in words if w]
    top = Counter(words).most_common(5)
    print(f"excerpt: {len(words)} words, {len(set(words))} distinct, {humanize.naturalsize(len(text.encode()))}")
    print(tabulate(top, headers=["word", "count"], tablefmt="simple"))
    print()
    _report_token()


def _report_token() -> None:
    tok = token.read_token()
    if tok is None:
        print("token: none injected (no externalAuthMode/externalAuthName in the wizard run)")
        return
    # Never print the token itself, only facts about it.
    print(f"token: read from file {token.TOKEN_FILE_VAR}, {len(tok)} chars, masked")
    info = token.claims(tok)
    rows = [[k, info[k]] for k in ("iss", "sub", "aud") if k in info]
    if "exp" in info:
        rows.append(["expires in", humanize.naturaldelta(info["exp"] - time.time())])
    if rows:
        print(tabulate(rows, tablefmt="simple"))
