"""Graph representation and analysis of neuronal morphologies.

A morphology is represented as a :class:`networkx.DiGraph` where each node
is a trace point carrying ``x, y, z, r`` (position and radius), ``s``
(structure id) and ``p`` (parent id) attributes, and each directed edge
runs parent -> child carrying a ``length`` attribute (the Euclidean
distance between the two points).
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Tuple

import networkx as nx
import numpy as np

from . import swc
from .swc import PathLike

#: Convention: the soma / root node id in a well-formed SWC morphology.
SOMA = 1


def euclidean_distance(graph: nx.DiGraph, n1, n2) -> float:
    """Euclidean distance between two nodes using their ``x, y, z`` attrs."""
    a = graph.nodes[n1]
    b = graph.nodes[n2]
    return float(
        np.sqrt(
            (a["x"] - b["x"]) ** 2
            + (a["y"] - b["y"]) ** 2
            + (a["z"] - b["z"]) ** 2
        )
    )


def swc_to_graph(source) -> nx.DiGraph:
    """Build a :class:`networkx.DiGraph` from a morphology.

    ``source`` may be a path to an SWC file or a structured array with
    :data:`morphoview.swc.SWC_DTYPE` layout.  Each node gets the point's
    ``x, y, z, r, s, p`` attributes; each edge gets a ``length``.
    """
    if isinstance(source, (str, bytes)) or hasattr(source, "__fspath__"):
        data = swc.load_swc(source)
    else:
        data = source

    graph = nx.DiGraph()
    for row in data:
        n = int(row["n"])
        p = int(row["p"])
        if p >= 0:
            graph.add_edge(p, n)
        else:
            graph.add_node(n)
        graph.nodes[n].update(
            x=float(row["x"]),
            y=float(row["y"]),
            z=float(row["z"]),
            r=float(row["r"]),
            p=p,
            s=int(row["s"]),
        )
    for n0, n1 in graph.edges:
        graph.edges[n0, n1]["length"] = euclidean_distance(graph, n0, n1)
    return graph


def combine(*graphs: nx.DiGraph) -> nx.DiGraph:
    """Merge several morphology graphs into one, renumbering node ids.

    Node ids across the inputs are shifted so they never collide, and each
    node's ``p`` (parent) attribute is shifted to match.  Useful for
    rendering several cells together in a single scene.
    """
    combined = nx.DiGraph()
    offset = 0
    for graph in graphs:
        if graph.number_of_nodes() == 0:
            continue
        mapping = {n: n + offset for n in graph.nodes()}
        relabeled = nx.relabel_nodes(graph, mapping, copy=True)
        for _, attr in relabeled.nodes(data=True):
            if attr.get("p", -1) >= 0:
                attr["p"] += offset
        combined = nx.union(combined, relabeled)
        offset = max(combined.nodes())
    return combined


def graph_to_swc(graph: nx.DiGraph, path: PathLike) -> None:
    """Write the morphology in ``graph`` to an SWC file."""
    with open(path, "w") as fd:
        for n in sorted(graph.nodes()):
            attr = graph.nodes[n]
            fd.write(
                "{n} {s} {x:.6f} {y:.6f} {z:.6f} {r:.6f} {p}\n".format(
                    n=n, **attr
                )
            )


# ---------------------------------------------------------------------------
# Morphology analysis
# ---------------------------------------------------------------------------

def structure_node_map(graph: nx.DiGraph) -> Dict[int, List[int]]:
    """Reverse lookup ``{structure_id: [nodes]}`` for a morphology."""
    ret: Dict[int, List[int]] = defaultdict(list)
    for n, attr in graph.nodes(data=True):
        ret[attr["s"]].append(n)
    return ret


def branch_points(graph: nx.DiGraph) -> List[Tuple[int, int]]:
    """Return ``[(node, out_degree)]`` for every branching node.

    A branch point is a node with more than one child.
    """
    return [(node, deg) for node, deg in graph.out_degree() if deg > 1]


def n_branches(graph: nx.DiGraph) -> int:
    """Total number of branches (counts the trunk out of the soma)."""
    return sum(deg for _, deg in branch_points(graph)) + 1


def leaf_nodes(graph: nx.DiGraph) -> List[int]:
    """Return the terminal (leaf) nodes of the morphology."""
    return [
        n
        for n in graph.nodes()
        if graph.out_degree(n) == 0 and graph.in_degree(n) == 1
    ]


def n_leaves(graph: nx.DiGraph) -> int:
    """Number of leaf (terminal) nodes."""
    return len(leaf_nodes(graph))


def total_length(graph: nx.DiGraph) -> float:
    """Total physical length of all neurites (sum of edge lengths)."""
    return float(sum(d["length"] for _, _, d in graph.edges(data=True)))


def sorted_edges(
    graph: nx.DiGraph, attr: str = "length", reverse: bool = False
) -> List[Tuple[int, int]]:
    """Edges sorted by an edge attribute (default ``length``)."""
    return sorted(
        graph.edges,
        key=lambda e: graph.edges[e[0], e[1]][attr],
        reverse=reverse,
    )


def soma_distance(graph: nx.DiGraph, soma: int = SOMA) -> Dict[int, float]:
    """Physical path length from the soma to each node."""
    dist = {soma: 0.0}
    for n0, n1 in nx.dfs_edges(graph, soma):
        if n1 not in dist:
            dist[n1] = dist[n0] + graph.edges[n0, n1]["length"]
    return dist


def soma_pathlen(graph: nx.DiGraph, soma: int = SOMA) -> Dict[int, int]:
    """Number of edges between the soma and each node."""
    dist = {soma: 0}
    for n0, n1 in nx.dfs_edges(graph, soma):
        if n1 not in dist:
            dist[n1] = dist[n0] + 1
    return dist


def summary(graph: nx.DiGraph) -> Dict[str, float]:
    """A dict of summary statistics for a morphology."""
    return {
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "branch_points": len(branch_points(graph)),
        "branches": n_branches(graph),
        "leaves": n_leaves(graph),
        "total_length": total_length(graph),
    }
