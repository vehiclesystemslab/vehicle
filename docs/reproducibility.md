# Reproducibility Policy

## Purpose
This document defines the scientific execution protocol for VEHICLE Systems Lab. The goal is to ensure that every experiment can be rerun, audited, and compared under an explicit parameter set and a transparent computational trail.

## Reproducibility principles

1. Every experiment must be driven by a versioned configuration file.
2. Every run must use an explicit random seed.
3. Every output must be written to a dedicated results directory.
4. Every figure must be generated from saved results, not from transient notebook state.
5. Every claim must be traceable to code, configuration, and recorded history.

## Canonical repository flow

1. Select an experiment configuration from `configs/experiments/`.
2. Run the corresponding executable in `experiments/`.
3. Save all run outputs in `results/<experiment_name>/run_<timestamp>_seed<seed>/`.
4. Generate figures from the saved CSV/JSON outputs.
5. Record interpretation and decisions in `docs/experiments/`.

## Minimum artifacts per run

Each reproducible run should generate:

- `config_used.yaml`
- `history.csv`
- `metrics_summary.json`
- `final_state.csv`
- `run.log`
- final figures in PNG format

## Required metadata

Each run should preserve, at minimum:

- experiment name
- run timestamp
- random seed
- code version or commit hash
- parameter values
- initial topology description
- output file list

## Parameter management

Parameters may not be hidden inside notebooks or ad hoc edits. They must remain in the configuration layer and should be copied into each run directory as executed.

Recommended configuration classes:

- network structure
- initial state ranges
- update parameters
- projection-governance parameters
- validation tolerances
- output settings

## Validation policy

The first validation layer should test the declared experimental hypothesis directly. For the current base experiment, the target is H1: monotone dissipation.

Validation should report:

- pass/fail status
- numerical tolerance used
- number of violations
- time index of violations
- summary statistics of the tension trajectory

## File naming

Use `snake_case` for files and folders. Experiment names should be mirrored across:

- config file name
- script file name
- results folder name
- experiment note
- figure file names

## Good practice

- Prefer deterministic data generation.
- Keep model code separate from experiment scripts.
- Keep plotting code separate from simulation code.
- Never overwrite prior runs.
- Document any parameter change that affects interpretation.

## Reproducibility statement

VEHICLE Systems Lab treats each experiment as a versioned scientific object, not as a disposable notebook output. If the configuration, code, or seed changes, the resulting run is scientifically distinct and must be stored separately.
