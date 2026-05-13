# cv-claw

Render a resume JSON file into a print-ready, self-contained HTML
document via Jinja2 templates. The primary user is Claude (or any
shell-capable agent): produce JSON, then run one command to hand the
user a real artifact — no browser, no dev server required.

A small live-preview dev server is available behind an optional extra.

## Install

This project uses [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

To include the optional dev server and PDF backends:

```bash
uv sync --all-extras
```

## Quickstart

```bash
uv run cv-claw render resumes/example.json
# → writes resumes/example.html next to the JSON
```

The dev repo keeps its example JSON under `resumes/`, but in your own
workspace the JSON can live anywhere — cv-claw just renders whichever
path you give it. To keep generated HTML out of the way:

```bash
uv run cv-claw render path/to/resume.json --output-dir build/
# → writes build/resume.html
```

Open the HTML in a browser and use the browser's print dialog to export
to PDF.

## CLI

### render

```
cv-claw render <input.json> [flags]
```

Validate the JSON, look up the template, and write a standalone HTML
file. By default the output lands next to the input with an `.html`
suffix.

| Flag                    | Default          | Description                                                                                  |
|-------------------------|------------------|----------------------------------------------------------------------------------------------|
| `-o, --output <path>`   | `<input>.html`   | Single explicit output file. Wins over `--output-dir`.                                       |
| `--output-dir <dir>`    | —                | Output directory; filename is `<input-stem>.html`. Directory is created if missing.          |
| `--template <name>`     | from JSON        | Override the `template` field in the resume JSON for this render only.                       |
| `--templates-dir <dir>` | auto-discover    | Replace the default search roots (workspace + bundled) with a single directory.              |

### list-templates

```
cv-claw list-templates [flags]
```

Print discovered template names, one per line. Default output annotates
each entry with its source: `(workspace)` for templates under
`./.cvclaw/templates/`, `(bundled)` for those shipped inside cv-claw.

| Flag                    | Default       | Description                                                                                |
|-------------------------|---------------|--------------------------------------------------------------------------------------------|
| `--templates-dir <dir>` | auto-discover | Replace the default search roots with a single directory; drops the source annotation.     |

### validate

```
cv-claw validate <input.json>
```

Run schema validation only. Exits 0 on success, non-zero on failure.
Useful as a sanity check before rendering.

### serve

```
cv-claw serve [flags]
```

Run a small live-reload dev server. Requires the optional `[serve]`
extra (`uv sync --all-extras` or `pip install 'cv-claw[serve]'`).

| Flag                    | Default       | Description                                                  |
|-------------------------|---------------|--------------------------------------------------------------|
| `--host <addr>`         | `127.0.0.1`   | Host to bind to.                                             |
| `-p, --port <int>`      | `8000`        | Port to listen on.                                           |
| `--resumes-dir <dir>`   | CWD           | Directory of resume JSON files to serve.                     |
| `--templates-dir <dir>` | auto-discover | Replace the default template search roots with a single dir. |

### Global

| Flag        | Description           |
|-------------|-----------------------|
| `--version` | Show version and exit. |

## Schema

A resume is a JSON document with a `template`, a `header`, and a list of
`sections`. Each section is one of four kinds — `prose`, `keyvalue`,
`list`, or `timeline` — and is dispatched to the matching renderer in
the template.

## Using the skill in your own workspace

The [`skills/cv-claw/`](skills/cv-claw/) directory ships a single
[Agent Skill](https://agentskills.io) covering three resume tasks —
ingest (PDF/image/text → JSON), tailor (adapt for a job description),
and create-template (new Jinja2 layout). The main `SKILL.md` stays
small; each task lives under `references/` and is loaded on demand.

To use:

1. Install cv-claw in your workspace: `uv add cv-claw` (or
   `pip install cv-claw`).
2. Copy `skills/cv-claw/` into your workspace's skills directory.
3. Point your agent at it and start producing resume JSON.

## Templates

Templates live in two roots, both auto-discovered:

1. **Bundled** — ship inside the cv-claw package (e.g. `classic`).
   Read-only; they come down with `pip install cv-claw`.
2. **Workspace** — under `./.cvclaw/templates/<name>/` in your current
   working directory. Optional; created on first use by the skill.

A workspace template **shadows** a bundled template of the same name —
that's the supported way to fork. The `.cvclaw/` prefix is reserved for
cv-claw workspace state; today it holds `templates/`, and future
versions may add cache or config under the same prefix.

A typical workspace tree:

```text
my-resume-workspace/
├── resumes/                       # or wherever you keep your JSON
│   └── default.json
└── .cvclaw/
    └── templates/
        └── minimalist/
            ├── minimalist.html.j2 # entry point
            ├── minimalist.css     # inlined into the rendered HTML
            └── _macros.html.j2    # optional section renderers
```

Files and directories starting with `_` are treated as partials and are
skipped by template discovery. Add a new template by dropping in a new
folder with the same shape (the [`create-template` task](skills/cv-claw/references/create-template.md)
automates the scaffolding).

## Resume JSON conventions

cv-claw doesn't impose a directory for your resume JSON — pass any
path on the CLI and it just works. The bundled skill (used by Claude
Code and other agent surfaces) **asks the user once** where resume JSON
should live and can record the answer in your workspace `CLAUDE.md`
under a `## cv-claw: resume location` heading so future sessions don't
re-ask.

## Development

```bash
make install     # uv sync --all-extras
make lint        # ruff check
make format      # ruff format
make check       # ruff check + ruff format --check
make render      # render resumes/example.json
make clean       # remove caches and build artifacts
```

## License

MIT — see [`LICENSE`](LICENSE).
