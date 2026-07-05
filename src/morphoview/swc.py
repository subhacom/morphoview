"""Reading and writing SWC morphology files.

The SWC format is a plain-text description of a neuron's traced
morphology.  Each non-comment line is one sample point::

    n  s  x  y  z  r  parent

where ``n`` is an integer id, ``s`` the structure identifier (see
:mod:`morphoview.colors`), ``x``/``y``/``z`` the position and ``r`` the
radius (all in micrometres by convention), and ``parent`` the id of the
parent point (``-1`` for the root).
"""

from __future__ import annotations

import os
from typing import Union

import numpy as np

#: Structured dtype for one SWC sample point.
SWC_DTYPE = np.dtype(
    [
        ("n", int),
        ("s", int),
        ("x", float),
        ("y", float),
        ("z", float),
        ("r", float),
        ("p", int),
    ]
)

PathLike = Union[str, os.PathLike]


def load_swc(path: PathLike) -> np.ndarray:
    """Load an SWC file into a structured numpy array.

    Comment lines (starting with ``#``) are ignored.  The returned array
    has fields ``n, s, x, y, z, r, p`` (see :data:`SWC_DTYPE`).

    A single-point morphology still comes back as a 1-D array so callers
    can iterate over rows uniformly.
    """
    data = np.loadtxt(path, dtype=SWC_DTYPE, comments="#", ndmin=1)
    return data


def save_swc(data: np.ndarray, path: PathLike) -> None:
    """Write a structured/record SWC array back to a file.

    The array columns must be ``id, type, x, y, z, r, parent`` in that
    order (the layout produced by :func:`load_swc`).
    """
    np.savetxt(path, data, fmt="%d %d %.6f %.6f %.6f %.6f %d")
