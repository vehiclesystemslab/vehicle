import pandas as pd

from vehicle.observables import h1_monotone_dissipation, h2_observable_non_factorization


def test_h1_detects_monotone_sequence():
    result = h1_monotone_dissipation([3.0, 2.0, 2.0, 1.0])
    assert result["ok"] is True
    assert result["violation_count"] == 0


def test_h1_detects_violation():
    result = h1_monotone_dissipation([3.0, 2.0, 2.1, 1.0], epsilon=1e-6)
    assert result["ok"] is False
    assert result["violations"] == [2]


def test_h2_requires_columns():
    df = pd.DataFrame({"total_tension": [1.0, 0.9]})
    result = h2_observable_non_factorization(df)
    assert result["ok"] is False
