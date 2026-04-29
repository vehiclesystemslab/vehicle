"""
vehicle/governance.py

Projection-governance operator for VEHICLE 3D with E.I.A.R.(V).
Implements a relaxed projection update around an approximate local gradient:

    V_op(S_i) = P_K[S_i - gamma * g_i]
    S_i(t+1) = (1-alpha) S_i(t) + alpha V_op(S_i(t))

At this stage, g_i is an explicit computational approximation, not a claim of
an exact analytical gradient of the full global tension functional.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np


@dataclass(frozen=True)
class GovernanceParams:
    """Parameters for the projection-governance update."""

    gamma: float = 0.05
    alpha: float = 0.3
    tau_limit: float = 0.5
    clip_range: Tuple[float, float] = (-2.0, 2.0)

    def __post_init__(self) -> None:
        if self.gamma < 0:
            raise ValueError("gamma must be non-negative.")
        if not 0.0 <= self.alpha <= 1.0:
            raise ValueError("alpha must be within [0, 1].")
        if self.tau_limit < 0:
            raise ValueError("tau_limit must be non-negative.")
        if len(self.clip_range) != 2:
            raise ValueError("clip_range must contain exactly two values.")
        low, high = float(self.clip_range[0]), float(self.clip_range[1])
        if low > high:
            raise ValueError("clip_range lower bound must be <= upper bound.")
        object.__setattr__(self, "gamma", float(self.gamma))
        object.__setattr__(self, "alpha", float(self.alpha))
        object.__setattr__(self, "tau_limit", float(self.tau_limit))
        object.__setattr__(self, "clip_range", (low, high))


def _as_state_vector(vec: np.ndarray, name: str = "state_vec") -> np.ndarray:
    arr = np.asarray(vec, dtype=float).reshape(-1)
    if arr.size == 0:
        raise ValueError(f"{name} must not be empty.")
    return arr


def coherence_measure(S: np.ndarray) -> float:
    """Baseline internal coherence measure Θ(S) = ||S - mean(S)||²."""
    arr = _as_state_vector(S, "S")
    dev = arr - float(np.mean(arr))
    return float(np.dot(dev, dev))


def project_to_coherent_region(
    S: np.ndarray,
    tau_limit: float,
    clip_range: Tuple[float, float] = (-2.0, 2.0),
) -> np.ndarray:
    """Project a state vector into a bounded coherence region K."""
    if tau_limit < 0:
        raise ValueError("tau_limit must be non-negative.")
    low, high = float(clip_range[0]), float(clip_range[1])
    if low > high:
        raise ValueError("clip_range lower bound must be <= upper bound.")

    vec = _as_state_vector(S, "S").copy()
    mean = float(np.mean(vec))
    dev = vec - mean
    theta = float(np.dot(dev, dev))

    if theta > float(tau_limit):
        scale = np.sqrt(float(tau_limit) / (theta + 1e-12))
        vec = mean + dev * scale

    return np.clip(vec, low, high)


def approximate_gradient(state_vec: np.ndarray, neighbor_mean: np.ndarray | None = None) -> np.ndarray:
    """
    Approximate local relational gradient.

    If a neighbor mean is supplied, the gradient points away from local relational
    compatibility. If omitted, the origin is used as the neutral baseline.
    """
    state = _as_state_vector(state_vec, "state_vec")
    if neighbor_mean is None:
        neighbor = np.zeros_like(state)
    else:
        neighbor = _as_state_vector(neighbor_mean, "neighbor_mean")
        if neighbor.shape != state.shape:
            raise ValueError("state_vec and neighbor_mean must have the same shape.")
    return state - neighbor


def v_operator(state_vec: np.ndarray, gradient_vec: np.ndarray, params: GovernanceParams) -> np.ndarray:
    """Projection-governance operator V_op."""
    state = _as_state_vector(state_vec, "state_vec")
    grad = _as_state_vector(gradient_vec, "gradient_vec")
    if state.shape != grad.shape:
        raise ValueError("state_vec and gradient_vec must have the same shape.")
    raw = state - params.gamma * grad
    return project_to_coherent_region(raw, tau_limit=params.tau_limit, clip_range=params.clip_range)


# Mathematical alias preserved for readability in papers and notebooks.
V_op = v_operator


def relaxed_update(state_vec: np.ndarray, gradient_vec: np.ndarray, params: GovernanceParams) -> np.ndarray:
    """Relaxed update S_i(t+1) = (1-alpha)S_i(t) + alpha V_op(S_i(t))."""
    state = _as_state_vector(state_vec, "state_vec")
    projected = v_operator(state, gradient_vec, params)
    updated = (1.0 - params.alpha) * state + params.alpha * projected
    return np.clip(updated, params.clip_range[0], params.clip_range[1])


__all__ = [
    "GovernanceParams",
    "coherence_measure",
    "project_to_coherent_region",
    "approximate_gradient",
    "v_operator",
    "V_op",
    "relaxed_update",
]
