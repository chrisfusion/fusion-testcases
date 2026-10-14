# Marks `assets` as a Python package. Required: fusion-forge only copies top-level
# directories that are importable packages into the venv. The raw ebook
# (die_verwandlung.txt) travels with it and is located relative to this package
# by kafka_etl/paths.py. Shipping the text inside the artifact means the job needs
# NO internet access at runtime.
