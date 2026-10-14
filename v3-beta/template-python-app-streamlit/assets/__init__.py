# Marks `assets` as a Python package. Required: fusion-forge only copies top-level
# directories that are importable packages into the venv. Everything in this
# directory - the text, the pictures, the css, the icons/ sub-directory - is
# copied along with it, no extra flag needed. wordviz/theme.py locates the files
# relative to this package's __file__.
