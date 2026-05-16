.PHONY: help install lint lint-fix format check check-example render serve \
        sync-skills sync-example clean

# Resume example exists twice on purpose: the repo copy (used by `make
# render`) and the packaged copy shipped in the wheel for `cv-claw
# init`. The wheel can't reach files outside src/cvclaw/, so the copy
# is unavoidable — check-example keeps them byte-identical.
REPO_EXAMPLE     := resumes/example.json
PACKAGE_EXAMPLE  := src/cvclaw/examples/example.json

UV ?= uv

help:
	@echo "Targets:"
	@echo "  install   Sync deps (incl. dev) via uv"
	@echo "  lint      Run ruff check"
	@echo "  lint-fix  Run ruff check with --fix"
	@echo "  format    Run ruff format"
	@echo "  check     Lint + format check + example parity (no writes)"
	@echo "  check-example  Fail if the repo and packaged example differ"
	@echo "  render    Render resumes/example.json to HTML"
	@echo "  serve     Run the dev server (requires [serve] extra)"
	@echo "  sync-skills  Copy skills/ → .claude/skills/ (no deletions)"
	@echo "  sync-example Copy repo example → packaged example"
	@echo "  clean     Remove caches and build artifacts"

install:
	$(UV) sync --all-extras

lint:
	$(UV) run ruff check .

lint-fix:
	$(UV) run ruff check --fix .

format:
	$(UV) run ruff format .

check: check-example
	$(UV) run ruff check .
	$(UV) run ruff format --check .

check-example:
	@cmp -s $(REPO_EXAMPLE) $(PACKAGE_EXAMPLE) || { \
	  echo "ERROR: $(REPO_EXAMPLE) and $(PACKAGE_EXAMPLE) differ."; \
	  echo "Run 'make sync-example' to update the packaged copy."; \
	  exit 1; \
	}

sync-example:
	cp $(REPO_EXAMPLE) $(PACKAGE_EXAMPLE)

render:
	$(UV) run cv-claw render resumes/example.json

serve:
	$(UV) run cv-claw serve

sync-skills:
	rsync -a skills/ .claude/skills/

clean:
	rm -rf .ruff_cache .pytest_cache build dist *.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
