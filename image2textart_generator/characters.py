"""
Character set presets and management for ASCII art generation
"""

from typing import Dict, List


class CharacterSet:
    """
    Manages character sets for different ASCII art styles.
    """

    PRESETS: Dict[str, str] = {
        # Block characters (sorted from light to dark)
        "block": " ░▒▓█▄▀",
        
        # Dense gradient (sorted for smooth transitions)
        "dense": " .,:;+~=^*#%@$",
        
        # Line art characters (complete set for detailed line drawings)
        "lineart": "║╗╝╔╩╦╠═╬╧╨╤╥╙╘╒╓╫╪┘┌┐└├┤┬┴┼",
        
        # Classic ASCII gradient (traditional ASCII art)
        "classic": " .:-=+*#%@",
        
        # Unicode blocks (extensive set for detailed shading)
        "unicode": " ▁▂▃▄▅▆▇█▖▗▘▙▚▛▜▝▞▟",
        
        # Highly detailed character set (sorted by visual density)
        "detailed": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
        
        # Binary (for high contrast images)
        "binary": "01",
        
        # Minimal gradient (for clean, simple output)
        "minimal": " .:-=+*#%@",
        
        # Circle-based characters (great for organic shapes)
        "circles": " .°ᵒO@",
        
        # Pure shading blocks (consistent gradient)
        "shading": " ░▒▓█",
        
        # Geometric shapes (for abstract patterns)
        "geometric": " ▢▣▤▥▦▧▨▩■□◊○●◐◑◒◓◔◕◖◗",
        
        # Braille dots patterns (alternative to braille mode)
        "dots": " ⠀⠁⠂⠃⠄⠅⠆⠇⠈⠉⠊⠋⠌⠍⠎⠏⠐⠑⠒⠓⠔⠕⠖⠗⠘⠙⠚⠛⠜⠝⠞⠟",
        
        # High contrast (just space and full block - dramatic)
        "contrast": " █",
        
        # Enhanced gradient (optimized for photographic detail)
        "photo": " .,:;'\"^=+*#%&@$",
        
        # Pixel art style (good for retro-looking output)
        "pixel": " ▖▗▘▙▚▛▜▝▞▟■",
        
        # Ultra-detailed (combines multiple strategies for max detail)
        "ultra": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/#%@&$",
    }

    # Character density (darkness) lookup for brightness mapping
    # Maps characters to their approximate visual density (0.0-1.0)
    DENSITY_MAP = {
        # Space is 0.0, full block is 1.0
        ' ': 0.0, '.': 0.1, '`': 0.1, "'": 0.1, ',': 0.15, ':': 0.2, ';': 0.25,
        'i': 0.3, '!': 0.3, 'l': 0.3, 'I': 0.35, '^': 0.3, '"': 0.3, 
        '-': 0.3, '+': 0.4, '_': 0.4, '?': 0.45, ']': 0.5, '[': 0.5, 
        '{': 0.5, '}': 0.5, '(': 0.5, ')': 0.5, '\\': 0.5, '/': 0.5, 
        't': 0.5, 'f': 0.55, 'j': 0.55, 'r': 0.55, 'x': 0.6, 'n': 0.6, 
        'u': 0.6, 'v': 0.6, 'c': 0.6, 'z': 0.65, 'X': 0.7, 'Y': 0.7, 
        'U': 0.7, 'J': 0.7, 'C': 0.7, 'L': 0.75, 'Q': 0.8, '0': 0.8, 
        'O': 0.8, 'Z': 0.8, 'm': 0.85, 'w': 0.85, 'q': 0.85, 'p': 0.85, 
        'd': 0.85, 'b': 0.85, 'k': 0.85, 'h': 0.85, 'a': 0.85, 'o': 0.85, 
        '*': 0.85, '#': 0.9, 'M': 0.95, 'W': 0.95, '&': 0.95, '8': 0.95, 
        '%': 0.95, 'B': 0.95, '@': 0.97, '$': 1.0,
        
        # Unicode block characters
        '░': 0.25, '▒': 0.5, '▓': 0.75, '█': 1.0,
        
        # Partial block characters
        '▁': 0.125, '▂': 0.25, '▃': 0.375, '▄': 0.5,
        '▅': 0.625, '▆': 0.75, '▇': 0.875,
        '▖': 0.25, '▗': 0.25, '▘': 0.25, '▙': 0.75,
        '▚': 0.5, '▛': 0.75, '▜': 0.75, '▝': 0.25,
        '▞': 0.5, '▟': 0.75,
        
        # Box drawing characters
        '─': 0.3, '│': 0.3, '┌': 0.3, '┐': 0.3, '└': 0.3, '┘': 0.3,
        '├': 0.4, '┤': 0.4, '┬': 0.4, '┴': 0.4, '┼': 0.5,
        '═': 0.4, '║': 0.4, '╒': 0.4, '╓': 0.4, '╔': 0.4, '╕': 0.4,
        '╖': 0.4, '╗': 0.4, '╘': 0.4, '╙': 0.4, '╚': 0.4, '╛': 0.4,
        '╜': 0.4, '╝': 0.4, '╞': 0.5, '╟': 0.5, '╠': 0.5, '╡': 0.5,
        '╢': 0.5, '╣': 0.5, '╤': 0.5, '╥': 0.5, '╦': 0.5, '╧': 0.5,
        '╨': 0.5, '╩': 0.5, '╪': 0.6, '╫': 0.6, '╬': 0.6,
        
        # Circle characters
        '°': 0.2, 'ᵒ': 0.3, 'O': 0.7, '○': 0.6, '●': 0.9,
        '◌': 0.3, '◍': 0.4, '◎': 0.5, '◐': 0.5, '◑': 0.5,
        '◒': 0.5, '◓': 0.5, '◔': 0.3, '◕': 0.7, '◖': 0.5,
        '◗': 0.5, '◦': 0.2,
        
        # Braille patterns (estimated density based on dot count)
        '⠀': 0.0, '⠁': 0.125, '⠂': 0.125, '⠃': 0.25, '⠄': 0.125,
        '⠅': 0.25, '⠆': 0.25, '⠇': 0.375, '⠈': 0.125, '⠉': 0.25,
        '⠊': 0.25, '⠋': 0.375, '⠌': 0.25, '⠍': 0.375, '⠎': 0.375,
        '⠏': 0.5, '⠐': 0.125, '⠑': 0.25, '⠒': 0.25, '⠓': 0.375,
        '⠔': 0.25, '⠕': 0.375, '⠖': 0.375, '⠗': 0.5, '⠘': 0.25,
        '⠙': 0.375, '⠚': 0.375, '⠛': 0.5, '⠜': 0.375, '⠝': 0.5,
        '⠞': 0.5, '⠟': 0.625, '⠠': 0.125, '⠡': 0.25, '⠢': 0.25,
        '⠣': 0.375, '⠤': 0.25, '⠥': 0.375, '⠦': 0.375, '⠧': 0.5,
        '⠨': 0.25, '⠩': 0.375, '⠪': 0.375, '⠫': 0.5, '⠬': 0.375,
        '⠭': 0.5, '⠮': 0.5, '⠯': 0.625, '⠰': 0.25, '⠱': 0.375,
        '⠲': 0.375, '⠳': 0.5, '⠴': 0.375, '⠵': 0.5, '⠶': 0.5,
        '⠷': 0.625, '⠸': 0.375, '⠹': 0.5, '⠺': 0.5, '⠻': 0.625,
        '⠼': 0.5, '⠽': 0.625, '⠾': 0.625, '⠿': 0.75, '⡀': 0.125,
        '⡁': 0.25, '⡂': 0.25, '⡃': 0.375, '⡄': 0.25, '⡅': 0.375,
        '⡆': 0.375, '⡇': 0.5, '⡈': 0.25, '⡉': 0.375, '⡊': 0.375,
        '⡋': 0.5, '⡌': 0.375, '⡍': 0.5, '⡎': 0.5, '⡏': 0.625,
        '⡐': 0.25, '⡑': 0.375, '⡒': 0.375, '⡓': 0.5, '⡔': 0.375,
        '⡕': 0.5, '⡖': 0.5, '⡗': 0.625, '⡘': 0.375, '⡙': 0.5,
        '⡚': 0.5, '⡛': 0.625, '⡜': 0.5, '⡝': 0.625, '⡞': 0.625,
        '⡟': 0.75, '⡠': 0.25, '⡡': 0.375, '⡢': 0.375, '⡣': 0.5,
        '⡤': 0.375, '⡥': 0.5, '⡦': 0.5, '⡧': 0.625, '⡨': 0.375,
        '⡩': 0.5, '⡪': 0.5, '⡫': 0.625, '⡬': 0.5, '⡭': 0.625,
        '⡮': 0.625, '⡯': 0.75, '⡰': 0.375, '⡱': 0.5, '⡲': 0.5,
        '⡳': 0.625, '⡴': 0.5, '⡵': 0.625, '⡶': 0.625, '⡷': 0.75,
        '⡸': 0.5, '⡹': 0.625, '⡺': 0.625, '⡻': 0.75, '⡼': 0.625,
        '⡽': 0.75, '⡾': 0.75, '⡿': 0.875,
        
        # Geometric characters
        '▢': 0.5, '▣': 0.7, '▤': 0.6, '▥': 0.7, '▦': 0.65,
        '▧': 0.7, '▨': 0.75, '▩': 0.8, '■': 1.0, '□': 0.5,
        '◊': 0.5, '◆': 0.8,
    }

    # Class-level cache for character densities
    _density_cache = {}

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
    
    @classmethod
    def get_character_density(cls, char: str) -> float:
        """
        Get the approximate visual density of a character (0.0-1.0).
        Uses an optimized caching mechanism to improve performance.
        """
        # Check class-level cache first
        if char in cls._density_cache:
            return cls._density_cache[char]
            
        # Look up in DENSITY_MAP or use default
        density = cls.DENSITY_MAP.get(char, 0.5)
        
        # Store in cache for future lookups
        cls._density_cache[char] = density
        
        return density
    
    @classmethod
    def sort_by_density(cls, chars: str) -> str:
        """Sort characters by their visual density (dark to light)."""
        return ''.join(sorted(chars, key=lambda c: cls.get_character_density(c)))
    
    @classmethod
    def optimize_character_set(cls, chars: str, target_range: tuple = (0.0, 1.0)) -> str:
        """
        Optimize a character set to ensure even distribution across the target density range.
        
        Args:
            chars: The character string to optimize
            target_range: Tuple of (min_density, max_density) to spread characters across
            
        Returns:
            Optimized character string
        """
        # Get character densities
        char_densities = [(c, cls.get_character_density(c)) for c in chars]
        
        # Sort by density
        char_densities.sort(key=lambda x: x[1])
        
        # Get current range
        min_density = char_densities[0][1]
        max_density = char_densities[-1][1]
        
        # If range is too small, expand it
        if max_density - min_density < 0.1:
            # Add space and full block if not present
            if ' ' not in chars:
                char_densities = [(' ', 0.0)] + char_densities
            if '█' not in chars:
                char_densities.append(('█', 1.0))
                
            # Resort
            char_densities.sort(key=lambda x: x[1])
            min_density = char_densities[0][1]
            max_density = char_densities[-1][1]
        
        # Create mapping from current range to target range
        target_min, target_max = target_range
        
        # Remap densities
        if max_density > min_density:  # Avoid division by zero
            remapped = []
            for char, density in char_densities:
                normalized = (density - min_density) / (max_density - min_density)
                new_density = target_min + normalized * (target_max - target_min)
                remapped.append((char, new_density))
            
            # Sort by remapped density
            remapped.sort(key=lambda x: x[1])
            
            return ''.join(c for c, _ in remapped)
        else:
            # If all characters have same density, just return as is
            return chars
