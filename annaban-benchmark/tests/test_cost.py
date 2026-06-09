from annaban_benchmark.cost import total_cost


def test_total_cost():
    assert total_cost([0.1, 0.2]) == 0.3
