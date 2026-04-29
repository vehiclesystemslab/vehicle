"""
scripts/plot_exp01_base_dissipation.py

Generate publication-ready diagnostic figures for exp01_base_dissipation
from the latest saved run directory.
"""

from __future__ import annotations

from pathlib import Path
import json
import shutil

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS_ROOT = ROOT / "results" / "exp01_base_dissipation"
FIGURES_DIR = ROOT / "figures" / "exp01_base_dissipation"


def latest_run_dir(results_root: Path = RESULTS_ROOT) -> Path:
    if not results_root.exists():
        raise FileNotFoundError(f"Results directory not found: {results_root}")
    run_dirs = sorted([p for p in results_root.iterdir() if p.is_dir() and p.name.startswith("run_")])
    if not run_dirs:
        raise FileNotFoundError(f"No run_* directories found in: {results_root}")
    return run_dirs[-1]


def plot_total_tension(history: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.plot(history["time"], history["total_tension"], marker="o", linewidth=1.6)
    ax.set_title("VEHICLE Experiment 01 — Total Tension")
    ax.set_xlabel("Discrete time step")
    ax.set_ylabel("Total tension T(X)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def plot_tension_components(history: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.plot(history["time"], history["external_tension"], marker="o", linewidth=1.4, label="External")
    ax.plot(history["time"], history["internal_tension"], marker="s", linewidth=1.4, label="Internal")
    ax.set_title("VEHICLE Experiment 01 — Tension Components")
    ax.set_xlabel("Discrete time step")
    ax.set_ylabel("Tension component value")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def main() -> None:
    run_dir = latest_run_dir()
    history_path = run_dir / "history.csv"
    metrics_path = run_dir / "metrics_summary.json"

    if not history_path.exists():
        raise FileNotFoundError(f"Missing history.csv in {run_dir}")

    history = pd.read_csv(history_path)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    fig_total = FIGURES_DIR / "fig_exp01_total_tension.png"
    fig_components = FIGURES_DIR / "fig_exp01_tension_components.png"

    plot_total_tension(history, fig_total)
    plot_tension_components(history, fig_components)

    if metrics_path.exists():
        shutil.copy2(metrics_path, FIGURES_DIR / "metrics_summary_latest.json")
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        print(json.dumps({"latest_run": str(run_dir.relative_to(ROOT)), "figures_dir": str(FIGURES_DIR.relative_to(ROOT)), **metrics}, indent=2))
    else:
        print(f"Figures saved to {FIGURES_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
