import numpy as np
import pandas as pd
import networkx as nx

from vehicle.state import NodeState, SystemState, initialize_random_state
from vehicle.tension import compute_total_tension, internal_incoherence_quadratic
from vehicle.governance import GovernanceParams, V_op, relaxed_update
from vehicle.eiarv import DynamicsParams, step_eiarv
from vehicle.observables import h1_monotone_dissipation
from vehicle.attractors import classify_state, summarize_attractors, AttractorThresholds


def test_node_state_vector_roundtrip():
    node = NodeState(E=1, I=2, A=3, R=4, V=5, node_id=7)
    vec = node.to_vector()
    node2 = NodeState.from_vector(vec, node_id=7)
    assert np.allclose(vec, node2.to_vector())


def test_initialize_random_state_size():
    system = initialize_random_state(5, seed=123)
    assert len(system.nodes) == 5
    assert system.to_matrix().shape == (5, 5)


def test_internal_incoherence_nonnegative():
    s = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
    assert internal_incoherence_quadratic(s) == 0.0


def test_governance_projection_shape():
    s = np.array([2.0, -2.0, 1.0, 0.0, 0.5])
    g = GovernanceParams()
    out = V_op(s, s, g)
    assert out.shape == (5,)


def test_relaxed_update_shape():
    s = np.array([1, 2, 3, 4, 5], dtype=float)
    g = GovernanceParams()
    out = relaxed_update(s, s, g)
    assert out.shape == (5,)


def test_h1_basic():
    res = h1_monotone_dissipation([3.0, 2.0, 2.0, 1.5])
    assert res['ok'] is True


def test_attractor_summarize():
    labels = ['A0', 'A0', 'A4', 'A6']
    summary = summarize_attractors(labels)
    assert summary['A0'] == 2
    assert summary['A4'] == 1
    assert summary['A6'] == 1


def test_classify_state_returns_label():
    s = np.array([0.1, 0.1, 0.1, 0.1, 0.1])
    label = classify_state(s, local_tension=0.1, thresholds=AttractorThresholds())
    assert label in {'A0','A1','A2','A3','A4','A5','A6'}
