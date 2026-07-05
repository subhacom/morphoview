import matplotlib

matplotlib.use("Agg")  # headless, no display required

import neuronview as nv
from neuronview.backends import mpl


def test_plot_2d_draws_all_edges(sample_graph):
    ax = mpl.plot_2d(sample_graph, proj="xy")
    # one Line2D per edge
    assert len(ax.lines) == sample_graph.number_of_edges()


def test_plot_2d_bad_proj(sample_graph):
    import pytest

    with pytest.raises(ValueError):
        mpl.plot_2d(sample_graph, proj="xq")


def test_plot_3d_with_palette(sample_graph):
    ax = mpl.plot_3d(sample_graph, color=nv.get_colormap("4cp"))
    assert len(ax.lines) == sample_graph.number_of_edges()


def test_mark_nodes(sample_graph):
    ax = mpl.plot_3d(sample_graph)
    before = len(ax.lines)
    leaves = nv.leaf_nodes(sample_graph)
    mpl.mark_nodes(sample_graph, leaves, ax, label=False)
    assert len(ax.lines) == before + len(leaves)
