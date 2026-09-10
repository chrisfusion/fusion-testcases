import json
import os

print(json.dumps({
    "message": "Goodbye, World!",
    "entrypoint": "goodbye.py",
    "artifact": os.environ.get("WEAVE_ARTIFACT"),
    "tag": os.environ.get("WEAVE_TAG"),
    "version": os.environ.get("WEAVE_VERSION"),
}))
