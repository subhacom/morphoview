"""Structure-type definitions and colour palettes for morphologies.

SWC files tag each point with a *structure identifier* (the second
column).  The SWC standard defines a handful of these (soma, axon,
basal/apical dendrite); anything above 4 is custom.  This module maps
those identifiers to human-readable names and provides a set of
colour-blind-friendly palettes for colouring the different structures.

Colours are stored as ``(r, g, b)`` tuples with components in ``0-255``.
Use :func:`normalize` to convert a palette to the ``0.0-1.0`` range that
matplotlib and VTK's floating-point APIs expect.
"""

from __future__ import annotations

from typing import Dict, Tuple

RGB = Tuple[int, int, int]

#: SWC standard structure identifiers.
STANDARD_STRUCTURE_NAMES: Dict[int, str] = {
    0: "unknown",
    1: "soma",
    2: "axon",
    3: "basal_dendrite",
    4: "apical_dendrite",
}

#: Custom structure identifiers (non-standard; e.g. GGN neuropil regions).
CUSTOM_STRUCTURE_NAMES: Dict[int, str] = {
    5: "LCA",
    6: "MCA",
    7: "LH",
    8: "alphaL",
}

#: Combined structure-id -> name lookup.
STRUCTURE_NAMES: Dict[int, str] = {
    **STANDARD_STRUCTURE_NAMES,
    **CUSTOM_STRUCTURE_NAMES,
}

#: Reverse lookup: name -> structure id.
STRUCTURE_IDS: Dict[str, int] = {v: k for k, v in STRUCTURE_NAMES.items()}


def structure_name(sid: int) -> str:
    """Return the human-readable name for a structure id.

    Unknown identifiers are reported as ``"neurite"`` rather than raising,
    matching the SWC convention that anything above 4 is a custom neurite.
    """
    return STRUCTURE_NAMES.get(sid, "neurite")


# ---------------------------------------------------------------------------
# Colour palettes.  Names follow colorbrewer2.org / SRON conventions:
#   the leading number is the number of classes, the suffix the scheme.
# ---------------------------------------------------------------------------

#: 3-class Dark2 -- colour-blind safe and printer friendly.
_3cd2 = {0: (27, 158, 119), 1: (217, 95, 2), 2: (117, 112, 179)}

#: 3-class Set2.
_3cs2 = {0: (102, 194, 165), 1: (252, 141, 98), 2: (141, 160, 203)}

#: 3-class Paired.
_3cp = {0: (166, 206, 227), 1: (31, 120, 180), 2: (178, 223, 138)}

#: 4-class Paired -- the only colour-blind safe *and* printer friendly
#: qualitative scheme on colorbrewer2.org.
_4cp = {
    0: (166, 206, 227),
    1: (31, 120, 180),
    2: (178, 223, 138),
    3: (51, 160, 44),
}

#: 5-class Dark2 -- printer friendly but not colour-blind safe.
_5cd2 = {
    0: (27, 158, 119),
    1: (217, 95, 2),
    2: (117, 112, 179),
    3: (231, 41, 138),
    4: (102, 166, 30),
}

#: 5-class Set3.
_5cs3 = {
    0: (141, 211, 199),
    1: (255, 255, 179),
    2: (190, 186, 218),
    3: (251, 128, 114),
    4: (128, 177, 211),
}

#: 7-class SRON qualitative (https://personal.sron.nl/~pault/).
_7q = {
    0: (187, 187, 187),
    1: (102, 204, 238),
    2: (68, 119, 170),
    3: (170, 51, 119),
    4: (238, 102, 119),
    5: (204, 187, 68),
    6: (34, 136, 51),
}

#: 7-class Paired.
_7cp = {
    0: (166, 206, 227),
    1: (31, 120, 180),
    2: (178, 223, 138),
    3: (51, 160, 44),
    4: (251, 154, 153),
    5: (227, 26, 28),
    6: (253, 191, 111),
}

