"""Where the files are: the raw ebook (asset) and the files of the pipeline (shared storage)."""
import os

import assets

# Shared storage. fusion mounts the per-run volume of a chain with `sharedStorage`
# at /weave-shared in every job pod and every run-owned deploy step; all steps of
# one run see the same files. SHARED_DIR overrides it, e.g. for a local run.
SHARED_DIR = os.environ.get("SHARED_DIR", "/weave-shared")

RAW_FILE = os.path.join(os.path.dirname(assets.__file__), "die_verwandlung.txt")  # input, shipped in the artifact
CLEAN_FILE = os.path.join(SHARED_DIR, "clean.txt")        # written by extract.py, read by count.py
WORDCOUNT_FILE = os.path.join(SHARED_DIR, "wordcount.csv")  # written by count.py, read by dashboard.py
