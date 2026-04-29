PYTHON ?= python
PIP ?= $(PYTHON) -m pip

.PHONY: install dev test validate exp01 plot-exp01 run-exp01 install-run clean clean-results clean-cache

install:
	$(PIP) install -e .

dev:
	$(PIP) install -e ".[dev]"

test:
	$(PYTHON) -m pytest

validate:
	$(PYTHON) scripts/validate_exp01.py

exp01:
	$(PYTHON) experiments/exp01_base_dissipation.py

plot-exp01:
	$(PYTHON) scripts/plot_exp01_base_dissipation.py

run-exp01:
	$(PYTHON) scripts/run_exp01_base_dissipation.py

install-run:
	$(PYTHON) scripts/install_and_run_exp01.py

clean-results:
	find results -mindepth 1 ! -name .gitkeep -exec rm -rf {} +
	find figures -mindepth 1 ! -name .gitkeep -exec rm -rf {} +
	mkdir -p results/exp01_base_dissipation figures/exp01_base_dissipation
	touch results/.gitkeep results/exp01_base_dissipation/.gitkeep figures/.gitkeep figures/exp01_base_dissipation/.gitkeep

clean-cache:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache build dist *.egg-info

clean: clean-cache
