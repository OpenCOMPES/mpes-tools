"""mpes-tools module easy access APIs."""
import importlib.metadata

from .show_4d_window import show_4d_window

__version__ = importlib.metadata.version("mpes-tools")
__all__ = ["show_4d_window"]