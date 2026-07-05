"""Matplotlib rendering backend.

Lightweight 2-D projections and a 3-D line rendering of a morphology.
This backend has no interactive picking of individual compartments but is
the most portable and works well for figures and headless rendering.
"""

from __future__ import annotations

from typing import Iterable

import networkx as nx

from .. import colors


def _resolve_color(color, sid, normalized):
    """Pick a colour for a segment given a fixed colour or a palette."""
    if isinstance(color, dict):
        return colors.color_for_structure(normalized, sid)
    return color


def plot_2d(
    graph: nx.DiGraph,
    ax=None,
    proj: str = "xy",
    color="k",
    alpha: float = 0.8,
    linewidth: float = 1.0,
):
    """Plot a 2-D projection of the morphology onto two axes.

    ``proj`` selects the plane, e.g. ``"xy"``, ``"xz"`` or ``"yz"``.
    ``color`` is either a matplotlib colour or a ``{sid: (r, g, b)}``
    palette (0-255) used to colour each segment by its structure type.
    """
    import matplotlib.pyplot as plt

    if len(proj) != 2 or any(c not in "xyz" for c in proj):
        raise ValueError(f"proj must be two of x/y/z, got {proj!r}")

    if ax is None:
        _, ax = plt.subplots()
        ax.set_aspect("equal")
        ax.set_xlabel(f"{proj[0]} (um)")
        ax.set_ylabel(f"{proj[1]} (um)")

    normalized = colors.normalize(color) if isinstance(color, dict) else {}
    a0, a1 = proj[0], proj[1]
    for n0, n1 in graph.edges():
        p0, p1 = graph.nodes[n0], graph.nodes[n1]
        c = _resolve_color(color, p0["s"], normalized)
        ax.plot(
            [p0[a0], p1[a0]],
            [p0[a1], p1[a1]],
            color=c,
            alpha=alpha,
            linewidth=linewidth,
        )
    return ax


def plot_3d(
    graph: nx.DiGraph,
    ax=None,
    color="k",
    alpha: float = 0.8,
    linewidth: float = 1.0,
):
    """Plot the morphology as 3-D lines.

    ``color`` may be a matplotlib colour or a ``{sid: (r, g, b)}`` palette.
    Returns the 3-D axes so callers can add markers or annotations.
    """
    import matplotlib.pyplot as plt

    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(projection="3d")
        ax.set_xlabel("x (um)")
        ax.set_ylabel("y (um)")
        ax.set_zlabel("z (um)")

    normalized = colors.normalize(color) if isinstance(color, dict) else {}
    for n0, n1 in graph.edges():
        p0, p1 = graph.nodes[n0], graph.nodes[n1]
        c = _resolve_color(color, p0["s"], normalized)
        ax.plot(
            [p0["x"], p1["x"]],
            [p0["y"], p1["y"]],
            [p0["z"], p1["z"]],
            color=c,
            alpha=alpha,
            linewidth=linewidth,
        )
    return ax


def mark_nodes(
    graph: nx.DiGraph,
    nodes: Iterable[int],
    ax,
    label: bool = True,
    color: str = "r",
    marker: str = "^",
):
    """Mark and optionally label a set of nodes on a 3-D axes."""
    for n in nodes:
        attr = graph.nodes[n]
        ax.plot([attr["x"]], [attr["y"]], [attr["z"]], marker=marker, color=color)
        if label:
            ax.text(attr["x"], attr["y"], attr["z"], str(n))
    return ax


def show():
    """Display any open matplotlib figures."""
    import matplotlib.pyplot as plt

    plt.show()
