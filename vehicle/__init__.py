"""VEHICLE Systems Lab computational core."""

from .state import NodeState, SystemState, initialize_random_state
from .tension import (
    compute_external_tension,
    compute_internal_tension,
    compute_local_tension,
    compute_total_tension,
    euclidean_discrepancy,
    internal_incoherence_quadratic,
)
from .governance import GovernanceParams, V_op, relaxed_update, v_operator
from .eiarv import DynamicsParams, run_dynamics, step_eiarv
from .observables import (
    evaluate_history_observables,
    h1_monotone_dissipation,
    h2_observable_non_factorization,
    h3_separation_of_time_scales,
    h4_subconvergence_without_total_consensus,
    h5_topological_filtering,
)
from .attractors import (
    AttractorThresholds,
    classify_regime,
    classify_state,
    summarize_attractors,
)

__version__ = "0.1.0"

__all__ = [
    "NodeState",
    "SystemState",
    "initialize_random_state",
    "euclidean_discrepancy",
    "internal_incoherence_quadratic",
    "compute_external_tension",
    "compute_internal_tension",
    "compute_total_tension",
    "compute_local_tension",
    "GovernanceParams",
    "V_op",
    "v_operator",
    "relaxed_update",
    "DynamicsParams",
    "step_eiarv",
    "run_dynamics",
    "h1_monotone_dissipation",
    "h2_observable_non_factorization",
    "h3_separation_of_time_scales",
    "h4_subconvergence_without_total_consensus",
    "h5_topological_filtering",
    "evaluate_history_observables",
    "AttractorThresholds",
    "classify_state",
    "classify_regime",
    "summarize_attractors",
]
