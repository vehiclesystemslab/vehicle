"""
experiments/exp01_base_dissipation.py

Baseline dissipation experiment for VEHICLE Systems Lab.

Purpose
-------
Evaluate the first reproducible dissipation experiment for the VEHICLE 3D
E.I.A.R.(V) computational layer.

This script does not claim a proof of monotone dissipation. It performs an
empirical H1 check under the configured update rule:

    H1: T(X(t+1)) <= T(X(t)) + epsilon

Outputs
-------
For each run, the script writes:

- config_used.yaml
- graph_edges.csv
- history.csv
- final_state.csv
- metrics_summary.json
- run.log
- fig_total_tension.png, if generate_figures is enabled

Run
---
From the repository root:

    python experiments/exp01_base_dissipation.py

or, after installing the package:

    python -m experiments.exp01_base_dissipation
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np
import pandas as pd
import yaml

# Allow direct execution from the repository root without requiring PYTHONPATH.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vehicle.state import SystemState, initialize_random_state
from vehicle.tension import compute_total_tension


CFG_PATH = ROOT / "configs" / "experiments" / "exp01_base_dissipation.yaml"


def load_config(path: Path) -> dict[str, Any]:
    """Load a YAML configuration file."""
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    if not isinstance(cfg, dict):
        raise ValueError(f"Invalid configuration format: {path}")

    return cfg


def build_graph(
    n: int,
    p: float,
    seed: int,
    weight_range: tuple[float, float] = (0.5, 1.5),
) -> nx.Graph:
    """
    Build a weighted Erdos-Renyi graph.

    Parameters
    ----------
    n:
        Number of nodes.
    p:
        Edge probability.
    seed:
        Reproducibility seed.
    weight_range:
        Inclusive lower/upper range used to sample edge weights.

    Returns
    -------
    nx.Graph
        Weighted undirected graph.
    """
    if n <= 0:
        raise ValueError("Number of nodes must be positive.")

    if not 0.0 <= p <= 1.0:
        raise ValueError("Edge probability must be in [0, 1].")

    low, high = weight_range
    if low < 0 or high < low:
        raise ValueError("Invalid edge weight range.")

    graph = nx.erdos_renyi_graph(n=n, p=p, seed=seed)
    rng = np.random.default_rng(seed)

    for u, v in graph.edges():
        graph[u][v]["weight"] = float(rng.uniform(low, high))

    return graph


def project_state(
    vec: np.ndarray,
    tau_limit: float,
    clip_range: tuple[float, float] = (-2.0, 2.0),
) -> np.ndarray:
    """
    Project a node state into a bounded admissible region.

    The current projection is a baseline isotropic coherence projection:
    if internal quadratic incoherence exceeds tau_limit, deviations from
    the component mean are radially contracted.

    This is a first operational projection, not the final VEHICLE governance
    operator.
    """
    if tau_limit <= 0:
        raise ValueError("tau_limit must be positive.")

    clip_low, clip_high = clip_range
    if clip_high < clip_low:
        raise ValueError("Invalid clip_range: upper bound is below lower bound.")

    projected = np.asarray(vec, dtype=float).copy()

    mean = float(projected.mean())
    deviation = projected - mean
    theta = float(np.dot(deviation, deviation))

    if theta > tau_limit:
        scale = float(np.sqrt(tau_limit / (theta + 1e-12)))
        projected = mean + deviation * scale

    projected = np.clip(projected, clip_low, clip_high)
    return projected


def step_system(
    system: SystemState,
    graph: nx.Graph,
    params: dict[str, Any],
    dynamics: dict[str, Any],
    validation: dict[str, Any],
) -> tuple[SystemState, dict[str, float], dict[str, float], bool]:
    """
    Advance the system by one synchronous Jacobi-style update.

    Important
    ---------
    Neighbor means are computed from the previous system state, not from
    partially updated nodes. This makes the experiment easier to audit and
    avoids accidental Gauss-Seidel behavior.
    """
    alpha = float(params["alpha_relaxation"])
    gamma = float(params["gamma_gradient"])
    tau_limit = float(params["tau_limit"])
    lambda_coupling = float(params["lambda_coupling"])

    clip_range = tuple(dynamics.get("clip_range", (-2.0, 2.0)))
    epsilon = float(validation.get("epsilon_tolerance", 1.0e-6))

    if not 0.0 <= alpha <= 1.0:
        raise ValueError("alpha_relaxation must be in [0, 1].")

    if gamma < 0:
        raise ValueError("gamma_gradient must be non-negative.")

    tension_before = compute_total_tension(
        system,
        graph,
        lambda_coupling=lambda_coupling,
    )

    previous_vectors = {
        node.node_id: node.to_vector().copy()
        for node in system.nodes
    }

    new_system = system.copy()

    for node in new_system.nodes:
        vec = previous_vectors[node.node_id]

        neighbor_vectors = [
            previous_vectors[n_id]
            for n_id in graph.neighbors(node.node_id)
            if n_id in previous_vectors
        ]

        neighbor_mean = (
            np.mean(neighbor_vectors, axis=0)
            if neighbor_vectors
            else vec
        )

        # Baseline relational relaxation toward local compatibility.
        gradient = vec - neighbor_mean
        updated = vec - gamma * gradient

        if bool(dynamics.get("projection_enabled", True)):
            updated = project_state(
                updated,
                tau_limit=tau_limit,
                clip_range=clip_range,
            )

        relaxed = (1.0 - alpha) * vec + alpha * updated

        if bool(dynamics.get("clipping_enabled", True)):
            relaxed = np.clip(relaxed, clip_range[0], clip_range[1])

        node.E, node.I, node.A, node.R, node.V = [float(x) for x in relaxed.tolist()]

    new_system.time = system.time + 1

    tension_after = compute_total_tension(
        new_system,
        graph,
        lambda_coupling=lambda_coupling,
    )

    h1_ok = bool(tension_after["total"] <= tension_before["total"] + epsilon)

    return new_system, tension_before, tension_after, h1_ok


def make_run_dir(base_results_dir: Path, seed: int) -> Path:
    """Create a timestamped, seed-stamped run directory."""
    timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
    run_dir = base_results_dir / f"run_{timestamp}_seed{seed}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def save_graph_edges(graph: nx.Graph, path: Path) -> None:
    """Save weighted graph edges as CSV."""
    rows = [
        {
            "source": int(u),
            "target": int(v),
            "weight": float(data.get("weight", 1.0)),
        }
        for u, v, data in graph.edges(data=True)
    ]
    pd.DataFrame(rows, columns=["source", "target", "weight"]).to_csv(
        path,
        index=False,
    )


def save_tension_figure(history_df: pd.DataFrame, path: Path) -> None:
    """Save a simple total tension diagnostic figure."""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.plot(history_df["time"], history_df["total_tension"], marker="o", linewidth=1.5)
    ax.set_title("VEHICLE Experiment 01 — Total Tension")
    ax.set_xlabel("Discrete time step")
    ax.set_ylabel("Total tension T(X)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> None:
    cfg = load_config(CFG_PATH)

    exp = cfg["experiment"]
    rep = cfg["reproducibility"]
    net = cfg["network"]
    init = cfg["initial_state"]
    params = cfg["parameters"]
    dyn = cfg["dynamics"]
    val = cfg["validation"]
    out = cfg["output"]

    seed = int(rep["seed"])

    base_results_dir = (ROOT / out["results_dir"]).resolve()
    run_dir = make_run_dir(base_results_dir, seed)

    graph = build_graph(
        n=int(net["initial_nodes"]),
        p=float(net["edge_probability"]),
        seed=seed,
        weight_range=tuple(net.get("edge_weight_range", [0.5, 1.5])),
    )

    system = initialize_random_state(
        N=int(net["initial_nodes"]),
        seed=seed,
        E_range=tuple(init["E_range"]),
        I_range=tuple(init["I_range"]),
        A_range=tuple(init["A_range"]),
        R_range=tuple(init["R_range"]),
        V_range=tuple(init["V_range"]),
    )

    lambda_coupling = float(params["lambda_coupling"])
    initial_tension = compute_total_tension(
        system,
        graph,
        lambda_coupling=lambda_coupling,
    )

    history: list[dict[str, Any]] = [
        {
            "time": 0,
            "total_tension": float(initial_tension["total"]),
            "external_tension": float(initial_tension["external"]),
            "internal_tension": float(initial_tension["internal"]),
            "delta_total_tension": 0.0,
            "num_nodes": int(len(system.nodes)),
            "h1_ok": True,
        }
    ]

    h1_violations = 0

    for _ in range(int(dyn["max_iterations"])):
        system, tension_before, tension_after, h1_ok = step_system(
            system=system,
            graph=graph,
            params=params,
            dynamics=dyn,
            validation=val,
        )

        if not h1_ok:
            h1_violations += 1

        history.append(
            {
                "time": int(system.time),
                "total_tension": float(tension_after["total"]),
                "external_tension": float(tension_after["external"]),
                "internal_tension": float(tension_after["internal"]),
                "delta_total_tension": float(
                    tension_after["total"] - tension_before["total"]
                ),
                "num_nodes": int(len(system.nodes)),
                "h1_ok": bool(h1_ok),
            }
        )

    history_df = pd.DataFrame(history)
    history_df.to_csv(run_dir / "history.csv", index=False)

    metrics = {
        "experiment": exp["name"],
        "description": exp["description"],
        "version": exp.get("version", "0.1.0"),
        "seed": seed,
        "initial_nodes": int(net["initial_nodes"]),
        "final_time": int(system.time),
        "final_nodes": int(len(system.nodes)),
        "initial_total_tension": float(history_df.iloc[0]["total_tension"]),
        "final_total_tension": float(history_df.iloc[-1]["total_tension"]),
        "min_total_tension": float(history_df["total_tension"].min()),
        "max_total_tension": float(history_df["total_tension"].max()),
        "total_tension_change": float(
            history_df.iloc[-1]["total_tension"] - history_df.iloc[0]["total_tension"]
        ),
        "h1_violations": int(h1_violations),
        "h1_pass_rate": float(1.0 - h1_violations / max(1, len(history_df) - 1)),
        "results_dir": str(run_dir.relative_to(ROOT)),
    }

    with open(run_dir / "metrics_summary.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    with open(run_dir / "config_used.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False, allow_unicode=True)

    save_graph_edges(graph, run_dir / "graph_edges.csv")

    final_state_df = pd.DataFrame(
        [node.to_vector() for node in system.nodes],
        columns=["E", "I", "A", "R", "V"],
    )
    final_state_df.insert(0, "node_id", [int(node.node_id) for node in system.nodes])
    final_state_df.insert(1, "node_type", [node.node_type for node in system.nodes])
    final_state_df.to_csv(run_dir / "final_state.csv", index=False)

    if bool(out.get("generate_figures", False)):
        save_tension_figure(history_df, run_dir / "fig_total_tension.png")

    run_log = [
        f"experiment={exp['name']}",
        f"description={exp['description']}",
        f"seed={seed}",
        f"iterations={dyn['max_iterations']}",
        f"initial_nodes={net['initial_nodes']}",
        f"final_nodes={len(system.nodes)}",
        f"initial_total_tension={metrics['initial_total_tension']:.6f}",
        f"final_total_tension={metrics['final_total_tension']:.6f}",
        f"total_tension_change={metrics['total_tension_change']:.6f}",
        f"h1_violations={h1_violations}",
        f"h1_pass_rate={metrics['h1_pass_rate']:.3f}",
        f"results_dir={metrics['results_dir']}",
    ]
    (run_dir / "run.log").write_text("\n".join(run_log), encoding="utf-8")

    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
