import pathlib

import pytest

import neuronview as nv

SAMPLE = pathlib.Path(__file__).resolve().parents[1] / "examples" / "sample.swc"


@pytest.fixture
def sample_path():
    return str(SAMPLE)


@pytest.fixture
def sample_graph(sample_path):
    return nv.swc_to_graph(sample_path)
