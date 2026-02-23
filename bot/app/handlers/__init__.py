"""Bot handlers package."""

from .start import router as start_router
from .errors import router as errors_router

__all__ = ["start_router", "errors_router"]
