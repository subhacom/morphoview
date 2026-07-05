"""VTK rendering backend.

Renders a morphology as tapered tubes (using per-point radii) or as
fixed-width lines, coloured by structure type.  Supports labelling nodes,
an optional scale-bar axis, fullscreen display and saving a PNG snapshot.

Requires the ``vtk`` package (``pip install neuronview[vtk]``).
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import networkx as nx
import numpy as np

from .. import colors

try:
    import vtk
    from vtk.util import numpy_support as vtknp
except ImportError as exc:  # pragma: no cover - exercised only without vtk
    raise ImportError(
        "The VTK backend requires the 'vtk' package. "
        "Install it with: pip install neuronview[vtk]"
    ) from exc


def graph_to_polydata(
    graph: nx.DiGraph,
    colormap: Optional[Dict[int, colors.RGB]] = None,
    lines: bool = False,
) -> "vtk.vtkPolyData":
    """Convert a morphology graph into a ``vtkPolyData``.

    When ``lines`` is False the point radii are attached so a tube filter
    can taper the rendering; segment colours come from ``colormap`` keyed
    by the parent node's structure id.
    """
    if colormap is None:
        colormap = colors.get_colormap(colors.DEFAULT_COLORMAP)

    node_map = {n: i for i, n in enumerate(graph.nodes())}
    points = vtk.vtkPoints()
    points.SetNumberOfPoints(graph.number_of_nodes())
    for n, i in node_map.items():
        attr = graph.nodes[n]
        points.SetPoint(i, (attr["x"], attr["y"], attr["z"]))

    edges = vtk.vtkCellArray()
    color_arr = vtk.vtkUnsignedCharArray()
    color_arr.SetName("Colors")
    color_arr.SetNumberOfComponents(3)
    color_arr.SetNumberOfTuples(graph.number_of_edges())
    for i, (n0, n1) in enumerate(graph.edges()):
        line = vtk.vtkLine()
        line.GetPointIds().SetId(0, node_map[n0])
        line.GetPointIds().SetId(1, node_map[n1])
        edges.InsertNextCell(line)
        color_arr.SetTuple3(
            i, *colors.color_for_structure(colormap, graph.nodes[n0]["s"])
        )

    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetLines(edges)
    polydata.GetCellData().SetScalars(color_arr)

    if not lines:
        radii = np.array([graph.nodes[n]["r"] for n in node_map], dtype=float)
        radius_arr = vtknp.numpy_to_vtk(
            radii, deep=True, array_type=vtk.VTK_FLOAT
        )
        radius_arr.SetName("Radius")
        polydata.GetPointData().AddArray(radius_arr)
        polydata.GetPointData().SetActiveScalars("Radius")
        polydata.GetCellData().AddArray(color_arr)
    return polydata


def make_actor(
    graph: nx.DiGraph,
    colormap: Optional[Dict[int, colors.RGB]] = None,
    lines: float = 0.0,
) -> "vtk.vtkActor":
    """Build a ``vtkActor`` for a morphology.

    ``lines`` <= 0 renders tapered tubes; a positive value renders
    fixed-width lines of that width.
    """
    polydata = graph_to_polydata(graph, colormap=colormap, lines=lines > 0)
    mapper = vtk.vtkPolyDataMapper()
    if lines > 0:
        mapper.SetInputData(polydata)
    else:
        tube = vtk.vtkTubeFilter()
        tube.SetNumberOfSides(10)
        tube.SetVaryRadiusToVaryRadiusByAbsoluteScalar()
        tube.SetInputData(polydata)
        mapper.SetInputConnection(tube.GetOutputPort())
        mapper.ScalarVisibilityOn()
        mapper.SetScalarModeToUseCellFieldData()
        mapper.SelectColorArray("Colors")

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    if lines > 0:
        actor.GetProperty().SetLineWidth(lines)
    return actor


def make_label_actor(
    graph: nx.DiGraph,
    label_nodes: Sequence[int],
    labels: Optional[Sequence[str]] = None,
    priorities: Optional[Sequence[int]] = None,
    color: Tuple[float, float, float] = (0, 0, 0),
) -> "vtk.vtkActor2D":
    """Build a 2-D label actor placing text at the given nodes."""
    labels = labels or []
    priorities = priorities or []

    points = vtk.vtkPoints()
    label_str = vtk.vtkStringArray()
    label_str.SetName("Labels")
    for i, n in enumerate(label_nodes):
        attr = graph.nodes[n]
        points.InsertNextPoint((attr["x"], attr["y"], attr["z"]))
        text = str(labels[i]) if i < len(labels) else str(n)
        label_str.InsertNextValue(text)

    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.GetPointData().AddArray(label_str)

    hierarchy = vtk.vtkPointSetToLabelHierarchy()
    hierarchy.SetLabelArrayName(label_str.GetName())
    hierarchy.GetTextProperty().SetColor(*color)
    if priorities and len(priorities) == len(label_nodes):
        parray = vtk.vtkIntArray()
        parray.SetName("Priorities")
        for p in priorities:
            parray.InsertNextValue(p)
        hierarchy.SetPriorityArrayName(parray.GetName())
    hierarchy.SetInputData(polydata)

    prop = vtk.vtkTextProperty()
    prop.SetColor(*color)
    prop.ItalicOn()
    mapper = vtk.vtkLabelPlacementMapper()
    mapper.SetInputConnection(hierarchy.GetOutputPort())
    mapper.GetRenderStrategy().SetDefaultTextProperty(prop)

    actor = vtk.vtkActor2D()
    actor.SetMapper(mapper)
    return actor


def _scalebar_axes(renderer, background):
    color = tuple(1.0 - c for c in background)
    axes = vtk.vtkCubeAxesActor2D()
    axes.SetLabelFormat("%3.0f")
    # A fixed 0-200 um reference cube. Show the two endpoint labels so the
    # scale is readable; VTK requires >= 1 label per axis (0 warns).
    axes.SetNumberOfLabels(2)
    axes.SetBounds(0, 200, 0, 200, 0, 200)
    axes.SetXLabel("X")
    axes.SetYLabel("Y")
    axes.SetZLabel("Z")
    axes.SetXOrigin(0)
    axes.SetYOrigin(0)
    axes.SetZOrigin(0)
    tprop = vtk.vtkTextProperty()
    tprop.SetColor(*color)
    axes.SetAxisLabelTextProperty(tprop)
    axes.GetProperty().SetColor(*color)
    axes.SetCamera(renderer.GetActiveCamera())
    return axes


def make_renderer(
    graphs,
    colormap: Optional[Dict[int, colors.RGB]] = None,
    background: Tuple[float, float, float] = (0, 0, 0),
    lines: float = 0.0,
    label_nodes: Optional[Sequence[int]] = None,
    labels: Optional[Sequence[str]] = None,
    axes: bool = False,
) -> "vtk.vtkRenderer":
    """Assemble a ``vtkRenderer`` for one or more morphology graphs.

    ``graphs`` may be a single graph or an iterable of graphs.
    """
    if isinstance(graphs, nx.DiGraph):
        graphs = [graphs]
    if colormap is None:
        colormap = colors.get_colormap(colors.DEFAULT_COLORMAP)

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(*background)
    for graph in graphs:
        renderer.AddActor(make_actor(graph, colormap=colormap, lines=lines))
        if label_nodes:
            label_color = tuple(1.0 - c for c in background)
            renderer.AddActor2D(
                make_label_actor(
                    graph, label_nodes, labels=labels, color=label_color
                )
            )
    if axes:
        renderer.AddActor(_scalebar_axes(renderer, background))
    renderer.ResetCamera()
    return renderer


def show(
    graphs,
    colormap: Optional[Dict[int, colors.RGB]] = None,
    background: Tuple[float, float, float] = (0, 0, 0),
    lines: float = 0.0,
    label_nodes: Optional[Sequence[int]] = None,
    labels: Optional[Sequence[str]] = None,
    axes: bool = False,
    fullscreen: bool = False,
    stereo: bool = False,
    size: Tuple[int, int] = (1024, 768),
    save: Optional[str] = None,
    offscreen: bool = False,
) -> None:
    """Render morphologies in an interactive window (or offscreen).

    When ``save`` is given a PNG snapshot is written.  Set ``offscreen``
    True to render without opening a window (useful for headless PNG
    export); in that case the interactor loop is skipped.
    """
    renderer = make_renderer(
        graphs,
        colormap=colormap,
        background=background,
        lines=lines,
        label_nodes=label_nodes,
        labels=labels,
        axes=axes,
    )
    window = vtk.vtkRenderWindow()
    window.AddRenderer(renderer)
    window.SetSize(*size)
    if offscreen:
        window.SetOffScreenRendering(1)
    elif fullscreen:
        window.FullScreenOn()
    if stereo and not offscreen:
        window.GetStereoCapableWindow()
        window.StereoCapableWindowOn()
        window.SetStereoRender(1)
        window.SetStereoTypeToCrystalEyes()

    interactor = None
    if not offscreen:
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(window)

    window.Render()

    if save is not None:
        _save_png(window, save)

    if interactor is not None:
        interactor.Initialize()
        interactor.Start()


def _save_png(window, path: str) -> None:
    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(window)
    w2if.SetInputBufferTypeToRGB()
    w2if.ReadFrontBufferOff()
    w2if.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(path)
    writer.SetInputConnection(w2if.GetOutputPort())
    writer.Write()
