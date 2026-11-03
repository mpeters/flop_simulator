"""Shared pytest fixtures and the import shim for the extension-less `flop_sim`.

The simulator lives in a file named `flop_sim` (no `.py` suffix), so it cannot
be imported with a normal `import` statement. We load it once here via
importlib and expose it as a session-scoped fixture, and also register it in
``sys.modules`` so coverage attributes executed lines to the real file.
"""

import importlib.util
import os
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_SCRIPT = os.path.join(os.path.dirname(_HERE), "flop_sim")


def _load_flop_sim():
    spec = importlib.util.spec_from_loader(
        "flop_sim",
        importlib.machinery.SourceFileLoader("flop_sim", _SCRIPT),
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["flop_sim"] = module
    spec.loader.exec_module(module)
    return module


# Load at import time so `import flop_sim` works inside test modules too.
flop_sim = _load_flop_sim()


@pytest.fixture(scope="session")
def fs():
    """The loaded flop_sim module."""
    return flop_sim
