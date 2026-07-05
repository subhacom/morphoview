# morphoview

Read, analyze and visualize neuronal morphologies stored in
[SWC](http://www.neuronland.org/NLMorphologyConverter/MorphologyFormats/SWC/Spec.html)
format.

`morphoview` loads an SWC trace into a `networkx` graph, computes
morphology statistics (branch points, leaves, path lengths, total
neurite length), and renders the cell in 2-D or 3-D using any of three
pluggable backends:

| Backend      | Strengths                                    | Extra dependency |
|--------------|----------------------------------------------|------------------|
| `mpl`        | Portable, figure-quality 2-D/3-D line plots  | `matplotlib`     |
| `vtk`        | Tapered tubes, interactive, PNG/movie export | `vtk`            |
| `vispy`      | GPU-accelerated interactive tube view        | `vispy`          |

The core I/O and analysis need only `numpy` and `networkx`; each
rendering backend is optional and imported lazily.

This is a refactored, Python-3-native successor to the `morphutils`
scripts (`neurograph.py`, `displaycell.py`, `morph3d*.py`, `cellmovie.py`).

## Installation

Install from PyPI. The rendering backends are optional extras — the core
I/O and analysis need only `numpy` and `networkx`:

```bash
pip install morphoview            # core only (numpy + networkx)
pip install "morphoview[mpl]"     # + matplotlib backend
pip install "morphoview[vtk]"     # + VTK backend
pip install "morphoview[all]"     # everything
```

To work on the source, install in editable mode from a checkout:

```bash
pip install -e ".[dev]"           # editable install + test/backend deps
```

## Command line

```bash
# Print morphology statistics
morphoview info examples/sample.swc

# Interactive 3-D display (VTK, tapered tubes, coloured by structure)
morphoview display examples/sample.swc

# Matplotlib 2-D projection onto the XY plane
morphoview display examples/sample.swc -b mpl --proj xy -c 4cp

# Several cells at once, positioned independently
morphoview display cellA.swc cellB.swc -t "0 0 0" -t "200 0 0" -r "z 90"

# Save a snapshot without opening a window (headless)
morphoview display examples/sample.swc --save cell.png --offscreen

# Render a rotating movie sweeping 360 degrees about Y
morphoview movie -i examples/sample.swc -o cell.avi -y 360
```

Useful `display` options:

- `-b/--backend {vtk,mpl,vispy}` — pick the renderer (default `vtk`).
- `-l/--lines W` — draw fixed-width lines of width `W` instead of tubes.
- `-c/--colormap NAME` — structure colour palette (see below).
- `-t/--translate "X Y Z"`, `-r/--rotate "x 90 y 45"`, `-m/--mirror x` —
  per-file rigid transforms (repeat the flag once per input file).
- `--branches`, `--leaves`, `-s/--struct-id ID...` — label nodes.
- `-a/--scalebar`, `-F/--fullscreen`, `--save FILE.png`, `--offscreen`.

## Python API

```python
import morphoview as nv

graph = nv.swc_to_graph("examples/sample.swc")
print(nv.summary(graph))
# {'nodes': 19, 'edges': 18, 'branch_points': 3, 'branches': 8,
#  'leaves': 5, 'total_length': 57.76...}

# Per-structure node lists (soma / axon / dendrites / custom regions)
by_type = nv.structure_node_map(graph)

# Path length from the soma to every node
distances = nv.soma_distance(graph)

# Render with matplotlib
from morphoview.backends import mpl
ax = mpl.plot_3d(graph, color=nv.get_colormap("3cd2"))
mpl.show()

# Render with VTK (tapered tubes)
from morphoview.backends import vtk
vtk.show(graph, colormap=nv.get_colormap("3cd2"), axes=True)
```

### Transformations

```python
from morphoview import transform as tf

tf.rotate(graph, thetaz=90)          # degrees, about the origin
tf.translate(graph, 100, 0, 0)       # micrometres
tf.mirror(graph, "x")                # reflect across the YZ plane

combined = nv.combine(graph_a, graph_b)   # merge, renumbering node ids
```

## Structure ids and colour palettes

SWC tags each point with a structure id. The standard ids are
`1=soma`, `2=axon`, `3=basal dendrite`, `4=apical dendrite`; ids `>= 5`
are custom (`morphoview` also names the GGN regions `5=LCA`, `6=MCA`,
`7=LH`, `8=alphaL`).

Palettes are keyed by short names combining a class count and a scheme,
mostly from [colorbrewer2.org](https://colorbrewer2.org) and the
[SRON](https://personal.sron.nl/~pault/) colour-blind-safe sets:
`3cd2` (default), `3cs2`, `3cp`, `4cp`, `5cd2`, `5cs3`, `7q`, `7cp`,
`7ca`, `7cd2`, `9q`, `10cp`, `10cs3`, `15cb`. Structure ids beyond a
palette's length wrap around so every morphology still renders.

## Project layout

```
src/morphoview/
    swc.py          SWC file I/O (numpy structured arrays)
    graph.py        networkx graph construction + morphology analysis
    colors.py       structure-id names and colour palettes
    transform.py    rigid transforms (translate/rotate/mirror)
    cli.py          the `morphoview` command-line entry point
    backends/
        mpl.py      matplotlib 2-D/3-D
        vtk.py      VTK tubes/lines, labels, PNG export
        vispy.py    vispy tube view
        movie.py    VTK rotating-movie export
tests/              pytest suite (core + matplotlib backend)
examples/sample.swc small synthetic neuron for demos/tests
```

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Releasing to PyPI

Publishing is automated by
[`.github/workflows/publish.yml`](.github/workflows/publish.yml). It builds
the sdist and wheel on every push/PR as a smoke test, and uploads them to
PyPI when a GitHub Release is published, using
[Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (OIDC) — so
there are no API tokens to store as secrets.

One-time setup on PyPI: at
<https://pypi.org/manage/account/publishing/> add a *pending publisher* for
this project with

- PyPI project name: `morphoview`
- Owner: `subhacom`
- Repository: `morphoview`
- Workflow: `publish.yml`
- Environment: `pypi`

To cut a release:

1. Bump `version` in `pyproject.toml` (and commit).
2. Create a GitHub Release with a tag matching that version, e.g. `v0.1.0`
   (the leading `v` is optional). The workflow verifies the tag matches
   `pyproject.toml` and fails fast on a mismatch.
3. Publishing runs automatically once the release is published.

## History
It was refactored and updated by Claude Opus 4.8 from the morphology utilities developed for the GGN model published in Ray S, Aldworth ZN, Stopfer MA. Feedback inhibition and its control in an insect olfactory circuit. Scott K, editor. eLife. 2020 Mar 12;9:e53281. doi:10.7554/eLife.53281.


## License

MIT
