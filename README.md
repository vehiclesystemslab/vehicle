# VEHICLE Systems Lab

**VEHICLE Systems Lab** is the scientific and computational environment for the VEHICLE framework: a structured approach to describing, measuring, auditing, and simulating structural tension in hybrid systems.

The project is built on a strong convergence thesis: under explicit compatibility rules, projection-governed updates, and bounded relational tension, complex hybrid systems can exhibit measurable movement toward structural coherence. This repository does not present that thesis as a closed universal proof; it turns it into reproducible code, observable trajectories, and testable experimental evidence.

## Current base

The current computational base is the E.I.A.R.(V) formulation. Each node is represented as a principal state vector:

```text
S_i = (E, I, A, R, V)
```

where the model tracks structural orientation, information density, active coupling, relational compatibility, and verification-projection. The repository introduces a projection-governed operator `V_op` for controlled evolution under tension.

## What this repository contains

- `vehicle/`: reusable scientific core.
- `experiments/`: executable validation scripts.
- `configs/`: experiment definitions and reproducibility parameters.
- `results/`: saved outputs per run.
- `figures/`: PNG figures generated from persisted results.
- `docs/`: architecture, reproducibility, and experiment notes.
- `scripts/`: orchestration and plotting utilities.
- `manuscripts/`: paper and publication materials.

## Scientific base

The repository follows the updated conceptual floor of VEHICLE:

- **Object of study:** structural tension in hybrid organizational systems.
- **Minimal architecture:** node, relation, load, compatibility, local tension, global tension, propagation, containment, recovery, fragility, stability, and trajectory.
- **Formal layer:** computable and auditable notation, open to refinement.
- **Validation layer:** H1-H5 observables and A0-A6 attractor taxonomy.
- **Central thesis:** convergence is not assumed rhetorically; it is tested through explicit dynamics, tension histories, diagnostics, and reproducible runs.

## Core modules

- `vehicle/state.py`: principal node state and global system state.
- `vehicle/tension.py`: external, internal, and total tension functions.
- `vehicle/governance.py`: projection-governance operator `V_op`.
- `vehicle/eiarv.py`: discrete governed dynamics.
- `vehicle/observables.py`: diagnostic checks for H1-H5.
- `vehicle/attractors.py`: A0-A6 attractor classification.

## Reproducibility policy

Each run must be driven by a versioned configuration file, a fixed random seed, and a dedicated results directory. Saved artifacts should include `config_used.yaml`, `history.csv`, `metrics_summary.json`, `final_state.csv`, `run.log`, and generated figures.

Figures must always be regenerated from saved results, never from transient notebook state.

## Base experiments

- `exp01_base_dissipation`
- `exp02_rigid_vs_fluid`
- `exp03_impulse_recovery`
- `exp04_natural_mitosis`
- `exp05_regime_comparison`

The first end-to-end workflow is:

1. run `experiments/exp01_base_dissipation.py`
2. save results in `results/exp01_base_dissipation/`
3. generate figures with `scripts/plot_exp01_base_dissipation.py`
4. inspect the PNG outputs in `figures/exp01_base_dissipation/`

## Installation

```bash
python -m pip install -e .
```

## Execution

Run the first experiment end-to-end with:

```bash
python scripts/run_exp01_base_dissipation.py
```

Run a local install-and-run workflow with:

```bash
python scripts/install_and_run_exp01.py
```

Run tests with:

```bash
pytest
```


## Makefile workflow

The repository includes a small `Makefile` for repeatable local execution:

```bash
make dev          # install package with development dependencies
make test         # run the test suite
make validate     # run the short exp01 validator
make run-exp01    # run exp01 and generate figures
make clean-cache  # remove Python caches
```

The validator is intentionally lightweight. It is a smoke check that verifies the computational core, a short E.I.A.R.(V) update sequence, finite tension values, and A0-A6 attractor summarization.

## Status

This repository is under active construction. Its purpose is not to dilute the ambition of VEHICLE, but to discipline it: to move from conceptual definitions toward reproducible computational evidence for structural tension, governed dynamics, and convergence-oriented behavior.

## License and attribution

Source code in this repository is licensed under the Apache License 2.0.

Documentation, diagrams, research notes, manuscripts, and methodological descriptions are licensed under Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International unless otherwise stated. See `docs/LICENSE-DOCS.md`.

VEHICLE Systems Lab, VEHICLE, VEHICLE-T, AIMTG, and related institutional identifiers are research identifiers of Roberto Borda Milan. Use of these names for endorsement, certification, institutional representation, or commercial services requires explicit written permission.

## Citation

Citation metadata is provided in `CITATION.cff`. If you use this project in research, please cite the VEHICLE Systems Lab repository and the associated E.I.A.R.(V) paper.
