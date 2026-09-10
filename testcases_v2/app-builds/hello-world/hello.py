import json
import os

print(json.dumps({
    "message": "Hello, World!",
    "entrypoint": "hello.py",
    "artifact": os.environ.get("WEAVE_ARTIFACT"),
    "tag": os.environ.get("WEAVE_TAG"),
    "version": os.environ.get("WEAVE_VERSION"),
}))
