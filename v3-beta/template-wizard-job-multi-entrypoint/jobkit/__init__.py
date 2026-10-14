# Marks `jobkit` as a Python package. Required: fusion-forge only copies top-level
# directories that are importable packages into the venv.
#
# Code shared by the entrypoints lives here. The loose scripts (count.py, top.py,
# longest.py) cannot import each other - only packages are installed into the venv.
