"""Rendering backends for neuronal morphologies.

Each backend is imported lazily so that the heavy, optional dependencies
(matplotlib, VTK, vispy) are only required if you actually use them.
Import the one you need directly, e.g.::

    from neuronview.backends import mpl
    from neuronview.backends import vtk
"""
