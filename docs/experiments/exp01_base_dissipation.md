# Experiment 01 — Base Dissipation

## Purpose

Evaluate the baseline tension trajectory of the VEHICLE 3D E.I.A.R.(V) computational layer under a projection-governed relaxed update.

## Hypothesis target

H1 — Monotone dissipation:

```text
T(X(t+1)) <= T(X(t)) + epsilon
```

## Configuration

Canonical configuration file:

```text
configs/experiments/exp01_base_dissipation.yaml
```

## Execution

From the repository root:

```bash
python experiments/exp01_base_dissipation.py
```

## Expected outputs

Each run should write outputs into a dedicated results directory:

- `config_used.yaml`
- `graph_edges.csv`
- `history.csv`
- `final_state.csv`
- `metrics_summary.json`
- `run.log`
- `fig_total_tension.png`, when figure generation is enabled

## Interpretation note

This experiment is an empirical diagnostic under a configured update rule. It should not be presented as a universal proof of convergence. Its role is to establish a reproducible baseline for later comparisons across regimes, perturbations, recovery behavior, and attractor diagnostics.
