import pytest
from annaban_benchmark.router import select_runner


def test_select_runner_openrouter():
    assert select_runner("openrouter").name == "openrouter"


def test_select_runner_unknown():
    with pytest.raises(ValueError):
        select_runner("nope")
