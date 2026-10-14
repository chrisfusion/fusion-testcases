# Marks `wordstats` as a Python package. Required: fusion-forge only copies top-level
# directories that are importable packages into the venv.
#
# This is where code shared by the entrypoints lives. The loose scripts
# (count.py, top.py, longest.py) are NOT importable from each other - only
# packages are - so anything two scripts need goes here.
