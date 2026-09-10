import json
import os

INPUT_PATH = "/weave-input/input.json"


def _load_upstream_input() -> dict:
    if not os.path.exists(INPUT_PATH):
        return {}
    with open(INPUT_PATH) as f:
        return json.load(f)


def main() -> None:
    upstream = _load_upstream_input()

    print("wizard-batch-test-job: single batch run starting...")
    result = {
        "job": "wizard-batch-test-job",
        "upstream": upstream,
    }
    print("wizard-batch-test-job: done.")
    # Last stdout line must be the JSON payload for fusion-weave's
    # producesOutput capture rule to pick it up.
    print(json.dumps(result))


if __name__ == "__main__":
    main()
