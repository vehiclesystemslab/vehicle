"""
vehicle/observables.py

Diagnostic observables for hypotheses H1-H5 in VEHICLE 3D with E.I.A.R.(V).
These diagnostics are computational indicators, not final proof objects.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


def _as_float_array(values: Iterable[float], name: str) -> np.ndarray:
    arr = np.asarray(list(values), dtype=float).reshape(-1)
    if arr.size == 0:
        raise ValueError(f"{name} must not be empty.")
    return arr


def h1_monotone_dissipation(tensions: Iterable[float], epsilon: float = 1e-6) -> dict:
    """Check whether T(t+1) <= T(t) + epsilon across a tension history."""
    arr = _as_float_array(tensions, "tensions")
    if epsilon < 0:
        raise ValueError("epsilon must be non-negative.")

    violations: list[int] = []
    increases: list[float] = []
    for i in range(1, len(arr)):
        increase = float(arr[i] - arr[i - 1])
        increases.append(increase)
        if increase > epsilon:
            violations.append(i)

    return {
        "name": "H1",
        "ok": len(violations) == 0,
        "violations": violations,
        "violation_count": len(violations),
        "max_increase": float(max(increases)) if increases else 0.0,
    }


def h2_observable_non_factorization(history_df: pd.DataFrame) -> dict:
    """
    Baseline diagnostic for coupled external/internal variation.

    This is an indicator only. It should not be described as a mathematical proof
    of non-factorization.
    """
    required = {"external_tension", "internal_tension"}
    if not required.issubset(history_df.columns):
        return {"name": "H2", "ok": False, "reason": "missing columns"}
    if len(history_df) < 2:
        return {"name": "H2", "ok": False, "reason": "insufficient data"}

    internal = history_df["internal_tension"].astype(float)
    external = history_df["external_tension"].astype(float)
    internal_var = float(internal.var(ddof=0))
    external_var = float(external.var(ddof=0))
    correlation = float(internal.corr(external)) if internal_var > 0 and external_var > 0 else 0.0

    return {
        "name": "H2",
        "ok": bool(internal_var > 0 and external_var > 0),
        "internal_variance": internal_var,
        "external_variance": external_var,
        "internal_external_correlation": correlation,
    }


def h3_separation_of_time_scales(internal_times: Iterable[float], external_times: Iterable[float]) -> dict:
    """Check whether the mean internal time scale is smaller than the external one."""
    internal = _as_float_array(internal_times, "internal_times")
    external = _as_float_array(external_times, "external_times")
    tau_int = float(np.mean(internal))
    tau_ext = float(np.mean(external))
    return {"name": "H3", "ok": bool(tau_int < tau_ext), "tau_int": tau_int, "tau_ext": tau_ext}


def h4_subconvergence_without_total_consensus(tensions: Iterable[float], tolerance: float = 1e-3) -> dict:
    """Detect a low-variation positive plateau in the final tension window."""
    arr = _as_float_array(tensions, "tensions")
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative.")
    if len(arr) < 3:
        return {"name": "H4", "ok": False, "reason": "insufficient data"}

    window = arr[-5:] if len(arr) >= 5 else arr
    std = float(np.std(window))
    mean = float(np.mean(window))
    return {"name": "H4", "ok": bool(std < tolerance and mean > 0), "window_std": std, "window_mean": mean}


def h5_topological_filtering(initial_amplitudes: Iterable[float], final_amplitudes: Iterable[float]) -> dict:
    """Compare initial and final perturbation amplitude norms."""
    initial = _as_float_array(initial_amplitudes, "initial_amplitudes")
    final = _as_float_array(final_amplitudes, "final_amplitudes")
    if len(initial) != len(final):
        return {"name": "H5", "ok": False, "reason": "length mismatch"}

    init_norm = float(np.linalg.norm(initial))
    final_norm = float(np.linalg.norm(final))
    return {"name": "H5", "ok": bool(final_norm <= init_norm), "initial_norm": init_norm, "final_norm": final_norm}


def evaluate_history_observables(history_df: pd.DataFrame, epsilon: float = 1e-6) -> dict[str, dict]:
    """Evaluate available history-based observables from an experiment history table."""
    if "total_tension" not in history_df.columns:
        raise ValueError("history_df must contain a 'total_tension' column.")

    tensions = history_df["total_tension"].astype(float).to_list()
    results = {"H1": h1_monotone_dissipation(tensions, epsilon=epsilon)}
    results["H2"] = h2_observable_non_factorization(history_df)
    results["H4"] = h4_subconvergence_without_total_consensus(tensions)
    return results


__all__ = [
    "h1_monotone_dissipation",
    "h2_observable_non_factorization",
    "h3_separation_of_time_scales",
    "h4_subconvergence_without_total_consensus",
    "h5_topological_filtering",
    "evaluate_history_observables",
]
