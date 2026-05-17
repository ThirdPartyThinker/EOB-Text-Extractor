"""Ensure the project root is importable when running pytest.

Running ``pytest`` directly does not add the project root to ``sys.path``,
so ``tests/test_extract.py`` could not ``import eob_extract``. pytest loads
this root-level conftest.py before collecting tests; inserting the project
root here guarantees the import works regardless of how pytest is invoked.
"""

import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
