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
# → writes resumes/example.html
```

Open the HTML in a browser and use the browser's print dialog to export
to PDF.

## CLI

```text
cv-claw render <input.json> [-o <output.html>] [--template <name>]
cv-claw list-templates
cv-claw validate <input.json>
cv-claw serve [--port 8000]                # requires the [serve] extra
```

- `render` validates the JSON, looks up the template, and writes a
  standalone HTML file. By default the output lands next to the input
  with an `.html` suffix.
- `list-templates` prints the names of all discovered templates.
- `validate` runs schema validation only; useful as a sanity check
  before rendering.
- `serve` runs a tiny live-reload dev server (optional).

## Schema

A resume is a JSON document with a `template`, a `header`, and a list of
`sections`. Each section is one of four kinds — `prose`, `keyvalue`,
`list`, or `timeline` — and is dispatched to the matching renderer in
the template.

See [`SCHEMA.md`](SCHEMA.md) for the full schema and
[`resumes/example.json`](resumes/example.json) for a worked example.

## Templates

Templates live under `templates/<name>/`:

```text
templates/
└── classic/
    ├── classic.html.j2     # entry point
    ├── classic.css         # inlined into the rendered HTML
    └── _macros.html.j2     # section renderers
```

Files and directories starting with `_` are treated as partials and are
skipped by template discovery. Add a new template by dropping in a new
folder with the same shape.

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
