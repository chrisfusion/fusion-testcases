import json
import os

import numpy as np

INPUT_PATH = "/weave-input/input.json"


def _load_upstream_input() -> dict:
    if not os.path.exists(INPUT_PATH):
        return {}
    with open(INPUT_PATH) as f:
        return json.load(f)


def run() -> None:
    """One-shot batch job: summarize a dataset and print the report as JSON.

    Meant to run as a WeaveJobTemplate step (not Deploy). If upstream steps
    declared `consumesOutputFrom`, their merged output is available at
    /weave-input/input.json and is echoed back under "upstream" so a
    downstream step can chain off this one too (this step also sets
    `producesOutput: true` in the showroom chain).
    """
    upstream = _load_upstream_input()
    row_count = int(os.environ.get("ROW_COUNT", "1000"))

    print(f"Generating report over {row_count} rows...")
    rng = np.random.default_rng()
    values = rng.normal(loc=100, scale=15, size=row_count)

    report = {
        "rowCount": row_count,
        "mean": round(float(values.mean()), 2),
        "stddev": round(float(values.std()), 2),
        "min": round(float(values.min()), 2),
        "max": round(float(values.max()), 2),
        "upstream": upstream,
    }

    print("Report complete.")
    # Last stdout line must be the JSON payload — fusion-weave's producesOutput
    # capture only reads the final line that parses as JSON.
    print(json.dumps(report))
