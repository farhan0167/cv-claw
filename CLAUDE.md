# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project purpose

`cv-claw` is a Python CLI that turns a resume JSON file into a
print-ready, **standalone HTML artifact** via Jinja2 templates. The
primary user is an LLM (Claude, in any surface that can run shell
commands): the skill produces JSON, then a single `cv-claw render` call
hands the user a finished artifact — no browser, no dev server, no
frontend toolchain required.

## Common commands

The project uses [uv](https://docs.astral.sh/uv/). All commands assume
the repo root as the working directory.

```bash
# install / sync (incl. dev deps)
uv sync                          # core only
uv sync --all-extras             # include [serve] and [pdf] extras

# the CLI (after `uv sync`)
uv run cv-claw render resumes/example.json
uv run cv-claw list-templates
uv run cv-claw validate resumes/example.json
uv run cv-claw serve             # needs [serve] extra (not yet implemented)

# lint / format via the Makefile (ruff is the only quality tool)
make lint            # ruff check .
make lint-fix        # ruff check --fix .
make format          # ruff format .
make check           # lint + format --check, no writes (CI-style)
```

Other Makefile targets: `make install | render | serve | clean`.

## Dev workflow — MANDATORY after every code change

**You MUST run these three commands, in order, after making ANY change
to a `.py` file. No exceptions.** This applies after every edit,
not just before commits or handoffs:

```bash
make lint-fix        # auto-fix what ruff can
make format          # apply formatting
make lint            # confirm nothing remains
```

If `make lint` still reports issues, fix them by hand and re-run the
sequence until `make lint` is clean. Do not report a task as complete,
hand work back, or commit while `make lint` is failing.

This rule exists because there is no test suite — ruff is the only
automated quality gate, so it must always be green.

There is **no test suite**. Verification is by rendering
`resumes/example.json` and inspecting the output.

## Skills live in two places — MANDATORY sync rule

The shared skills exist in two locations in this repo:

- [`skills/`](skills/) — the **source of truth** and **public** copy.
  This is what gets distributed to end users (the published artifact,
  the OSS repo download). Always edit here.
- [`.claude/skills/`](.claude/skills/) — the **local** copy that Claude
  Code reads when working *inside this repo*. Without this copy, Claude
  Code has no access to the skills while developing cv-claw itself.
  This directory may also contain other repo-local-only skills that
  exist *only* under `.claude/skills/` — do not delete those.

**Why two copies and not a symlink:** symlinks break on Windows clones
of OSS repos without Developer Mode, which would silently leave
contributors with no working skills. A real copy is portable everywhere.

**The rule:** edit only under `skills/`. After any change there, run:

```bash
make sync-skills    # rsync -a skills/ .claude/skills/  (no --delete)
```

This copies new/changed files from `skills/` into `.claude/skills/`
without touching anything else — repo-local-only skills are preserved.
Include the resulting `.claude/skills/` changes in the same commit as
the `skills/` change.

Caveat: file *deletions* under `skills/` won't propagate automatically.
If you remove a file from a shared skill, also delete it manually under
`.claude/skills/<same-path>` and include both in the commit.

## Architecture

The render pipeline is the spine of the codebase — five short modules
under [src/cvclaw/](src/cvclaw/), each with one job:

1. **`schema.py`** — pydantic v2 models for the resume schema. Sections
   are a discriminated union over `kind` (`prose | keyvalue | list |
   timeline`); all models use `extra="forbid"` so JSON typos surface as
   real errors instead of silently rendering nothing.

2. **`templates_loader.py`** — auto-discovers templates by globbing
   `templates/*/` for a matching `<name>.html.j2`. Names beginning with
   `_` are skipped (reserved for shared partials). Also builds the Jinja
   `Environment` rooted at the **whole** templates directory (not at one
   template's folder), so a template can `{% import "classic/_macros..."
   %}` cross-folder, and shared partials in `_partials/` are reachable
   the same way. Autoescape is on; `StrictUndefined` is used so typos
   like `resume.headers.name` raise instead of rendering empty.

3. **`render.py`** — the integration point. `render_resume(...)` loads
   the validated `Resume` into Jinja context, renders the template body,
   reads the matching `<name>.css`, and wraps everything in a complete
   HTML document with the CSS inlined into a `<style>` block. Templates
   own the body markup only; `render.py._wrap_document` adds the
   `<!doctype>` / `<head>` / `<style>` shell. The Resume is passed as a
   pydantic model (not `.model_dump()`), so templates access fields via
   attribute syntax (`resume.header.name`, `section.data.items`).

4. **`cli.py`** — Typer CLI. `render` calls `render_file`; `validate`
   only runs `load_resume`; `list-templates` calls `discover_templates`.
   `serve` is a stub that imports `cvclaw.serve` lazily and tells the
   user to install the `[serve]` extra — the serve module is not yet
   implemented.

5. **`__init__.py`** — re-exports `Resume` and `render_resume` as the
   public API.

### Template contract

Templates live at `templates/<name>/`:

- `<name>.html.j2` — entry point. Renders the body markup only.
- `<name>.css` — auto-inlined into a `<style>` block at render time.
  **Every CSS rule must start with `.<name>`** to avoid leakage when
  templates are combined; this is enforced by convention, not code.
- `_macros.html.j2` (optional) — section renderers as Jinja macros.
  Imported via `{% import "<name>/_macros.html.j2" as m %}`.

`templates/classic/` is the reference template. The starter scaffolding
copied by the `create-template` skill lives at
[skills/create-template/assets/starter/](skills/create-template/assets/starter/).

### Section kinds — the load-bearing abstraction

Every section dispatches on its `kind` field. The kinds taxonomy is
fixed at four (`prose`, `keyvalue`, `list`, `timeline`) and **adding new
kinds is a schema change** that ripples through every template. Don't
add kinds; map novel layouts onto existing kinds with custom CSS, or
branch sparingly on `section.name`.

The `timeline` kind has two render modes: **compact** (no item has
bullets — typical for Education) vs **full** (any item has bullets). The
template auto-detects via `selectattr("bullets") | list | length > 0`.

### Skills

One [Agent Skill](https://agentskills.io) lives at
[skills/cv-claw/](skills/cv-claw/). The main `SKILL.md` is intentionally
thin — a description and a routing table. The three resume tasks
(ingest, tailor, create-template) each live as a single reference file
under `references/`, loaded on demand via progressive disclosure. The
schema lives in **one place**: `references/schema.md`. The
`assets/starter/` directory holds the Jinja boilerplate the
create-template task copies into a new `templates/<name>/` folder.

The authoritative schema implementation is the pydantic models in
[src/cvclaw/schema.py](src/cvclaw/schema.py); if those change, update
`skills/cv-claw/references/schema.md` (single source — no fan-out).

## Conventions worth knowing

- **Python ≥ 3.10** is supported (`requires-python = ">=3.10"`); the dev
  environment uses 3.12 via `.python-version`. Ruff `target-version =
  "py310"` keeps linting honest about the lower bound.
- **Imports are absolute from the `cvclaw` package** (`from cvclaw.foo
  import bar`), not relative. The `src/` layout means the package is
  only importable after `uv sync` installs it.
- **No backward-compat shims, no dead-code paths.** This is pre-1.0 OSS;
  break things and update callers rather than carrying compat code.
- **The serve module is deliberately absent.** Importing it raises
  `ImportError`, which `cli.py serve` catches and converts into a
  helpful install message. When implementing serve, add
  `src/cvclaw/serve.py` and make sure the optional `[serve]` deps
  (`fastapi`, `uvicorn`, `watchdog`, `websockets`) are the only ones it
  imports.
- **`.claude/specifications/`** is gitignored; the SPEC for the rewrite
  lives there locally but is not part of the public repo.
