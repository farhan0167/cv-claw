"""Template discovery and Jinja environment construction.

Templates live in a directory tree shaped like::

    <root>/
        <name>/
            <name>.html.j2
            <name>.css

A template "name" is the subdirectory name. The matching ``.html.j2`` file is
the entry point; the matching ``.css`` file (if present) is inlined into the
rendered output by :mod:`cvclaw.render`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape


def default_templates_dir() -> Path:
    """Return the bundled ``templates/`` directory shipped with the package."""

    # Resolve relative to repo root: src/cvclaw/templates_loader.py -> ../../templates
    return Path(__file__).resolve().parents[2] / "templates"


@dataclass(frozen=True)
class Template:
    """A discovered template on disk."""

    name: str
    root: Path

    @property
    def entry(self) -> Path:
        return self.root / f"{self.name}.html.j2"

    @property
    def css(self) -> Path | None:
        path = self.root / f"{self.name}.css"
        return path if path.exists() else None


class TemplateNotFoundError(LookupError):
    """Raised when a requested template name does not exist."""


def discover_templates(templates_dir: Path | None = None) -> dict[str, Template]:
    """Return a mapping of template name to :class:`Template`.

    Skips entries that begin with ``_`` (reserved for shared partials) and any
    directory missing a matching ``<name>.html.j2`` file.
    """

    root = templates_dir or default_templates_dir()
    if not root.is_dir():
        return {}

    templates: dict[str, Template] = {}
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith("_"):
            continue
        candidate = Template(name=child.name, root=child)
        if candidate.entry.exists():
            templates[child.name] = candidate
    return templates


def get_template(name: str, templates_dir: Path | None = None) -> Template:
    """Return the named template or raise :class:`TemplateNotFoundError`."""

    templates = discover_templates(templates_dir)
    if name not in templates:
        available = ", ".join(sorted(templates)) or "(none)"
        raise TemplateNotFoundError(
            f"Template {name!r} not found. Available: {available}"
        )
    return templates[name]


def build_environment(templates_dir: Path | None = None) -> Environment:
    """Build a Jinja2 environment rooted at the templates directory.

    The loader sees the entire templates tree so a template can reference
    partials in its own folder or in ``_partials/`` via standard Jinja
    ``{% include %}`` / ``{% import %}`` paths like
    ``"classic/_timeline.html.j2"`` or ``"_partials/_section.html.j2"``.
    """

    root = templates_dir or default_templates_dir()
    env = Environment(
        loader=FileSystemLoader(str(root)),
        autoescape=select_autoescape(("html", "j2", "html.j2")),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    return env
