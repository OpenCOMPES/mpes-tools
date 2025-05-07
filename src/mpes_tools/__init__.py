"""mpes-tools module easy access APIs."""
import importlib.metadata

from mpes_tools.show_4d_window import MainWindow

__version__ = importlib.metadata.version("mpes-tools")
__all__ = ["MainWindow"]