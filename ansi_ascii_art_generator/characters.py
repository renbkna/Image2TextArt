"""
Character set presets and management for ASCII art generation
"""

from typing import Dict, List


class CharacterSet:
    """
    Manages character sets for different ASCII art styles.
    """

    PRESETS: Dict[str, str] = {
        "block": " ░▒▓▄▀█",
        "dense": "@%#*+=-:. ",
        "lineart": "║╗╝╔╩╦╠═╬╧╨╤╥╙╘╒╓╫╪┘┌",
        "classic": " .:-=+*#%@",
        "unicode": " ▖▘▝▗▚▞▌▀█",
        "detailed": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
        "binary": "01",
    }

    @classmethod
    def get_preset_names(cls) -> List[str]:
        """Get available preset names."""
        return list(cls.PRESETS.keys())

    @classmethod
    def get_preset(cls, name: str) -> str:
        """Get a specific preset character set."""
        if name not in cls.PRESETS:
            raise ValueError(
                f"Invalid preset name. Available presets: {', '.join(cls.PRESETS.keys())}"
            )
        return cls.PRESETS[name]

    @staticmethod
    def validate_characters(chars: str) -> None:
        """Validate a custom character set."""
        if len(chars) < 2:
            raise ValueError("Character set must contain at least 2 characters")
        if len(set(chars)) != len(chars):
            raise ValueError("Character set contains duplicate characters")

    @classmethod
    def create_custom_set(cls, chars: str) -> str:
        """Create and validate a custom character set."""
        cls.validate_characters(chars)
        return chars
