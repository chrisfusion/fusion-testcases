# Marks `kafka_etl` as a Python package. Required: fusion-forge only copies top-level
# directories that are importable packages into the venv.
#
# This is where the code shared by the three entrypoints lives. The loose scripts
# (extract.py, count.py, dashboard.py) cannot import each other - only packages
# are installed into the venv.
