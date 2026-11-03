# Makefile for flop_simulator
#
# `make test`  — create a local virtualenv, install dev dependencies into it,
#                and run the pytest suite with coverage.
# `make clean` — remove the virtualenv, caches, and other build artifacts.

VENV    := .venv
PYTHON  := python3
BIN     := $(VENV)/bin
PIP     := $(BIN)/pip
PYTEST  := $(BIN)/pytest

# Sentinel file marking that dependencies are installed into the venv.
STAMP   := $(VENV)/.deps-installed

.PHONY: test clean

# Create the virtualenv and install dependencies. The stamp depends on the
# requirements file, so edits to it trigger a reinstall.
$(STAMP): requirements-dev.txt
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt
	touch $(STAMP)

test: $(STAMP)
	$(PYTEST)

clean:
	rm -rf $(VENV)
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -f .coverage .coverage.*
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -type f -name '*.py[cod]' -delete
