"""
ASCII Art Generator package

Exports:
- AsciiArtGenerator: Main conversion class
- run_cli: Command-line interface entry point
- run_gui: Graphical interface entry point
- CharacterSet: Character set management
"""

__version__ = "1.3.0"
__all__ = ["AsciiArtGenerator", "run_cli", "run_gui", "CharacterSet"]

from .core import AsciiArtGenerator
from .cli import main as run_cli
from .gui import run_gui
from .characters import CharacterSet
