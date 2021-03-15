"""Notebook utilities for development environment setup"""

import pathlib
import sys

NOTEBOOK_ROOT = pathlib.Path(__file__).parent
PACKAGE_ROOT = NOTEBOOK_ROOT.parent


def setup_notebook():
    """Simple utility for adding dev-root to path for notebooks"""
    sys.path.append(str(PACKAGE_ROOT))
