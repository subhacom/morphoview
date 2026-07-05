import networkx as nx
import numpy as np

import morphoview as nv


def test_graph_structure(sample_graph):
    assert sample_graph.number_of_nodes() == 19
    assert sample_graph.number_of_edges() == 18  # tree: nodes - 1
    assert nx.is_weakly_connected(sample_graph)


def test_node_attributes(sample_graph):
    soma = sample_graph.nodes[1]
    assert soma["s"] == 1
    assert soma["p"] == -1
    for key in ("x", "y", "z", "r"):
        assert key in soma


def test_edge_lengths(sample_graph):
    # edge 1->16 goes from (0,0,0) to (2,0,0): length 2
    assert np.isclose(sample_graph.edges[1, 16]["length"], 2.0)
    assert all(d["length"] >= 0 for _, _, d in sample_graph.edges(data=True))


def test_branch_points(sample_graph):
    bps = dict(nv.branch_points(sample_graph))
    # node 1 (soma) branches to soma pts, axon; node 6 and 11 branch dendrites
    assert 6 in bps and bps[6] == 2
    assert 11 in bps and bps[11] == 2


def test_leaf_nodes(sample_graph):
    leaves = set(nv.leaf_nodes(sample_graph))
    # dendrite tips and axon end
    assert {8, 10, 13, 15, 19}.issubset(leaves)
    assert nv.n_leaves(sample_graph) == len(leaves)


def test_structure_node_map(sample_graph):
    smap = nv.structure_node_map(sample_graph)
    assert set(smap.keys()) == {1, 2, 3, 4}
    assert len(smap[1]) == 3  # soma points


def test_soma_distance(sample_graph):
    dist = nv.soma_distance(sample_graph)
    assert dist[1] == 0.0
    # farther nodes have larger distances
    assert dist[8] > dist[4]


def test_total_length_positive(sample_graph):
    assert nv.total_length(sample_graph) > 0


def test_summary_keys(sample_graph):
    stats = nv.summary(sample_graph)
    for key in ("nodes", "edges", "branch_points", "branches", "leaves",
                "total_length"):
        assert key in stats


def test_graph_from_array(sample_path):
    data = nv.load_swc(sample_path)
    g_arr = nv.swc_to_graph(data)
    g_file = nv.swc_to_graph(sample_path)
    assert g_arr.number_of_nodes() == g_file.number_of_nodes()
    assert g_arr.number_of_edges() == g_file.number_of_edges()


def test_graph_swc_roundtrip(sample_graph, tmp_path):
    out = tmp_path / "rt.swc"
    nv.graph_to_swc(sample_graph, str(out))
    reloaded = nv.swc_to_graph(str(out))
    assert reloaded.number_of_nodes() == sample_graph.number_of_nodes()
    assert reloaded.number_of_edges() == sample_graph.number_of_edges()


def test_combine_renumbers(sample_graph):
    combined = nv.combine(sample_graph, sample_graph)
    assert combined.number_of_nodes() == 2 * sample_graph.number_of_nodes()
    assert combined.number_of_edges() == 2 * sample_graph.number_of_edges()
