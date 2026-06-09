from annaban_benchmark.consensus import agreement_score


def test_agreement_score():
    assert agreement_score(["a", "a", "b"]) == 0.6667