#: 7-class Dark2.
_7cd2 = {
    0: (127, 158, 119),
    1: (217, 95, 2),
    2: (117, 112, 179),
    3: (231, 41, 138),
    4: (102, 166, 30),
    5: (230, 171, 2),
    6: (166, 118, 29),
}

#: 7-class Accent.
_7ca = {
    0: (127, 201, 127),
    1: (190, 174, 212),
    2: (253, 192, 134),
    3: (255, 255, 153),
    4: (56, 108, 176),
    5: (240, 2, 127),
    6: (191, 91, 23),
}

#: 9-class SRON qualitative.
_9q = {
    0: (136, 204, 238),
    1: (221, 204, 119),
    2: (68, 170, 153),
    3: (153, 153, 51),
    4: (204, 102, 119),
    5: (170, 68, 153),
    6: (51, 34, 136),
    7: (17, 119, 51),
    8: (136, 34, 85),
}

#: 10-class Paired.
_10cp = {
    0: (166, 206, 227),
    1: (31, 120, 180),
    2: (178, 223, 138),
    3: (51, 160, 44),
    4: (251, 154, 153),
    5: (227, 26, 28),
    6: (253, 191, 111),
    7: (255, 127, 0),
    8: (202, 178, 214),
    9: (106, 61, 154),
}

#: 10-class Set3.
_10cs3 = {
    0: (141, 211, 199),
    1: (255, 255, 179),
    2: (190, 186, 218),
    3: (251, 128, 114),
    4: (128, 177, 211),
    5: (253, 180, 98),
    6: (179, 222, 105),
    7: (252, 205, 229),
    8: (217, 217, 217),
    9: (188, 128, 189),
}

#: 15-class colour-blind friendly (tuned for GGN structure ids).
_15cb = {
    0: (0, 0, 0),
    1: (0, 73, 73),
    2: (0, 146, 146),
    3: (255, 109, 182),
    4: (255, 182, 219),
    5: (219, 109, 0),
    6: (0, 109, 219),
    7: (182, 109, 255),
    8: (109, 182, 255),
    9: (182, 219, 255),
    10: (146, 0, 0),
    11: (146, 73, 0),
    12: (73, 0, 146),
    13: (36, 255, 36),
    14: (255, 255, 109),
}

#: All available palettes keyed by short name.
COLORMAPS: Dict[str, Dict[int, RGB]] = {
    "3cd2": _3cd2,
    "3cs2": _3cs2,
    "3cp": _3cp,
    "4cp": _4cp,
    "5cd2": _5cd2,
    "5cs3": _5cs3,
    "7q": _7q,
    "7cp": _7cp,
    "7ca": _7ca,
    "7cd2": _7cd2,
    "9q": _9q,
    "15cb": _15cb,
    "10cp": _10cp,
    "10cs3": _10cs3,
}

#: Default palette used across the package.
DEFAULT_COLORMAP = "3cd2"


def get_colormap(name: str) -> Dict[int, RGB]:
    """Look up a palette by name, raising a helpful error otherwise."""
    try:
        return COLORMAPS[name]
    except KeyError:
        available = ", ".join(sorted(COLORMAPS))
        raise KeyError(
            f"Unknown colormap {name!r}. Available: {available}"
        ) from None


def color_for_structure(colormap: Dict[int, RGB], sid: int) -> RGB:
    """Return the palette colour for a structure id.

    Structure ids beyond the palette length wrap around, so any morphology
    renders with *some* colour even if it uses more structure types than the
    palette defines.
    """
    return colormap[sid % len(colormap)]


def normalize(colormap: Dict[int, RGB]) -> Dict[int, Tuple[float, float, float]]:
    """Convert a ``0-255`` palette to ``0.0-1.0`` floating-point components."""
    return {
        k: (r / 255.0, g / 255.0, b / 255.0)
        for k, (r, g, b) in colormap.items()
    }
