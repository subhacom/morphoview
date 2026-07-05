import numpy as np

import neuronview as nv


def test_load_swc_fields(sample_path):
    data = nv.load_swc(sample_path)
    assert data.dtype == nv.SWC_DTYPE
    assert len(data) == 19
    # first point is the soma root
    assert data[0]["n"] == 1
    assert data[0]["s"] == 1
    assert data[0]["p"] == -1


def test_load_ignores_comments(sample_path):
    data = nv.load_swc(sample_path)
    # comment lines must not appear as points
    assert set(data["n"]) == set(range(1, 20))


def test_single_point_is_1d(tmp_path):
    p = tmp_path / "one.swc"
    p.write_text("1 1 0 0 0 1 -1\n")
    data = nv.load_swc(str(p))
    assert data.ndim == 1
    assert len(data) == 1


def test_roundtrip_save_load(sample_path, tmp_path):
    data = nv.load_swc(sample_path)
    out = tmp_path / "out.swc"
    nv.save_swc(data, str(out))
    reloaded = nv.load_swc(str(out))
    assert np.array_equal(data["n"], reloaded["n"])
    assert np.allclose(data["x"], reloaded["x"])
    assert np.array_equal(data["p"], reloaded["p"])
