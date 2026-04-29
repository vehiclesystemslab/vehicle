"""
vehicle/eiarv.py

Core E.I.A.R.(V) node dynamics for VEHICLE 3D.
Tracks the principal state dimensions E, I, A, R, V and applies the
projection-governed relaxed update in synchronous discrete time.
"""

from __future__ import annotations

from dataclasses import dataclass

import networkx as nx
import numpy as np

from vehicle.governance import GovernanceParams, approximate_gradient, relaxed_update
from vehicle.state import STATE_DIMENSION, SystemState
from vehicle.tension import compute_total_tension


@dataclass(frozen=True)
class DynamicsParams:
    """Global dynamics parameters for E.I.A.R.(V) simulations."""

    lambda_coupling: float = 1.0
    max_iterations: int = 50
    epsilon_tolerance: float = 1e-6
    critical_spin_threshold: float = 1.0
    update_clip_range: tuple[float, float] = (-2.0, 2.0)

    def __post_init__(self) -> None:
        if self.lambda_coupling < 0:
            raise ValueError("lambda_coupling must be non-negative.")
        if self.max_iterations < 0:
            raise ValueError("max_iterations must be non-negative.")
        if self.epsilon_tolerance < 0:
            raise ValueError("epsilon_tolerance must be non-negative.")
        low, high = float(self.update_clip_range[0]), float(self.update_clip_range[1])
        if low > high:
            raise ValueError("update_clip_range lower bound must be <= upper bound.")
        object.__setattr__(self, "lambda_coupling", float(self.lambda_coupling))
        object.__setattr__(self, "max_iterations", int(self.max_iterations))
        object.__setattr__(self, "epsilon_tolerance", float(self.epsilon_tolerance))
        object.__setattr__(self, "critical_spin_threshold", float(self.critical_spin_threshold))
        object.__setattr__(self, "update_clip_range", (low, high))


def neighbor_mean_vector(system: SystemState, graph: nx.Graph, node_id: int) -> np.ndarray:
    """Return the mean E.I.A.R.(V) vector of a node's neighbors."""
    node = system.get_node(node_id)
    if node is None:
        raise ValueError(f"Cannot compute neighbor mean for missing node_id={node_id}.")

    neighbor_states = []
    for neighbor_id in graph.neighbors(node_id):
        neighbor = system.get_node(neighbor_id)
        if neighbor is None:
            raise ValueError(f"Graph references missing neighbor node_id={neighbor_id}.")
        neighbor_states.append(neighbor.to_vector())

    if not neighbor_states:
        return node.to_vector().copy()

    return np.mean(neighbor_states, axis=0)


def update_node_state(node_vec: np.ndarray, neighbor_vec: np.ndarray, gov: GovernanceParams) -> np.ndarray:
    """Update a single node vector under approximate local compatibility pressure."""
    gradient = approximate_gradient(node_vec, neighbor_vec)
    return relaxed_update(node_vec, gradient, gov)


def _check_graph_state_compatibility(system: SystemState, graph: nx.Graph) -> None:
    state_ids = set(system.node_ids())
    graph_ids = set(graph.nodes())
    missing_in_state = graph_ids - state_ids
    if missing_in_state:
        raise ValueError(f"Graph contains node ids not present in system: {sorted(missing_in_state)}")


def step_eiarv(
    system: SystemState,
    graph: nx.Graph,
    gov: GovernanceParams,
    dyn: DynamicsParams,
) -> tuple[SystemState, dict]:
    """Advance the global system by one synchronous discrete step."""
    _check_graph_state_compatibility(system, graph)

    current_tension = compute_total_tension(system, graph, lambda_coupling=dyn.lambda_coupling)
    new_system = system.copy()

    for node in new_system.nodes:
        nb_mean = neighbor_mean_vector(system, graph, node.node_id)
        new_vec = update_node_state(node.to_vector(), nb_mean, gov)
        clipped = np.clip(new_vec, dyn.update_clip_range[0], dyn.update_clip_range[1])
        node.E, node.I, node.A, node.R, node.V = clipped.tolist()

    new_system.time = int(system.time) + 1
    next_tension = compute_total_tension(new_system, graph, lambda_coupling=dyn.lambda_coupling)

    diagnostics = {
        "tension_before": current_tension,
        "tension_after": next_tension,
        "delta_total_tension": float(next_tension["total"] - current_tension["total"]),
        "h1_ok": bool(next_tension["total"] <= current_tension["total"] + dyn.epsilon_tolerance),
        "num_nodes": int(len(new_system.nodes)),
        "critical_nodes": int(sum(abs(n.E) >= dyn.critical_spin_threshold for n in new_system.nodes)),
    }
    return new_system, diagnostics


def _history_row(time: int, tension: dict[str, float], h1_ok: bool, critical_nodes: int, num_nodes: int) -> dict:
    return {
        "time": int(time),
        "total_tension": float(tension["total"]),
        "external_tension": float(tension["external"]),
        "internal_tension": float(tension["internal"]),
        "h1_ok": bool(h1_ok),
        "critical_nodes": int(critical_nodes),
        "num_nodes": int(num_nodes),
    }


def run_dynamics(
    system: SystemState,
    graph: nx.Graph,
    gov: GovernanceParams,
    dyn: DynamicsParams,
    include_initial: bool = True,
) -> tuple[SystemState, list[dict]]:
    """Run E.I.A.R.(V) dynamics and return final state plus iteration history."""
    _check_graph_state_compatibility(system, graph)

    history: list[dict] = []
    current = system.copy()

    if include_initial:
        t0 = compute_total_tension(current, graph, lambda_coupling=dyn.lambda_coupling)
        history.append(_history_row(current.time, t0, True, 0, len(current.nodes)))

    for _ in range(dyn.max_iterations):
        current, diag = step_eiarv(current, graph, gov, dyn)
        history.append(
            _history_row(
                current.time,
                diag["tension_after"],
                diag["h1_ok"],
                diag["critical_nodes"],
                diag["num_nodes"],
            )
        )

    return current, history


__all__ = [
    "DynamicsParams",
    "neighbor_mean_vector",
    "update_node_state",
    "step_eiarv",
    "run_dynamics",
]
