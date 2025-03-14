"""
Optimized color mapping utilities for ANSI color code generation.

This module provides efficient color mapping functionality for converting
RGB colors to ANSI 256-color and truecolor codes. It includes caching for
improved performance.
"""

class ColorMapper:
    """
    Efficient color mapping for ANSI terminal colors with built-in caching.
    """
    
    # Cache for ANSI 256-color lookups
    _color_cache = {}
    
    # Basic ANSI 16 color palette
    ANSI_BASIC = [
        (0, 0, 0),      # 0: Black
        (128, 0, 0),    # 1: Red
        (0, 128, 0),    # 2: Green
        (128, 128, 0),  # 3: Yellow
        (0, 0, 128),    # 4: Blue
        (128, 0, 128),  # 5: Magenta
        (0, 128, 128),  # 6: Cyan
        (192, 192, 192),# 7: White
        (128, 128, 128),# 8: Bright Black (Gray)
        (255, 0, 0),    # 9: Bright Red
        (0, 255, 0),    # 10: Bright Green
        (255, 255, 0),  # 11: Bright Yellow
        (0, 0, 255),    # 12: Bright Blue
        (255, 0, 255),  # 13: Bright Magenta
        (0, 255, 255),  # 14: Bright Cyan
        (255, 255, 255) # 15: Bright White
    ]
    
    @classmethod
    def rgb_to_ansi_code(cls, r, g, b):
        """
        Convert RGB color to the closest ANSI 256-color code with caching.
        
        Args:
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
            
        Returns:
            int: The closest ANSI 256-color code (0-255)
        """
        # Ensure inputs are integers in valid range
        r = max(0, min(255, int(r)))
        g = max(0, min(255, int(g)))
        b = max(0, min(255, int(b)))
        
        # Check cache first
        cache_key = (r, g, b)
        if cache_key in cls._color_cache:
            return cls._color_cache[cache_key]
        
        # Grayscale check
        if r == g == b:
            # For grayscale values:
            if r < 8:
                code = 16  # Black
            elif r > 238:
                code = 231  # White
            else:
                # Grayscale ramp (24 levels from index 232-255)
                code = 232 + min(23, ((r - 8) // 10))
        else:
            # For color values, use the 6x6x6 color cube (indices 16-231)
            r_idx = min(5, r * 6 // 256)
            g_idx = min(5, g * 6 // 256)
            b_idx = min(5, b * 6 // 256)
            code = 16 + 36 * r_idx + 6 * g_idx + b_idx
        
        # Cache the result
        cls._color_cache[cache_key] = code
        return code
    
    @staticmethod
    def get_ansi_truecolor(r, g, b):
        """
        Get ANSI truecolor escape sequence for the given RGB values.
        
        Args:
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
            
        Returns:
            str: ANSI escape sequence for the specified RGB color
        """
        return f"\033[38;2;{r};{g};{b}m"
    
    @classmethod
    def get_ansi_256_code(cls, r, g, b):
        """
        Get ANSI 256-color escape sequence for the given RGB values.
        
        Args:
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
            
        Returns:
            str: ANSI escape sequence for the closest 256-color
        """
        code = cls.rgb_to_ansi_code(r, g, b)
        return f"\033[38;5;{code}m"
