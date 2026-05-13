"""cv-claw: render resume JSON to print-ready HTML."""

from cvclaw.render import render_resume
from cvclaw.schema import Resume

__all__ = ["Resume", "render_resume", "__version__"]
__version__ = "0.1.0"
