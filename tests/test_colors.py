import pytest

import morphoview as nv
from morphoview import colors


def test_structure_names():
    assert colors.structure_name(1) == "soma"
    assert colors.structure_name(2) == "axon"
    # unknown / custom ids fall back to 'neurite'
    assert colors.structure_name(999) == "neurite"


def test_get_colormap_known():
    cm = nv.get_colormap("3cd2")
    assert cm is colors.COLORMAPS["3cd2"]


def test_get_colormap_unknown():
    with pytest.raises(KeyError):
        nv.get_colormap("does-not-exist")


def test_color_for_structure_wraps():
    cm = nv.get_colormap("3cd2")
    # sid beyond palette length wraps around
    assert colors.color_for_structure(cm, 5) == cm[5 % len(cm)]


def test_normalize_range():
    cm = nv.get_colormap("3cd2")
    norm = colors.normalize(cm)
    for rgb in norm.values():
        assert len(rgb) == 3
        assert all(0.0 <= c <= 1.0 for c in rgb)


def test_normalize_matches_source():
    cm = {0: (255, 0, 128)}
    norm = colors.normalize(cm)
    assert norm[0] == pytest.approx((1.0, 0.0, 128 / 255.0))
