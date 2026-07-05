"""Command-line interface for neuronview.

Subcommands:

    neuronview info   FILE...            print morphology statistics
    neuronview display FILE... [opts]    interactive 3-D / 2-D display
    neuronview movie  -i FILE -o OUT ...  render a rotating movie (VTK)
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from . import colors, graph as ng


def _parse_triplet(text: str) -> List[float]:
    """Parse a whitespace-separated triple like ``"100 50 10"``."""
    return [float(x) for x in text.split()]


def _parse_rotation(text: str) -> List[tuple]:
    """Parse a rotation spec like ``"x 90 y 45"`` into ``[('x', 90.0), ...]``."""
    parts = text.split()
    if len(parts) % 2 != 0:
        raise argparse.ArgumentTypeError(
            f"Rotation spec must be pairs of axis and angle, got {text!r}"
        )
    out = []
    for axis, angle in zip(parts[0::2], parts[1::2]):
        if axis not in ("x", "y", "z"):
            raise argparse.ArgumentTypeError(f"Bad rotation axis {axis!r}")
        out.append((axis, float(angle)))
    return out


# ---------------------------------------------------------------------------
# info
# ---------------------------------------------------------------------------

def _cmd_info(args) -> int:
    for fname in args.filenames:
        graph = ng.swc_to_graph(fname)
        stats = ng.summary(graph)
        print(f"\n{fname}")
        print(f"  nodes          : {stats['nodes']}")
        print(f"  edges          : {stats['edges']}")
        print(f"  branch points  : {stats['branch_points']}")
        print(f"  branches       : {stats['branches']}")
        print(f"  leaves         : {stats['leaves']}")
        print(f"  total length   : {stats['total_length']:.2f} um")
        sid_map = ng.structure_node_map(graph)
        print("  structures     :")
        for sid in sorted(sid_map):
            name = colors.structure_name(sid)
            print(f"      {sid:>3} {name:<16} {len(sid_map[sid])} nodes")
    return 0


# ---------------------------------------------------------------------------
# display
# ---------------------------------------------------------------------------

def _collect_label_nodes(graph, args) -> List[int]:
    label_nodes: List[int] = []
    if args.branches:
        bps = ng.branch_points(graph)
        label_nodes += [n for n, _ in bps]
    if args.leaves:
        label_nodes += ng.leaf_nodes(graph)
    if args.sid:
        sid_map = ng.structure_node_map(graph)
        for sid in args.sid:
            label_nodes += sid_map.get(sid, [])
    return label_nodes


def _load_and_transform(args):
    """Load each file, apply per-file mirror/translate/rotate, combine."""
    from . import transform as tf

    graphs = []
    for i, fname in enumerate(args.filenames):
        graph = ng.swc_to_graph(fname)
        if i < len(args.mirror) and args.mirror[i]:
            tf.mirror(graph, args.mirror[i])
        if i < len(args.rotate) and args.rotate[i]:
            for axis, angle in args.rotate[i]:
                kwargs = {f"theta{axis}": angle}
                tf.rotate(graph, **kwargs)
        if i < len(args.translate) and args.translate[i]:
            tf.translate(graph, *args.translate[i])
        graphs.append(graph)
    return graphs


def _cmd_display(args) -> int:
    try:
        colormap = colors.get_colormap(args.colormap)
    except KeyError as exc:
        print(exc, file=sys.stderr)
        return 2

    background = tuple(_parse_triplet(args.background)[:3])
    graphs = _load_and_transform(args)
    combined = ng.combine(*graphs)
    label_nodes = _collect_label_nodes(combined, args)

    if args.backend == "mpl":
        from .backends import mpl

        if args.proj == "3d":
            ax = mpl.plot_3d(combined, color=colormap, linewidth=max(args.lines, 0.5))
        else:
            ax = mpl.plot_2d(
                combined, proj=args.proj, color=colormap,
                linewidth=max(args.lines, 0.5),
            )
        if label_nodes and args.proj == "3d":
            mpl.mark_nodes(combined, label_nodes, ax)
        mpl.show()
    elif args.backend == "vtk":
        from .backends import vtk

        vtk.show(
            combined,
            colormap=colormap,
            background=background,
            lines=args.lines,
            label_nodes=label_nodes,
            axes=args.scalebar,
            fullscreen=args.fullscreen,
            save=args.save,
            offscreen=args.save is not None and not args.fullscreen and args.offscreen,
        )
    elif args.backend == "vispy":
        from .backends import vispy

        vispy.show(combined)
    else:  # pragma: no cover - argparse restricts choices
        print(f"Unknown backend {args.backend}", file=sys.stderr)
        return 2
    return 0


# ---------------------------------------------------------------------------
# movie
# ---------------------------------------------------------------------------

def _cmd_movie(args) -> int:
    from .backends import movie

    graph = ng.swc_to_graph(args.infile)
    movie.dump_movie(
        args.outfile,
        graph,
        xrot=args.xrot,
        yrot=args.yrot,
        zrot=args.zrot,
        xangle=args.xangle,
        yangle=args.yangle,
        zangle=args.zangle,
        frames_per_degree=args.fpd,
        framerate=args.framerate,
    )
    print(f"Saved movie in {args.outfile}")
    return 0


# ---------------------------------------------------------------------------
# argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="neuronview",
        description="Read, analyze and visualize neuronal morphologies (SWC).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # info
    p_info = sub.add_parser("info", help="Print morphology statistics")
    p_info.add_argument("filenames", nargs="+", help="SWC file(s)")
    p_info.set_defaults(func=_cmd_info)

    # display
    p_disp = sub.add_parser("display", help="Display morphology in 2-D/3-D")
    p_disp.add_argument(
        "filenames", nargs="+", help="SWC file(s) to display"
    )
    p_disp.add_argument(
        "-b", "--backend", choices=["vtk", "mpl", "vispy"], default="vtk",
        help="Rendering backend (default: vtk)",
    )
    p_disp.add_argument(
        "--proj", default="3d",
        help="For the mpl backend: '3d' or a 2-D plane like 'xy' (default 3d)",
    )
    p_disp.add_argument(
        "-t", "--translate", type=_parse_triplet, action="append", default=[],
        metavar='"X Y Z"',
        help="Translate a cell; repeat per file, applied in order.",
    )
    p_disp.add_argument(
        "-r", "--rotate", type=_parse_rotation, action="append", default=[],
        metavar='"x 90 y 45"',
        help="Rotate a cell (axis/degree pairs); repeat per file.",
    )
    p_disp.add_argument(
        "-m", "--mirror", action="append", default=[], metavar="AXES",
        help="Mirror across plane(s) normal to the named axes, e.g. 'x'.",
    )
    p_disp.add_argument(
        "-l", "--lines", type=float, default=0.0,
        help="If > 0, render fixed-width lines of this width; "
        "otherwise render tapered tubes.",
    )
    p_disp.add_argument(
        "-c", "--colormap", default=colors.DEFAULT_COLORMAP,
        help="Structure colour palette (see --list-colormaps).",
    )
    p_disp.add_argument(
        "--background", default="0 0 0", metavar='"R G B"',
        help="Background colour, components in [0, 1] (default black).",
    )
    p_disp.add_argument(
        "--branches", action="store_true", help="Label branch points"
    )
    p_disp.add_argument(
        "--leaves", action="store_true", help="Label leaf nodes"
    )
    p_disp.add_argument(
        "-s", "--struct-id", type=int, nargs="+", dest="sid", default=[],
        help="Label nodes with the given structure ids",
    )
    p_disp.add_argument(
        "-a", "--scalebar", action="store_true", help="Show scale-bar axes"
    )
    p_disp.add_argument(
        "-F", "--fullscreen", action="store_true",
        help="Fullscreen display (VTK only)",
    )
    p_disp.add_argument(
        "--save", metavar="FILE.png",
        help="Save a PNG snapshot (VTK only).",
    )
    p_disp.add_argument(
        "--offscreen", action="store_true",
        help="Render offscreen when saving (VTK, headless).",
    )
    p_disp.set_defaults(func=_cmd_display)

    # movie
    p_mov = sub.add_parser("movie", help="Render a rotating movie (VTK)")
    p_mov.add_argument("-i", "--input", dest="infile", required=True,
                       help="SWC file to render")
    p_mov.add_argument("-o", "--output", dest="outfile", required=True,
                       help="Output movie file (AVI)")
    p_mov.add_argument("--xrot", type=float, default=0.0,
                       help="Initial rotation about X (degrees)")
    p_mov.add_argument("--yrot", type=float, default=0.0,
                       help="Initial rotation about Y (degrees)")
    p_mov.add_argument("--zrot", type=float, default=0.0,
                       help="Initial rotation about Z (degrees)")
    p_mov.add_argument("-x", dest="xangle", type=float, default=0.0,
                       help="Total sweep about X during the movie (degrees)")
    p_mov.add_argument("-y", dest="yangle", type=float, default=0.0,
                       help="Total sweep about Y during the movie (degrees)")
    p_mov.add_argument("-z", dest="zangle", type=float, default=0.0,
                       help="Total sweep about Z during the movie (degrees)")
    p_mov.add_argument("-f", "--frames", dest="fpd", type=int, default=10,
                       help="Frames per degree of rotation")
    p_mov.add_argument("-r", "--rate", dest="framerate", type=int, default=25,
                       help="Frame rate")
    p_mov.set_defaults(func=_cmd_movie)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
