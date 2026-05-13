.PHONY: help install lint format check render serve clean

UV ?= uv

help:
	@echo "Targets:"
	@echo "  install   Sync deps (incl. dev) via uv"
	@echo "  lint      Run ruff check"
	@echo "  format    Run ruff format"
	@echo "  check     Lint + format check (no writes)"
	@echo "  render    Render resumes/example.json to HTML"
	@echo "  serve     Run the dev server (requires [serve] extra)"
	@echo "  clean     Remove caches and build artifacts"

install:
	$(UV) sync --all-extras

lint:
	$(UV) run ruff check .

format:
	$(UV) run ruff format .

check:
	$(UV) run ruff check .
	$(UV) run ruff format --check .

render:
	$(UV) run cv-claw render resumes/example.json

serve:
	$(UV) run cv-claw serve

clean:
	rm -rf .ruff_cache .pytest_cache build dist *.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
