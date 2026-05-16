"""cv-claw: render resume JSON to print-ready HTML."""

from importlib.metadata import PackageNotFoundError, version

from cvclaw.render import render_resume
from cvclaw.schema import Resume

__all__ = ["Resume", "render_resume", "__version__"]

try:
    __version__ = version("cv-claw")
except PackageNotFoundError:
    # Running from a source tree without the package installed.
    __version__ = "0.0.0+unknown"
