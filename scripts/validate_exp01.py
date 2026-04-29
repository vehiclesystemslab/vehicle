"""
scripts/validate_exp01.py

Small automatic validation driver for exp01_base_dissipation.
Runs a short smoke validation and prints the main diagnostics.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import networkx as nx
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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


def main() -> None:
    seed = 42
    graph = build_graph(seed=seed)
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
    thresholds = AttractorThresholds()

    tensions = [
        float(
            compute_total_tension(
                system,
                graph,
                lambda_coupling=dyn.lambda_coupling,
            )["total"]
        )
    ]
    labels = []

    for _ in range(dyn.max_iterations):
        system, diag = step_eiarv(system, graph, gov, dyn)
        tensions.append(float(diag["tension_after"]["total"]))
        labels.append(
            classify_state(
                system.nodes[0].to_vector(),
                local_tension=tensions[-1],
                thresholds=thresholds,
            )
        )

    summary = {
        "seed": seed,
        "steps": dyn.max_iterations,
        "initial_tension": tensions[0],
        "final_tension": tensions[-1],
        "delta_tension": tensions[-1] - tensions[0],
        "finite_tension_values": bool(all(np.isfinite(t) for t in tensions)),
        "h1_like_smoke_check": bool(tensions[-1] <= tensions[0] + 10.0),
        "attractors": summarize_attractors(labels),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
