# Repository Architecture

## Purpose
This document defines the conceptual and technical organization of the VEHICLE Systems Lab repository. The architecture is designed to preserve a clear separation between scientific concepts, computational core, experiment scripts, results, figures, and manuscript materials.

## Design goals

1. Keep the scientific model readable and auditable.
2. Separate reusable core logic from executable experiments.
3. Preserve reproducibility through explicit configurations.
4. Make outputs easy to compare across regimes and runs.
5. Support future expansion without breaking the current structure.

## Layered architecture

### 1. Scientific concepts
The conceptual base includes the object of study, the variable system, the formal language, the research questions, and the hypotheses. These materials live primarily in the manuscript and documentation layer.

### 2. Computational core
The `vehicle/` package contains the reusable implementation of the model. This layer should hold the state representation, tension functional, governance operator, dynamics, observables, attractors, and utility functions.

### 3. Experiment layer
The `experiments/` directory contains executable scripts for each validation case. Each experiment should use only the public API of the computational core and should not embed core scientific logic directly.

### 4. Configuration layer
The `configs/` directory stores experiment parameters, thresholds, and reproducibility settings. It is the formal source of truth for a run.

### 5. Data and results layer
The `data/` and `results/` directories store inputs, intermediate artifacts, and final outputs. Results must be run-specific and never mixed with source code.

### 6. Visualization layer
The `figures/` directory stores final figures used for analysis, manuscripts, or presentations. Figures should always be generated from saved results.

### 7. Documentation layer
The `docs/` directory stores architecture notes, reproducibility rules, glossary entries, and experiment reports.

### 8. Manuscript layer
The `manuscripts/` directory stores publication-oriented material. It should remain separate from executable code and from results.

## Core modules

### `vehicle/state.py`
Defines the principal nodal state `S_i = (E, I, A, R, V)` and the global system state.

### `vehicle/tension.py`
Implements the external, internal, and total tension functionals.

### `vehicle/governance.py`
Implements the projection-governance operator `V_op` and relaxed updates.

### `vehicle/eiarv.py`
Implements the discrete dynamics of the principal state under governed evolution.

### `vehicle/observables.py`
Implements diagnostic checks for hypotheses H1–H5.

### `vehicle/attractors.py`
Will map operational states to the A0–A6 taxonomy.

## Experiment structure

Each experiment should include:

- objective
- hypothesis target
- configuration file
- executable script
- output directory
- run summary
- figures derived from the run

## Current base experiments

- `exp01_base_dissipation`
- `exp02_rigid_vs_fluid`
- `exp03_impulse_recovery`
- `exp04_natural_mitosis`
- `exp05_regime_comparison`

## Dependency rule

The direction of dependency should be:

`manuscript -> docs -> configs -> experiments -> vehicle -> results -> figures`

Core code must not depend on ad hoc outputs, and documentation must not depend on temporary notebook state.

## Versioning rule

Changes to any scientific assumption must be reflected in at least one of the following:

- a configuration update
- a code update
- a documentation note
- a new experiment report

## Architectural statement

The repository is intentionally structured to support disciplined scientific work: every layer has a distinct role, and every experiment must leave a trace that allows later review, comparison, and refinement.
