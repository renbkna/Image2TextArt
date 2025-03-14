import colorama
colorama.init()  # Initialize Colorama to enable ANSI escape sequence handling

import argparse
import os
import sys
import json

# Handle both package and standalone imports
try:
    from .core import AsciiArtGenerator
    from .utils import (
        image_to_html, 
        calculate_best_width, 
        save_as_ansi_text, 
        handle_large_image,
        suggest_optimal_settings
    )
    from .characters import CharacterSet
except ImportError:
    # If running as a standalone script, adjust the path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    # Now try again with absolute imports
    try:
        from image2textart_generator.core import AsciiArtGenerator
        from image2textart_generator.utils import (
            image_to_html, 
            calculate_best_width, 
            save_as_ansi_text,
            handle_large_image,
            suggest_optimal_settings
        )
        from image2textart_generator.characters import CharacterSet
    except ImportError as e:
        print(f"Error importing modules: {e}")
        print(f"Python path: {sys.path}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Advanced ASCII Art Generator")
    
    # Input/output options
    parser.add_argument("image_path", help="Path to input image")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("-w", "--width", type=int, default=100, help="Output width (default: 100)")
    
    # Character set options
    parser.add_argument(
        "-p",
        "--preset",
        choices=CharacterSet.get_preset_names(),
        default="classic",
        help="Character set preset (default: classic)",
    )
    parser.add_argument(
        "--custom-chars",
        help="Custom character set (overrides preset)",
    )
    
    # Color & render mode options
    parser.add_argument(
        "-c",
        "--color",
        choices=["grayscale", "ansi", "truecolor", "html", "braille"],
        default="braille",
        help="Color mode (default: braille)",
    )
    
    # Image processing options
    parser.add_argument(
        "-d", "--dither", 
        action="store_true", 
        help="Enable dithering"
    )
    parser.add_argument(
        "-e", "--edges", 
        action="store_true", 
        help="Enable edge detection"
    )
    parser.add_argument(
        "--edge-threshold",
        type=int,
        default=75,
        help="Edge detection threshold (0-255, default: 75)"
    )
    parser.add_argument(
        "--no-enhance",
        action="store_false",
        dest="enhance",
        help="Disable auto contrast enhancement",
    )
    parser.add_argument(
        "--invert",
        action="store_true",
        help="Invert image colors",
    )
    parser.add_argument(
        "--aspect-ratio",
        type=float,
        default=0.55,
        help="Aspect ratio correction factor (default: 0.55)",
    )
    parser.add_argument(
        "--blur",
        type=float,
        default=0,
        help="Apply blur to image (0.0-10.0, default: 0)",
    )
    parser.add_argument(
        "--sharpen",
        type=float,
        default=0,
        help="Apply sharpening to image (0.0-10.0, default: 0)",
    )
    parser.add_argument(
        "--brightness",
        type=float,
        default=1.0,
        help="Adjust brightness (0.5-2.0, default: 1.0)",
    )
    parser.add_argument(
        "--saturation",
        type=float,
        default=1.0,
        help="Adjust saturation (0.0-2.0, default: 1.0)",
    )
    
    # Additional parameters for the GUI
    parser.add_argument(
        "--contrast",
        type=float,
        default=1.0,
        help="Adjust contrast (0.5-2.0, default: 1.0)",
    )
    parser.add_argument(
        "--detail-level",
        type=float,
        default=1.0,
        help="Adjust detail level (0.1-2.0, default: 1.0)",
    )
    parser.add_argument(
        "--gamma",
        type=float,
        default=1.0,
        help="Adjust gamma correction (0.5-2.0, default: 1.0)",
    )
    
    # Output formatting options
    parser.add_argument(
        "--html-font-size",
        type=int,
        default=8,
        help="Font size for HTML output (default: 8pt)",
    )
    parser.add_argument(
        "--html-font-family",
        default="monospace",
        help="Font family for HTML output (default: monospace)",
    )
    parser.add_argument(
        "--html-bg-color",
        default="#000000",
        help="Background color for HTML output (default: #000000)",
    )

    # Performance options
    parser.add_argument(
        "--optimize-for",
        choices=["quality", "speed", "memory"],
        default="quality",
        help="Optimization preference (default: quality)",
    )
    parser.add_argument(
        "--max-image-size",
        type=int,
        default=3000,
        help="Maximum image dimension before downscaling (default: 3000)",
    )
    
    # Special features
    parser.add_argument(
        "--auto-settings",
        action="store_true",
        help="Automatically determine optimal settings based on image content",
    )
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="List available character presets and exit",
    )

    # Parse arguments
    args = parser.parse_args()
    
    # Handle list-presets command
    if args.list_presets:
        print(json.dumps(CharacterSet.get_preset_names()))
        return 0

    # Validate input file
    if not os.path.isfile(args.image_path):
        print(f"Error: File '{args.image_path}' not found.")
        return 1

    # Auto-detect optimal settings if requested
    if args.auto_settings:
        optimal_settings = suggest_optimal_settings(args.image_path, args.width)
        
        # Update arguments with suggested settings
        args.width = optimal_settings["output_width"]
        args.color = optimal_settings["color_mode"]
        args.dither = optimal_settings["dithering"]
        args.edges = optimal_settings["edge_detect"]
        args.preset = optimal_settings["preset"]
        args.enhance = optimal_settings["enhance_contrast"]
        args.aspect_ratio = optimal_settings["aspect_ratio_correction"]
        args.invert = optimal_settings["invert"]
        args.edge_threshold = optimal_settings["edge_threshold"]
        
        print("Using auto-detected optimal settings:")
        print(f"  - Width: {args.width}")
        print(f"  - Color mode: {args.color}")
        print(f"  - Character preset: {args.preset}")
        print(f"  - Dithering: {'enabled' if args.dither else 'disabled'}")
        print(f"  - Edge detection: {'enabled' if args.edges else 'disabled'}")
        
    # Calculate optimal width
    best_width = calculate_best_width(args.image_path, args.width)
    
    # Get character set
    character_set = None
    if args.custom_chars:
        try:
            character_set = CharacterSet.create_custom_set(args.custom_chars)
        except ValueError as e:
            print(f"Error with custom character set: {e}")
            return 1
    
    # Handle large images if needed
    if args.optimize_for == "memory":
        try:
            # Use a lower threshold for memory optimization
            image = handle_large_image(args.image_path, args.max_image_size, best_width)
        except Exception as e:
            print(f"Error handling large image: {e}")
            return 1
    else:
        try:
            # Open image normally
            image = handle_large_image(args.image_path, args.max_image_size, best_width)
        except Exception as e:
            print(f"Error opening image: {e}")
            return 1
    
    try:
        # Initialize generator with all options
        generator = AsciiArtGenerator(
            image,  # Pass the already opened image
            output_width=best_width,
            color_mode=args.color,
            dithering=args.dither,
            edge_detect=args.edges,
            preset=args.preset,
            enhance_contrast=args.enhance,
            aspect_ratio_correction=args.aspect_ratio,
            invert=args.invert,
            edge_threshold=args.edge_threshold,
            blur=args.blur,
            sharpen=args.sharpen,
            brightness=args.brightness,
            saturation=args.saturation,
            contrast=args.contrast,
            detail_level=args.detail_level,
            gamma=args.gamma,
        )
        
        # If custom character set was specified, use it
        if character_set:
            generator.characters = character_set

        # Generate ASCII art
        ascii_art = generator.generate_ascii()

    except Exception as e:
        print(f"Error generating ASCII art: {e}")
        return 1
    
    # Output handling
    if args.output:
        try:
            output_ext = os.path.splitext(args.output)[1].lower()
            
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(args.output)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # HTML output
            if args.color == "html" or output_ext == ".html":
                image_to_html(
                    ascii_art, 
                    args.image_path, 
                    args.output,
                    font_size=args.html_font_size,
                    font_family=args.html_font_family,
                    background_color=args.html_bg_color,
                )
            else:
                # Plain text or ANSI text output
                if args.color in ["ansi", "truecolor"]:
                    save_as_ansi_text(ascii_art, args.output)
                else:
                    with open(args.output, "w", encoding="utf-8") as f:
                        f.write(ascii_art)
            print(f"Saved to {args.output}")
        except Exception as e:
            print(f"Error saving output: {e}")
            return 1
    else:
        # Print to console
        try:
            print(ascii_art)
        except UnicodeEncodeError:
            # Fallback for consoles that can't handle Unicode
            print("Output contains characters that can't be displayed in this console.")
            print("Try using --output to save to a file instead.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
