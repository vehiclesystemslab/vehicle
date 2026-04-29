# GitHub Upload Guide

## First upload

From the repository root:

```bash
git init
git add .
git commit -m "Initial VEHICLE Systems Lab computational core"
git branch -M main
git remote add origin https://github.com/vehiclesystemslab/vehicle.git
git push -u origin main
```

If the remote repository already exists with files, pull first or create an empty repository before pushing.

## Local verification before pushing

```bash
python -m pip install -e ".[dev]"
pytest
python scripts/run_exp01_base_dissipation.py
```

For a dependency-install plus execution workflow:

```bash
python scripts/install_and_run_exp01.py
```

Generated outputs are intentionally ignored by Git under `results/`, `figures/`, and data folders, except for `.gitkeep` directory placeholders.


## Makefile shortcuts

```bash
make dev
make test
make validate
make run-exp01
```
