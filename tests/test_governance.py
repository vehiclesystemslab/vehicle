import numpy as np
import pytest

from vehicle.governance import GovernanceParams, coherence_measure, project_to_coherent_region, relaxed_update


def test_projection_respects_tau_and_clip_range():
    vec = np.array([10.0, -10.0, 3.0, -3.0, 0.0])
    projected = project_to_coherent_region(vec, tau_limit=0.5, clip_range=(-2.0, 2.0))

    assert projected.shape == (5,)
    assert np.all(projected <= 2.0)
    assert np.all(projected >= -2.0)
    assert coherence_measure(projected) <= 0.5 + 1e-9


def test_relaxed_update_preserves_shape():
    params = GovernanceParams(gamma=0.05, alpha=0.3, tau_limit=0.5)
    vec = np.array([1.0, 0.5, 0.3, 0.2, 0.1])
    grad = np.ones(5) * 0.1
    updated = relaxed_update(vec, grad, params)

    assert updated.shape == vec.shape


def test_invalid_alpha_is_rejected():
    with pytest.raises(ValueError):
        GovernanceParams(alpha=1.5)
