"""Vispy rendering backend.

A GPU-accelerated interactive 3-D view using tube visuals.  Requires the
``vispy`` package (``pip install morphoview[vispy]``).
"""

from __future__ import annotations

import networkx as nx
import numpy as np

try:
    from vispy import scene
    from vispy.scene import visuals
except ImportError as exc:  # pragma: no cover - exercised only without vispy
    raise ImportError(
        "The vispy backend requires the 'vispy' package. "
        "Install it with: pip install morphoview[vispy]"
    ) from exc


def show(graph: nx.DiGraph, color="blue", name: str = "Neuron") -> None:
    """Render a morphology as tubes in an interactive vispy canvas."""
    canvas = scene.SceneCanvas(title=name, keys="interactive", show=True)
    view = canvas.central_widget.add_view()
    view.camera = scene.cameras.TurntableCamera(
        fov=45, azimuth=-45, parent=view.scene
    )
    for n0, n1 in graph.edges():
        a = graph.nodes[n0]
        b = graph.nodes[n1]
        pos0 = np.array((a["x"], a["y"], a["z"]))
        pos1 = np.array((b["x"], b["y"], b["z"]))
        mid = 0.5 * (pos0 + pos1)
        tube = visuals.Tube(
            points=np.vstack((pos0, mid, pos1)),
            radius=max(a["r"], 1e-3),
            color=color,
        )
        view.add(tube)
    canvas.app.run()
