"""Core rendering: resume JSON + template -> standalone HTML string."""

from __future__ import annotations

import json
from pathlib import Path

from cvclaw.schema import Resume
from cvclaw.templates_loader import (
    build_environment,
    get_template,
)


def load_resume(path: Path) -> Resume:
    """Load and validate a resume JSON file."""

    data = json.loads(path.read_text(encoding="utf-8"))
    return Resume.model_validate(data)


def render_resume(
    resume: Resume,
    *,
    templates_dir: Path | None = None,
    template_override: str | None = None,
) -> str:
    """Render a :class:`Resume` to a complete HTML document.

    Parameters
    ----------
    resume:
        The validated resume model.
    templates_dir:
        Optional override that replaces the default search roots
        (``./.cvclaw/templates/`` + the bundled package templates) with a
        single root.
    template_override:
        Optional template name that overrides ``resume.template`` (useful for
        previewing the same resume across templates without editing JSON).
    """

    template_name = template_override or resume.template
    template = get_template(template_name, templates_dir)
    env = build_environment(templates_dir)

    # Templates live under <name>/<name>.html.j2, addressed relative to the
    # loader root (the templates directory).
    jinja_template = env.get_template(f"{template.name}/{template.name}.html.j2")

    css = template.css.read_text(encoding="utf-8") if template.css else ""
    body = jinja_template.render(resume=resume, template_name=template.name)

    return _wrap_document(title=resume.header.name, css=css, body=body)


def render_file(
    input_path: Path,
    output_path: Path | None = None,
    *,
    templates_dir: Path | None = None,
    template_override: str | None = None,
) -> Path:
    """Render a JSON file to HTML on disk and return the output path."""

    resume = load_resume(input_path)
    html = render_resume(
        resume,
        templates_dir=templates_dir,
        template_override=template_override,
    )
    target = output_path or input_path.with_suffix(".html")
    target.write_text(html, encoding="utf-8")
    return target


def _wrap_document(*, title: str, css: str, body: str) -> str:
    """Wrap a rendered template body in a complete HTML document."""

    # The template is responsible for the inner markup; this shell adds the
    # boilerplate (doctype, meta, inlined CSS) so the artifact is standalone.
    return (
        "<!doctype html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{_escape(title)}</title>\n"
        "<style>\n"
        f"{css}\n"
        "</style>\n"
        "</head>\n"
        "<body>\n"
        f"{body}\n"
        "</body>\n"
        "</html>\n"
    )


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
