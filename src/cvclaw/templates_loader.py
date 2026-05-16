"""Template discovery and Jinja environment construction.

Templates live in a directory tree shaped like::

    <root>/
        <name>/
            <name>.html.j2
            <name>.css

A template "name" is the subdirectory name. The matching ``.html.j2`` file is
the entry point; the matching ``.css`` file (if present) is inlined into the
rendered output by :mod:`cvclaw.render`.

Two roots are discovered by default:

1. **Workspace** — ``./.cvclaw/templates/`` relative to CWD, for user-authored
   templates. Optional; absent in a fresh workspace.
2. **Bundled** — ``<package>/templates/``, shipped inside the wheel.

The workspace root is searched first, so a workspace template shadows a
bundled template of the same name. Passing an explicit ``templates_dir``
collapses discovery to that single root.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape


class TemplateSource(str, Enum):
    """Where a template was discovered."""

    WORKSPACE = "workspace"
    BUNDLED = "bundled"
    OVERRIDE = "override"


def bundled_templates_dir() -> Path:
    """Return the templates directory shipped inside the installed package."""

    return Path(__file__).resolve().parent / "templates"


def bundled_example_path() -> Path:
    """Return the example resume JSON shipped inside the installed package."""

    return Path(__file__).resolve().parent / "examples" / "example.json"


def workspace_state_dir() -> Path:
    """Return ``./.cvclaw/`` relative to CWD (reserved workspace namespace)."""

    return Path.cwd() / ".cvclaw"


def workspace_templates_dir() -> Path:
    """Return ``./.cvclaw/templates/`` relative to CWD (may not exist)."""

    return workspace_state_dir() / "templates"


def default_template_roots() -> list[Path]:
    """Return search roots in priority order (workspace first, bundled last)."""

    roots: list[Path] = []
    ws = workspace_templates_dir()
    if ws.is_dir():
        roots.append(ws)
    bundled = bundled_templates_dir()
    if bundled.is_dir():
        roots.append(bundled)
    return roots


def _resolve_roots(templates_dir: Path | None) -> list[Path]:
    """Return roots for discovery / loading.

    When ``templates_dir`` is given it is the only root (single-root override).
    Otherwise return the default two-root list.
    """

    if templates_dir is not None:
        return [templates_dir]
    return default_template_roots()


@dataclass(frozen=True)
class Template:
    """A discovered template on disk."""

    name: str
    root: Path
    source: TemplateSource = TemplateSource.BUNDLED

    @property
    def entry(self) -> Path:
        return self.root / f"{self.name}.html.j2"

    @property
    def css(self) -> Path | None:
        path = self.root / f"{self.name}.css"
        return path if path.exists() else None


class TemplateNotFoundError(LookupError):
    """Raised when a requested template name does not exist."""


def _source_for_root(root: Path, override: bool) -> TemplateSource:
    if override:
        return TemplateSource.OVERRIDE
    if root == workspace_templates_dir():
        return TemplateSource.WORKSPACE
    return TemplateSource.BUNDLED


def discover_templates(templates_dir: Path | None = None) -> dict[str, Template]:
    """Return a mapping of template name to :class:`Template`.

    Iterates the configured roots in priority order. Skips entries that begin
    with ``_`` (reserved for shared partials) and any directory missing a
    matching ``<name>.html.j2`` file. First write wins — so a workspace
    template shadows a bundled one of the same name.
    """

    roots = _resolve_roots(templates_dir)
    override = templates_dir is not None

    templates: dict[str, Template] = {}
    for root in roots:
        if not root.is_dir():
            continue
        source = _source_for_root(root, override)
        for child in sorted(root.iterdir()):
            if not child.is_dir() or child.name.startswith("_"):
                continue
            if child.name in templates:
                continue  # earlier root already provided this name
            candidate = Template(name=child.name, root=child, source=source)
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


class TemplateAlreadyEjectedError(FileExistsError):
    """Raised when ejecting would overwrite an existing workspace copy."""


@dataclass(frozen=True)
class EjectResult:
    """Outcome of an :func:`eject_template` call."""

    name: str
    source: Path
    destination: Path


def eject_template(
    name: str,
    *,
    from_root: Path | None = None,
    to_root: Path | None = None,
    force: bool = False,
) -> EjectResult:
    """Copy a template directory into the workspace so it can be edited.

    Parameters
    ----------
    name:
        Template name (the directory name; e.g. ``classic``).
    from_root:
        Optional source root. When ``None``, use normal discovery and prefer
        whichever root provides the template — typically bundled.
    to_root:
        Destination templates root. Defaults to ``./.cvclaw/templates/``.
    force:
        Overwrite an existing destination directory. Without this, the call
        raises :class:`TemplateAlreadyEjectedError` if the destination exists.

    Returns
    -------
    EjectResult
        Records the source and destination paths used.
    """

    # Eject inverts normal discovery priority: we want the *bundled* source
    # by default, since the user is asking for a fresh workspace copy. Only
    # honor an explicit --from override.
    if from_root is not None:
        template = get_template(name, from_root)
    else:
        template = _bundled_template(name)

    dest_root = to_root if to_root is not None else workspace_templates_dir()
    dest = dest_root / name

    if dest.exists():
        if not force:
            raise TemplateAlreadyEjectedError(
                f"Workspace already has {name!r} at {_display(dest)}. "
                "Pass --force to overwrite."
            )
        shutil.rmtree(dest)

    dest_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template.root, dest)
    return EjectResult(name=name, source=template.root, destination=dest)


def _bundled_template(name: str) -> Template:
    """Resolve a template against the bundled root only.

    Used by :func:`eject_template` so that the source is always the
    bundled version, even when a workspace copy already exists.
    """

    return get_template(name, bundled_templates_dir())


def _display(path: Path) -> str:
    """Best-effort short path for user-facing messages."""

    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path.resolve())


def build_environment(templates_dir: Path | None = None) -> Environment:
    """Build a Jinja2 environment rooted at the configured template roots.

    The loader is given the full list of roots (workspace + bundled, or the
    single override root). Jinja's ``FileSystemLoader`` searches them in
    order, so ``{% import "classic/_macros.html.j2" %}`` resolves to whichever
    root has the file first — preserving cross-template imports and shared
    ``_partials/`` lookups across the two roots.
    """

    roots = _resolve_roots(templates_dir)
    env = Environment(
        loader=FileSystemLoader([str(p) for p in roots]),
        autoescape=select_autoescape(("html", "j2", "html.j2")),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    return env
