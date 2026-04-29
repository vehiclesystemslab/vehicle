"""
vehicle/attractors.py

Operational attractor taxonomy for VEHICLE 3D with E.I.A.R.(V).
Maps local and regime-level diagnostic conditions to A0-A6 classes.

Important
---------
This module implements a diagnostic taxonomy. It is intended to support
interpretable experiments and regime comparison; it is not, by itself, a
mathematical proof of convergence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np


@dataclass(frozen=True)
class AttractorThresholds:
    """Threshold set for operational A0-A6 classification."""

    tau_limit: float = 0.5
    critical_spin_threshold: float = 1.0
    rigid_internal_coupling: float = 0.75
    fluid_external_coupling: float = 0.75
    recovery_tension_threshold: float = 0.25
    mitosis_pressure_threshold: float = 0.7

    def __post_init__(self) -> None:
        if self.tau_limit < 0:
            raise ValueError("tau_limit must be non-negative.")
        if self.critical_spin_threshold < 0:
            raise ValueError("critical_spin_threshold must be non-negative.")
        if self.recovery_tension_threshold < 0:
            raise ValueError("recovery_tension_threshold must be non-negative.")
        if self.mitosis_pressure_threshold < 0:
            raise ValueError("mitosis_pressure_threshold must be non-negative.")


def _as_state_vector(state_vec: np.ndarray) -> np.ndarray:
    vec = np.asarray(state_vec, dtype=float)
    if vec.shape != (5,):
        raise ValueError(f"Expected a 5-dimensional E.I.A.R.(V) vector, got shape {vec.shape}.")
    return vec


def classify_state(
    state_vec: np.ndarray,
    local_tension: float,
    thresholds: AttractorThresholds = AttractorThresholds(),
    expanded: bool = False,
    recovery_active: bool = False,
) -> str:
    """
    Return an A0-A6 diagnostic label for a single node state.

    A0: coherent / governed baseline
    A1: critical spin or jointly high incoherence and tension
    A2: recovery basin
    A3: intermediate / transitional state
    A4: expansion or mitosis pressure
    A5: rigid-local coherence under excessive local tension
    A6: internally incoherent but not locally overloaded
    """
    vec = _as_state_vector(state_vec)
    local_tension = float(local_tension)
    if local_tension < 0:
        raise ValueError("local_tension must be non-negative.")

    E = float(vec[0])
    coherence = float(np.var(vec))

    if recovery_active and local_tension <= thresholds.recovery_tension_threshold:
        return "A2"

    if expanded and local_tension > thresholds.mitosis_pressure_threshold:
        return "A4"

    if abs(E) >= thresholds.critical_spin_threshold:
        return "A1"

    if coherence <= thresholds.tau_limit and local_tension <= thresholds.tau_limit:
        return "A0"

    if coherence <= thresholds.tau_limit and local_tension > thresholds.tau_limit:
        return "A5"

    if coherence > thresholds.tau_limit and local_tension <= thresholds.tau_limit:
        return "A6"

    if coherence > thresholds.tau_limit and local_tension > thresholds.tau_limit:
        return "A1"

    return "A3"


def classify_regime(
    internal_coupling: float,
    external_coupling: float,
    governance_strength: float,
    thresholds: AttractorThresholds = AttractorThresholds(),
) -> str:
    """
    Classify a regime-level tendency as an A0-A6 diagnostic label.

    This is a diagnostic helper for experiments, not a theorem.
    """
    internal_coupling = float(internal_coupling)
    external_coupling = float(external_coupling)
    governance_strength = float(governance_strength)

    if min(internal_coupling, external_coupling, governance_strength) < 0:
        raise ValueError("Coupling and governance values must be non-negative.")

    if governance_strength >= 0.7:
        return "A0"

    if (
        internal_coupling >= thresholds.rigid_internal_coupling
        and external_coupling <= 0.35
    ):
        return "A5"

    if (
        external_coupling >= thresholds.fluid_external_coupling
        and internal_coupling <= 0.35
    ):
        return "A6"

    return "A3"


def summarize_attractors(labels: list[str]) -> Dict[str, int]:
    """Count A0-A6 labels in a sequence."""
    classes = [f"A{i}" for i in range(7)]
    invalid = sorted(set(labels) - set(classes))
    if invalid:
        raise ValueError(f"Invalid attractor labels: {invalid}")
    return {cls: int(sum(label == cls for label in labels)) for cls in classes}
