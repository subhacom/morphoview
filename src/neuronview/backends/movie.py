"""Render a rotating movie of a morphology with VTK.

Rotates the neuron about one or more axes and writes each frame, producing
an animation.  Requires the ``vtk`` package.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

import networkx as nx

from .. import colors, transform
from . import vtk as vtk_backend

vtk = vtk_backend.vtk


def _bounding_center(graph: nx.DiGraph) -> Tuple[float, float, float]:
    xs = [graph.nodes[n]["x"] for n in graph]
    ys = [graph.nodes[n]["y"] for n in graph]
    zs = [graph.nodes[n]["z"] for n in graph]
    return (
        (min(xs) + max(xs)) * 0.5,
        (min(ys) + max(ys)) * 0.5,
        (min(zs) + max(zs)) * 0.5,
    )


def dump_movie(
    filename: str,
    graph: nx.DiGraph,
    colormap: Optional[Dict[int, colors.RGB]] = None,
    background: Tuple[float, float, float] = (0, 0, 0),
    lines: float = 0.0,
    xrot: float = 0.0,
    yrot: float = 0.0,
    zrot: float = 0.0,
    xangle: float = 0.0,
    yangle: float = 0.0,
    zangle: float = 0.0,
    frames_per_degree: int = 10,
    framerate: int = 25,
    size: Tuple[int, int] = (800, 600),
) -> None:
    """Write a rotating animation of ``graph`` to ``filename`` (AVI).

    ``xrot/yrot/zrot`` orient the neuron before recording; ``xangle`` etc.
    are the total sweep in degrees about each axis during the movie.
    """
    if colormap is None:
        colormap = colors.get_colormap(colors.DEFAULT_COLORMAP)

    # Centre the morphology at the origin, then apply the initial orientation.
    cx, cy, cz = _bounding_center(graph)
    transform.apply_transform(
        graph,
        transform.rotation_translation_matrix(-cx, -cy, -cz, xrot, yrot, zrot),
    )

    renderer = vtk_backend.make_renderer(
        graph, colormap=colormap, background=background, lines=lines
    )
    actor = renderer.GetActors().GetLastActor()
    cx, cy, cz = _bounding_center(graph)
    actor.SetOrigin(cx, cy, cz)

    window = vtk.vtkRenderWindow()
    window.SetSize(*size)
    window.AddRenderer(renderer)
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)
    window.Render()
    interactor.Initialize()

    def _step(angle):
        return (0.0 if angle == 0 else 1.0 / frames_per_degree,
                int(angle * frames_per_degree))

    dx, xframes = _step(xangle)
    dy, yframes = _step(yangle)
    dz, zframes = _step(zangle)
    frames = max(xframes, yframes, zframes)

    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(window)
    w2if.ReadFrontBufferOff()
    w2if.Update()
    writer = vtk.vtkAVIWriter()
    writer.SetRate(framerate)
    writer.SetInputConnection(w2if.GetOutputPort())
    writer.SetFileName(filename)
    writer.Start()
    for _ in range(frames):
        actor.RotateX(dx)
        actor.RotateY(dy)
        actor.RotateZ(dz)
        window.Render()
        w2if.Modified()  # crucial: force the filter to grab the new frame
        writer.Write()
    writer.End()
