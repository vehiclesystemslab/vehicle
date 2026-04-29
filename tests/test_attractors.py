import numpy as np

from vehicle.attractors import classify_regime, classify_state, summarize_attractors


def test_classify_state_baseline_a0():
    label = classify_state(np.array([0.1, 0.1, 0.1, 0.1, 0.1]), local_tension=0.1)
    assert label == "A0"


def test_classify_state_rigid_pressure_a5():
    label = classify_state(np.array([0.1, 0.1, 0.1, 0.1, 0.1]), local_tension=0.8)
    assert label == "A5"


def test_classify_regime_governed_a0():
    assert classify_regime(0.4, 0.4, 0.8) == "A0"


def test_summarize_attractors_counts_all_classes():
    summary = summarize_attractors(["A0", "A0", "A5"])
    assert summary["A0"] == 2
    assert summary["A5"] == 1
    assert set(summary.keys()) == {f"A{i}" for i in range(7)}
