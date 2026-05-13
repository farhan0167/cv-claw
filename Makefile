.PHONY: help install lint lint-fix format check render serve sync-skills clean

UV ?= uv

help:
	@echo "Targets:"
	@echo "  install   Sync deps (incl. dev) via uv"
	@echo "  lint      Run ruff check"
	@echo "  lint-fix  Run ruff check with --fix"
	@echo "  format    Run ruff format"
	@echo "  check     Lint + format check (no writes)"
	@echo "  render    Render resumes/example.json to HTML"
	@echo "  serve     Run the dev server (requires [serve] extra)"
	@echo "  sync-skills  Copy skills/ → .claude/skills/ (no deletions)"
	@echo "  clean     Remove caches and build artifacts"

install:
	$(UV) sync --all-extras

lint:
	$(UV) run ruff check .

lint-fix:
	$(UV) run ruff check --fix .

format:
	$(UV) run ruff format .

check:
	$(UV) run ruff check .
	$(UV) run ruff format --check .

render:
	$(UV) run cv-claw render resumes/example.json

serve:
	$(UV) run cv-claw serve

sync-skills:
	rsync -a skills/ .claude/skills/

clean:
	rm -rf .ruff_cache .pytest_cache build dist *.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
