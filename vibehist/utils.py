#!/usr/bin/env python3
"""
Common utilities
"""

import os


def normalize_path(path: str | os.PathLike[str]) -> str:
    """
    Normalize to absolute path
    """
    epath = os.fspath(path)
    epath = os.path.expanduser(epath)
    epath = os.path.expandvars(epath)
    epath = os.path.abspath(epath)
    epath = os.path.normpath(epath)
    return epath
