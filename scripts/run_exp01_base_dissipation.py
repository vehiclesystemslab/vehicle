"""
scripts/run_exp01_base_dissipation.py

End-to-end runner for exp01_base_dissipation:
1. run simulation
2. save results/history.csv and other artifacts
3. generate PNG figures
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SIM_SCRIPT = ROOT / "experiments" / "exp01_base_dissipation.py"
PLOT_SCRIPT = ROOT / "scripts" / "plot_exp01_base_dissipation.py"


def run(cmd):
    subprocess.run([sys.executable, str(cmd)], check=True, cwd=str(ROOT))


def main():
    run(SIM_SCRIPT)
    run(PLOT_SCRIPT)
    print("exp01_base_dissipation completed end-to-end")


if __name__ == "__main__":
    main()
