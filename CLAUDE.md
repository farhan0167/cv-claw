# CLAUDE.md

Guidance for Claude Code working in this repo. Keep this file short —
load-bearing rules only. Everything else lives in code, skills, or
`README.md`.

## Project shape

`cv-claw` is a Python CLI that renders resume JSON into a standalone
HTML artifact via Jinja2 templates. The primary user is an LLM that
runs shell commands: produce JSON, run `cv-claw render`, hand the user
a finished file. No browser, no dev server, no frontend toolchain.

Source layout: `src/cvclaw/{schema,templates_loader,render,cli}.py`
plus `src/cvclaw/templates/` (bundled templates shipped in the wheel).
Read the modules directly when you need details — they have
docstrings.

## Dev workflow — MANDATORY after every code change

**You MUST run these three commands, in order, after ANY edit to a
`.py` file:**

```bash
make lint-fix
make format
make lint
```

If `make lint` still reports issues, fix them by hand and re-run until
clean. **Do not commit, hand work back, or report a task complete
while `make lint` is failing.** This repo has no test suite — ruff is
the only automated quality gate.

Manual verification: `uv run cv-claw render resumes/example.json` and
inspect the output.

## Skills live in two places — MANDATORY sync rule

- [`skills/`](skills/) — source of truth. Public; ships to end users.
  Always edit here.
- [`.claude/skills/`](.claude/skills/) — local mirror Claude Code
  reads while developing this repo. May also contain repo-local-only
  skills (e.g. [`pr-message`](.claude/skills/pr-message/)) that have
  no `skills/` counterpart — don't delete those.

After editing under `skills/`, run `make sync-skills` (rsync without
`--delete`) and include the `.claude/skills/` changes in the same
commit. **File deletions don't propagate** — remove them by hand from
both mirrors.

## Commit conventions

- [Conventional Commits](https://www.conventionalcommits.org/):
  `<type>(<scope>): <subject>`, imperative lowercase, ≤72 chars, no
  period. Draw scopes from `git log -20` rather than inventing new
  ones.
- Include a body when the subject can't carry the *why* on its own.
  Wrap ~72; lead with motivation.
- Last line of the body:
  `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`
- **No** `🤖 Generated with Claude Code` lines on commits (those are
  for PR bodies). **No** `--amend` or `--no-verify` without an
  explicit user request.

## Schema is load-bearing

Section `kind` is a fixed taxonomy: **`prose`, `keyvalue`, `list`,
`timeline`**. **Adding a kind is a schema change that ripples through
every template.** Don't add kinds; map novel layouts onto the existing
four with custom CSS or sparse `section.name` branches.

The authoritative schema is [src/cvclaw/schema.py](src/cvclaw/schema.py).
The skill's [schema reference](skills/cv-claw/references/schema.md) is
the single human-readable mirror; update it when the pydantic models
change. No other fan-out.

## Templates

- Two roots: workspace `./.cvclaw/templates/` (user-authored) and the
  bundled `src/cvclaw/templates/` (ships in the wheel). Workspace
  shadows bundled per directory.
- Per-template CSS rules **must start with `.<name>`** to prevent
  cross-template leakage when CSS is inlined.
- Directory names beginning with `_` are reserved for shared partials
  and skipped by discovery.

## Conventions worth knowing

- **Python ≥ 3.10** (`requires-python = ">=3.10"`); dev env is 3.12.
  Ruff `target-version = "py310"` enforces the lower bound.
- **Absolute imports** from the `cvclaw` package, never relative.
- **No backward-compat shims.** Pre-1.0 OSS — break and update callers.
- **`serve` is deliberately a stub.** `src/cvclaw/serve.py` doesn't
  exist; the CLI catches the `ImportError` and prints an install hint.
  When implementing, only import from the optional `[serve]` extra.
- **`.claude/specifications/` is gitignored.** Specs live there
  locally; they're not part of the public repo.
