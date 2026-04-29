"""
vehicle/tension.py

Tension functional for VEHICLE 3D with E.I.A.R.(V).
Defines external relational tension, internal coherence tension, local tension,
and total system tension.
"""

from __future__ import annotations

from typing import Callable

import networkx as nx
import numpy as np

from vehicle.state import NodeState, SystemState


def euclidean_discrepancy(S_i: np.ndarray, S_j: np.ndarray) -> float:
    """Default discrepancy measure: D(S_i, S_j) = ||S_i - S_j||_2."""
    a = np.asarray(S_i, dtype=float).reshape(-1)
    b = np.asarray(S_j, dtype=float).reshape(-1)
    if a.shape != b.shape:
        raise ValueError(f"State vectors must have the same shape, got {a.shape} and {b.shape}.")
    return float(np.linalg.norm(a - b))


def internal_incoherence_quadratic(S: np.ndarray) -> float:
    """
    Baseline isotropic internal incoherence measure.

    Θ(S) = ||S - mean(S)||².
    Future versions may introduce component weights or normalized coordinates.
    """
    arr = np.asarray(S, dtype=float).reshape(-1)
    deviation = arr - float(np.mean(arr))
    return float(np.dot(deviation, deviation))


def _get_required_node(system: SystemState, node_id: int) -> NodeState:
    node = system.get_node(node_id)
    if node is None:
        raise ValueError(f"Graph references missing node_id={node_id}.")
    return node


def compute_external_tension(
    system: SystemState,
    graph: nx.Graph,
    discrepancy_fn: Callable[[np.ndarray, np.ndarray], float] = euclidean_discrepancy,
) -> float:
    """Compute T_ext(X) = Σ_(i,j) ω_ij D(S_i, S_j)."""
    T_ext = 0.0
    for i, j in graph.edges():
        node_i = _get_required_node(system, i)
        node_j = _get_required_node(system, j)
        weight = float(graph[i][j].get("weight", 1.0))
        T_ext += weight * float(discrepancy_fn(node_i.to_vector(), node_j.to_vector()))
    return float(T_ext)


def compute_internal_tension(
    system: SystemState,
    lambda_coupling: float = 1.0,
    coherence_fn: Callable[[np.ndarray], float] = internal_incoherence_quadratic,
) -> float:
    """Compute T_int(X) = λ Σ_i C(S_i)."""
    lam = float(lambda_coupling)
    if lam < 0:
        raise ValueError("lambda_coupling must be non-negative.")
    return float(lam * sum(float(coherence_fn(node.to_vector())) for node in system.nodes))


def compute_total_tension(
    system: SystemState,
    graph: nx.Graph,
    lambda_coupling: float = 1.0,
    discrepancy_fn: Callable[[np.ndarray, np.ndarray], float] = euclidean_discrepancy,
    coherence_fn: Callable[[np.ndarray], float] = internal_incoherence_quadratic,
) -> dict[str, float]:
    """Compute T(X) = T_ext(X) + T_int(X)."""
    T_ext = compute_external_tension(system, graph, discrepancy_fn)
    T_int = compute_internal_tension(system, lambda_coupling, coherence_fn)
    return {"total": float(T_ext + T_int), "external": float(T_ext), "internal": float(T_int)}


def compute_local_tension(
    node: NodeState,
    neighbors: list[NodeState],
    graph: nx.Graph,
    lambda_coupling: float = 1.0,
    discrepancy_fn: Callable[[np.ndarray, np.ndarray], float] = euclidean_discrepancy,
    coherence_fn: Callable[[np.ndarray], float] = internal_incoherence_quadratic,
) -> dict[str, float]:
    """Compute local tension around a single node."""
    S_i = node.to_vector()
    T_ext_local = 0.0

    for neighbor in neighbors:
        if graph.has_edge(node.node_id, neighbor.node_id):
            weight = float(graph[node.node_id][neighbor.node_id].get("weight", 1.0))
            T_ext_local += weight * float(discrepancy_fn(S_i, neighbor.to_vector()))

    T_int_local = float(lambda_coupling) * float(coherence_fn(S_i))
    return {
        "total": float(T_ext_local + T_int_local),
        "external": float(T_ext_local),
        "internal": float(T_int_local),
    }
