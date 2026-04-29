import json

import networkx as nx
import numpy as np

from vehicle.attractors import AttractorThresholds, classify_state, summarize_attractors
from vehicle.eiarv import DynamicsParams, step_eiarv
from vehicle.governance import GovernanceParams
from vehicle.state import initialize_random_state
from vehicle.tension import compute_total_tension


def build_graph(n=6, p=0.4, seed=42):
    graph = nx.erdos_renyi_graph(n=n, p=p, seed=seed)
    rng = np.random.default_rng(seed)
    for u, v in graph.edges():
        graph[u][v]["weight"] = float(rng.uniform(0.5, 1.5))
    return graph


def test_exp01_integration_smoke(tmp_path):
    seed = 42
    graph = build_graph()
    system = initialize_random_state(6, seed=seed)
    gov = GovernanceParams(
        gamma=0.05,
        alpha=0.3,
        tau_limit=0.5,
        clip_range=(-2.0, 2.0),
    )
    dyn = DynamicsParams(
        lambda_coupling=1.0,
        max_iterations=5,
        epsilon_tolerance=1e-6,
    )

    tensions = []
    labels = []
    thresholds = AttractorThresholds()

    t0 = compute_total_tension(
        system,
        graph,
        lambda_coupling=dyn.lambda_coupling,
    )["total"]
    tensions.append(float(t0))

    for _ in range(dyn.max_iterations):
        system, diag = step_eiarv(system, graph, gov, dyn)
        t = float(diag["tension_after"]["total"])
        tensions.append(t)
        labels.append(
            classify_state(
                system.nodes[0].to_vector(),
                local_tension=t,
                thresholds=thresholds,
            )
        )

    assert len(tensions) == dyn.max_iterations + 1
    assert all(np.isfinite(t) for t in tensions)
    assert tensions[-1] <= tensions[0] + 10.0

    summary = summarize_attractors(labels)
    assert sum(summary.values()) == len(labels)

    out = tmp_path / "integration_summary.json"
    out.write_text(
        json.dumps({"tensions": tensions, "labels": labels}, indent=2),
        encoding="utf-8",
    )
    assert out.exists()
