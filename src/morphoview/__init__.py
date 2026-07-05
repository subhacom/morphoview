"""morphoview -- read, analyze and visualize neuronal morphologies.

Quick start::

    import morphoview as nv

    graph = nv.swc_to_graph("cell.swc")
    print(nv.summary(graph))

    # Matplotlib (portable, always available if matplotlib is installed)
    from morphoview.backends import mpl
    mpl.plot_3d(graph, color=nv.get_colormap("3cd2"))
    mpl.show()

    # VTK (tapered tubes, interactive)
    from morphoview.backends import vtk
    vtk.show(graph, colormap=nv.get_colormap("3cd2"), axes=True)

The rendering backends (matplotlib, VTK, vispy) are optional and imported
lazily, so the core I/O and analysis work with just numpy + networkx.
"""

from __future__ import annotations

from . import colors, graph, swc, transform
from .colors import (
    COLORMAPS,
    DEFAULT_COLORMAP,
    STRUCTURE_IDS,
    STRUCTURE_NAMES,
    color_for_structure,
    get_colormap,
    normalize,
    structure_name,
)
from .graph import (
    branch_points,
    combine,
    graph_to_swc,
    leaf_nodes,
    n_branches,
    n_leaves,
    soma_distance,
    soma_pathlen,
    structure_node_map,
    summary,
    swc_to_graph,
    total_length,
)
from .swc import SWC_DTYPE, load_swc, save_swc
from .transform import apply_transform, mirror, rotate, translate

__version__ = "0.1.0"

__all__ = [
    "__version__",
    # submodules
    "colors",
    "graph",
    "swc",
    "transform",
    # colors
    "COLORMAPS",
    "DEFAULT_COLORMAP",
    "STRUCTURE_IDS",
    "STRUCTURE_NAMES",
    "color_for_structure",
    "get_colormap",
    "normalize",
    "structure_name",
    # swc I/O
    "SWC_DTYPE",
    "load_swc",
    "save_swc",
    # graph
    "swc_to_graph",
    "graph_to_swc",
    "combine",
    "branch_points",
    "n_branches",
    "leaf_nodes",
    "n_leaves",
    "total_length",
    "soma_distance",
    "soma_pathlen",
    "structure_node_map",
    "summary",
    # transforms
    "apply_transform",
    "translate",
    "rotate",
    "mirror",
]
