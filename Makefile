.PHONY: help install install-dev test lint format type-check clean run-phase04 run-phase59

help:  ## Show this help message
	@echo "MV Orchestra v3.0 - Make Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -e ".[dev]"

test:  ## Run tests with coverage
	pytest

test-verbose:  ## Run tests with verbose output
	pytest -v

test-cov:  ## Run tests and generate coverage report
	pytest --cov --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

lint:  ## Run flake8 linting
	flake8 core/ phase*/ *.py

format:  ## Format code with black and isort
	black core/ phase*/ *.py
	isort core/ phase*/ *.py

format-check:  ## Check code formatting without making changes
	black --check core/ phase*/ *.py
	isort --check core/ phase*/ *.py

type-check:  ## Run mypy type checking
	mypy core/ phase*/ *.py

quality:  ## Run all quality checks (lint, format-check, type-check)
	@echo "Running flake8..."
	@$(MAKE) lint
	@echo "\nChecking formatting..."
	@$(MAKE) format-check
	@echo "\nRunning type check..."
	@$(MAKE) type-check
	@echo "\n✓ All quality checks passed!"

clean:  ## Clean up generated files
	rm -rf __pycache__ .pytest_cache .mypy_cache htmlcov .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete

clean-sessions:  ## Clean up session data (WARNING: deletes all sessions)
	rm -rf sessions/

# Run commands
run-phase04:  ## Run Phase 0-4 (Design) - Usage: make run-phase04 SESSION=my_session AUDIO=song.mp3
	python3 run_orchestrator.py $(SESSION) --audio $(AUDIO)

run-phase59:  ## Run Phase 5-9 (Generation) - Usage: make run-phase59 SESSION=my_session
	python3 run_phase5_9.py $(SESSION) --mock

run-full:  ## Run full pipeline - Usage: make run-full SESSION=my_session AUDIO=song.mp3
	python3 run_orchestrator.py $(SESSION) --audio $(AUDIO)
	python3 run_phase5_9.py $(SESSION) --mock

# Utility commands
check-claude:  ## Check if Claude CLI is available
	@which claude || echo "ERROR: Claude CLI not found in PATH"
	@claude --version || echo "ERROR: Cannot execute Claude CLI"

setup:  ## Initial project setup
	@echo "Setting up MV Orchestra v3.0..."
	@$(MAKE) install-dev
	@$(MAKE) check-claude
	@echo "\n✓ Setup complete!"

validate:  ## Validate all configuration files
	@echo "Validating configuration..."
	@python3 -c "import json; json.load(open('config/orchestrator_config.json'))" && echo "✓ orchestrator_config.json valid"
	@python3 -c "import toml; toml.load(open('pyproject.toml'))" && echo "✓ pyproject.toml valid" || echo "Note: Install 'toml' to validate pyproject.toml"

verify-prompts:  ## Verify all prompt files exist
	@echo "Checking prompt files..."
	@python3 -c "from pathlib import Path; prompts = Path('.claude/prompts'); missing = []; \
	for phase in [1,2,3,4]: \
	    for d in ['corporate','freelancer','veteran','award_winner','newcomer','evaluation']: \
	        p = prompts / f'phase{phase}_{d}.md'; \
	        (print(f'✓ {p.name}') if p.exists() else (missing.append(str(p)) or print(f'✗ {p.name}'))); \
	print(f'\n{len(missing)} missing prompts' if missing else '\n✓ All prompts present')"
