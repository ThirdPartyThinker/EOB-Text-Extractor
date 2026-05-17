# Placing conftest.py at the project root makes pytest add this directory to
# sys.path, so tests in tests/ can `import eob_extract` regardless of how
# pytest is invoked (`pytest` vs `python -m pytest`).
