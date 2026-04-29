import networkx as nx
import pandas as pd

from vehicle.eiarv import DynamicsParams, run_dynamics, step_eiarv
from vehicle.governance import GovernanceParams
from vehicle.observables import evaluate_history_observables
from vehicle.state import initialize_random_state


def _line_graph(n=5):
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for i in range(n - 1):
        g.add_edge(i, i + 1, weight=1.0)
    return g


def test_step_eiarv_advances_time():
    system = initialize_random_state(5, seed=42)
    graph = _line_graph(5)
    new_system, diag = step_eiarv(system, graph, GovernanceParams(), DynamicsParams(max_iterations=1))

    assert new_system.time == system.time + 1
    assert "tension_before" in diag
    assert "tension_after" in diag
    assert isinstance(diag["h1_ok"], bool)


def test_run_dynamics_returns_history_with_initial_row():
    system = initialize_random_state(5, seed=42)
    graph = _line_graph(5)
    final_system, history = run_dynamics(
        system,
        graph,
        GovernanceParams(),
        DynamicsParams(max_iterations=3),
        include_initial=True,
    )

    assert final_system.time == 3
    assert len(history) == 4
    assert history[0]["time"] == 0
    obs = evaluate_history_observables(pd.DataFrame(history))
    assert "H1" in obs
