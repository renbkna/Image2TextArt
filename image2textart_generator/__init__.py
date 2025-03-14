"""
ASCII Art Generator package

Exports:
- AsciiArtGenerator: Main conversion class
- run_cli: Command-line interface entry point
- run_gui: Graphical interface entry point
- CharacterSet: Character set management
- ColorMapper: Color mapping utilities
"""

__version__ = "1.0.0"
__all__ = ["AsciiArtGenerator", "run_cli", "run_gui", "CharacterSet", "ColorMapper"]

from .core import AsciiArtGenerator
from .cli import main as run_cli
from .gui import run_gui
from .characters import CharacterSet
from ._colormap import ColorMapper
