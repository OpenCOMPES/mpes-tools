"""mpes-tools module easy access APIs."""
import importlib.metadata

from .Arpes_gui import MainWindow

__version__ = importlib.metadata.version("mpes-tools")
__all__ = ["MainWindow"]