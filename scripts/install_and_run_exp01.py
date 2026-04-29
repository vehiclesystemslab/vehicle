"""
scripts/install_and_run_exp01.py

Utility script to install dependencies and run the first VEHICLE experiment end-to-end.
Installs runtime dependencies and runs the first experiment workflow.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd, cwd=ROOT):
    print(f"$ {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, cwd=str(cwd), check=True)


def main():
    run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    run([sys.executable, "experiments/exp01_base_dissipation.py"])
    run([sys.executable, "scripts/plot_exp01_base_dissipation.py"])
    print("End-to-end execution complete.", flush=True)


if __name__ == "__main__":
    main()
