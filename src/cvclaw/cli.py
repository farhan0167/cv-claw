"""Command-line interface for cv-claw."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from pydantic import ValidationError

from cvclaw import __version__
from cvclaw.render import load_resume, render_file
from cvclaw.templates_loader import (
    TemplateNotFoundError,
    TemplateSource,
    discover_templates,
)

app = typer.Typer(
    name="cv-claw",
    add_completion=False,
    no_args_is_help=True,
    help="Render resume JSON to print-ready HTML using Jinja templates.",
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"cv-claw {__version__}")
        raise typer.Exit()


@app.callback()
def _main(
    version: Optional[bool] = typer.Option(  # noqa: UP007 (typer needs Optional)
        None,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """cv-claw — turn resume JSON into a print-ready HTML artifact."""


@app.command()
def render(
    input: Path = typer.Argument(  # noqa: A002 (intentional CLI verb)
        ...,
        exists=True,
        dir_okay=False,
        readable=True,
        help="Path to resume JSON.",
    ),
    output: Optional[Path] = typer.Option(  # noqa: UP007
        None,
        "-o",
        "--output",
        help="Output HTML path. Defaults to <input>.html next to the input.",
    ),
    template: Optional[str] = typer.Option(  # noqa: UP007
        None,
        "--template",
        help="Override the template name from the JSON.",
    ),
    templates_dir: Optional[Path] = typer.Option(  # noqa: UP007
        None,
        "--templates-dir",
        help="Override the templates directory (replaces default search roots).",
    ),
    output_dir: Optional[Path] = typer.Option(  # noqa: UP007
        None,
        "--output-dir",
        help=(
            "Directory for rendered HTML. Filename derives from input stem. "
            "Ignored if -o/--output is set."
        ),
    ),
) -> None:
    """Render INPUT JSON to a standalone HTML file."""

    if output is None and output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        output = output_dir / f"{input.stem}.html"

    try:
        target = render_file(
            input,
            output_path=output,
            templates_dir=templates_dir,
            template_override=template,
        )
    except ValidationError as exc:
        typer.secho(f"Invalid resume JSON: {input}", fg=typer.colors.RED, err=True)
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc
    except TemplateNotFoundError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2) from exc

    typer.echo(str(target))


@app.command("list-templates")
def list_templates(
    templates_dir: Optional[Path] = typer.Option(  # noqa: UP007
        None,
        "--templates-dir",
        help="Override the templates directory.",
    ),
) -> None:
    """List discovered template names."""

    templates = discover_templates(templates_dir)
    if not templates:
        typer.secho("No templates found.", fg=typer.colors.YELLOW, err=True)
        raise typer.Exit(code=1)

    # When --templates-dir is used, there's only one root — no annotation
    # adds signal. Otherwise label each entry by where it was discovered.
    annotate = templates_dir is None
    for name, tpl in templates.items():
        if annotate and tpl.source is not TemplateSource.OVERRIDE:
            typer.echo(f"{name} ({tpl.source.value})")
        else:
            typer.echo(name)


@app.command()
def validate(
    input: Path = typer.Argument(  # noqa: A002
        ...,
        exists=True,
        dir_okay=False,
        readable=True,
        help="Path to resume JSON.",
    ),
) -> None:
    """Validate a resume JSON file against the schema."""

    try:
        load_resume(input)
    except ValidationError as exc:
        typer.secho(f"Invalid: {input}", fg=typer.colors.RED, err=True)
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    typer.secho(f"OK: {input}", fg=typer.colors.GREEN)


@app.command()
def serve(
    port: int = typer.Option(8000, "--port", "-p", help="Port to listen on."),
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind to."),
    resumes_dir: Path = typer.Option(
        Path.cwd(),
        "--resumes-dir",
        help="Directory of resume JSON files to serve. Defaults to CWD.",
    ),
    templates_dir: Optional[Path] = typer.Option(  # noqa: UP007
        None,
        "--templates-dir",
        help="Override the templates directory.",
    ),
) -> None:
    """Run the dev server with live-reload (requires the [serve] extra)."""

    try:
        from cvclaw.serve import run  # noqa: PLC0415 (optional import)
    except ImportError as exc:
        typer.secho(
            "The 'serve' command requires the optional [serve] extra. "
            "Install with: pip install 'cv-claw[serve]'",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1) from exc

    run(
        host=host,
        port=port,
        resumes_dir=resumes_dir,
        templates_dir=templates_dir,
    )


if __name__ == "__main__":
    app()
