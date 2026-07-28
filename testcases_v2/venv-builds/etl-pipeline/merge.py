import json
import os

print(json.dumps({
    "step": "merge",
    "artifact": os.environ.get("WEAVE_ARTIFACT"),
    "tag": os.environ.get("WEAVE_TAG"),
    "version": os.environ.get("WEAVE_VERSION"),
}))
