"""Rigid transformations (translation, rotation, mirroring) of morphologies.

These operate on the :class:`networkx.DiGraph` representation from
:mod:`morphoview.graph`, letting several cells be positioned relative to
one another before rendering.
"""

from __future__ import annotations

from typing import Iterable

import networkx as nx
import numpy as np


def rotation_translation_matrix(
    xshift: float = 0.0,
    yshift: float = 0.0,
    zshift: float = 0.0,
    thetax: float = 0.0,
    thetay: float = 0.0,
    thetaz: float = 0.0,
) -> np.ndarray:
    """Build a 4x4 homogeneous rigid-transform matrix.

    Rotation angles are in **degrees**.  Transformations are composed in
    the order: rotate about X, then Y, then Z, then translate.
    """
    tx, ty, tz = np.radians([thetax, thetay, thetaz])

    translate = np.identity(4)
    translate[:-1, -1] = (xshift, yshift, zshift)

    xrot = np.identity(4)
    xrot[1, 1] = np.cos(tx)
    xrot[2, 2] = np.cos(tx)
    xrot[1, 2] = -np.sin(tx)
    xrot[2, 1] = np.sin(tx)

    yrot = np.identity(4)
    yrot[0, 0] = np.cos(ty)
    yrot[0, 2] = np.sin(ty)
    yrot[2, 0] = -np.sin(ty)
    yrot[2, 2] = np.cos(ty)

    zrot = np.identity(4)
    zrot[0, 0] = np.cos(tz)
    zrot[0, 1] = -np.sin(tz)
    zrot[1, 0] = np.sin(tz)
    zrot[1, 1] = np.cos(tz)

    return translate.dot(zrot).dot(yrot).dot(xrot)


def apply_transform(graph: nx.DiGraph, matrix: np.ndarray) -> nx.DiGraph:
    """Apply a 4x4 homogeneous transform to every node of ``graph``.

    Modifies ``graph`` in place and also returns it for convenience.
    """
    for _, attr in graph.nodes(data=True):
        pos = np.array([attr["x"], attr["y"], attr["z"], 1.0])
        new = matrix.dot(pos)
        attr["x"], attr["y"], attr["z"] = new[0], new[1], new[2]
    return graph


def translate(graph: nx.DiGraph, xshift=0.0, yshift=0.0, zshift=0.0) -> nx.DiGraph:
    """Translate a morphology in place."""
    return apply_transform(
        graph, rotation_translation_matrix(xshift, yshift, zshift)
    )


def rotate(graph: nx.DiGraph, thetax=0.0, thetay=0.0, thetaz=0.0) -> nx.DiGraph:
    """Rotate a morphology about the origin (degrees), in place."""
    return apply_transform(
        graph,
        rotation_translation_matrix(0, 0, 0, thetax, thetay, thetaz),
    )


def mirror(graph: nx.DiGraph, axes: Iterable[str]) -> nx.DiGraph:
    """Reflect the morphology across the plane normal to each named axis.

    ``axes`` is any iterable of ``'x'``, ``'y'`` and/or ``'z'`` (e.g. the
    string ``"xz"``).  Modifies ``graph`` in place.
    """
    for axis in axes:
        if axis not in ("x", "y", "z"):
            raise ValueError(f"Mirror axis must be x, y or z, not {axis!r}")
        for _, attr in graph.nodes(data=True):
            attr[axis] = -attr[axis]
    return graph
