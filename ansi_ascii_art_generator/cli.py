import colorama

colorama.init()  # Initialize Colorama to enable ANSI escape sequence handling

import argparse
import os
from .core import AsciiArtGenerator
from .utils import image_to_html, calculate_best_width, save_as_ansi_text
from .characters import CharacterSet


def main():
    parser = argparse.ArgumentParser(description="Advanced ASCII Art Generator")
    
    # Input/output options
    parser.add_argument("image_path", help="Path to input image")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("-w", "--width", type=int, default=100, help="Output width")
    
    # Character set options
    parser.add_argument(
        "-p",
        "--preset",
        choices=CharacterSet.get_preset_names(),
        default="classic",
        help="Character set preset",
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
        help="Color mode (braille produces Unicode Braille art)",
    )
    
    # Image processing options
    parser.add_argument("-d", "--dither", action="store_true", help="Enable dithering")
    parser.add_argument(
        "-e", "--edges", action="store_true", help="Enable edge detection"
    )
    parser.add_argument(
        "--edge-threshold",
        type=int,
        default=75,
        help="Edge detection threshold (0-255)"
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
        help="Apply blur to image (0.0-10.0)",
    )
    parser.add_argument(
        "--sharpen",
        type=float,
        default=0,
        help="Apply sharpening to image (0.0-10.0)",
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

    # Parse arguments
    args = parser.parse_args()

    # Validate input file
    if not os.path.isfile(args.image_path):
        print(f"Error: File '{args.image_path}' not found.")
        return 1

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
    
    # Initialize generator with all options
    generator = AsciiArtGenerator(
        args.image_path,
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
    )
    
    # If custom character set was specified, use it
    if character_set:
        generator.characters = character_set

    # Generate ASCII art
    ascii_art = generator.generate_ascii()

    # Output handling
    if args.output:
        output_ext = os.path.splitext(args.output)[1].lower()
        
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
    else:
        # Print to console
        print(ascii_art)

    return 0


if __name__ == "__main__":
    main()
